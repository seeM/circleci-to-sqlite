import requests


FTS_CONFIG = {}

FOREIGN_KEYS = (
    ("jobs", "project_id", "projects", "id"),
    ("steps", "job_id", "jobs", "id"),
    ("actions", "step_id", "steps", "id"),
)

VIEWS = {}


def make_session(token):
    session = requests.Session()
    if token is not None:
        session.auth = requests.auth.HTTPBasicAuth(token, "")
    session.headers.update({"Accept": "application/json"})
    return session


def fetch_projects(token):
    session = make_session(token)
    response = session.get("https://circleci.com/api/v1.1/projects")
    response.raise_for_status()
    return response.json()


def fetch_jobs(project_slug, token):
    session = make_session(token)
    vcs_type, user, repo = project_slug.split("/")
    url = f"https://circleci.com/api/v1.1/project/{vcs_type}/{user}/{repo}"
    response = session.get(url)
    response.raise_for_status()
    return response.json()


def fetch_steps(project_slug, build_num, token):
    session = make_session(token)
    vcs_type, user, repo = project_slug.split("/")
    url = f"https://circleci.com/api/v1.1/project/{vcs_type}/{user}/{repo}/{build_num}"
    response = session.get(url)
    response.raise_for_status()
    return response.json()


def save_project(db, project):
    to_save = {
        key: value
        for key, value in project.items()
        if key in ("vcs_type", "username", "reponame", "vcs_url", "default_branch")
    }

    # TODO: Make an issue: ideally this would be an upsert
    existing = list(
        db["projects"].rows_where(
            "vcs_type = ? and username = ? and reponame = ?",
            [project["vcs_type"], project["username"], project["reponame"]],
        ),
    )
    if existing:
        project_id = existing[0]["id"]
        db["projects"].update(project_id, to_save).last_pk
    else:
        project_id = db["projects"].insert(to_save, pk="id", alter=True).last_pk

    db["projects"].create_index(
        ["vcs_type", "username", "reponame"], unique=True, if_not_exists=True
    )
    return project_id


def save_projects(db, projects):
    for project in projects:
        save_project(db, project)


def save_job(db, job):
    # Each job contains its project's columns. Create a project using the first job.
    project_id = save_project(db, job)

    to_save = {
        key: value
        for key, value in job.items()
        if key
        in (
            "build_num",
            "build_url",
            "branch",
            "parallel",
            "usage_queued_at",
            "queued_at",
            "start_time",
            "stop_time",
            "status",
            "failed",
            "canceled",
        )
    }
    to_save["user_id"] = job["user"].get("id")
    to_save["user_name"] = job["user"]["login"]
    to_save.update(job["workflows"])
    to_save.pop("upstream_job_ids", None)
    to_save.pop("upstream_concurrency_map", None)
    to_save["project_id"] = project_id

    existing = list(
        db["jobs"].rows_where(
            "project_id = ? and build_num = ?",
            [project_id, job["build_num"]],
        ),
    )
    if existing:
        job_id = existing[0]["id"]
        db["jobs"].update(job_id, to_save).last_pk
    else:
        job_id = (
            db["jobs"]
            .insert(
                to_save,
                pk="id",
                alter=True,
                foreign_keys=[("project_id", "projects")],
            )
            .last_pk
        )

    db["jobs"].create_index(
        ["project_id", "build_num"], unique=True, if_not_exists=True
    )
    return job_id


def save_jobs(db, jobs):
    for job in jobs:
        save_job(db, job)


def save_steps(db, steps):
    # Steps dict contains its job's columns. Create a job using that
    job_id = save_job(db, steps)

    # Delete existing steps and actions
    existing = list(db["steps"].rows_where("job_id = ?", [job_id]))
    if existing:
        db["actions"].delete_where(
            "step_id in (select id from steps where job_id = ?)", [job_id]
        )
        db["steps"].delete_where("job_id = ?", [job_id])

    for step_index, original in enumerate(steps["steps"]):
        step_name = original["name"]
        step_id = (
            db["steps"]
            .insert(
                {
                    "job_id": job_id,
                    "index": step_index,
                    "name": step_name,
                },
                pk="id",
                alter=True,
                foreign_keys=[("job_id", "jobs")],
            )
            .last_pk
        )
        db["steps"].create_index(["job_id", "index"], unique=True, if_not_exists=True)

        for action in original["actions"]:
            db["actions"].insert(
                {"step_id": step_id, **action},
                pk="id",
                alter=True,
                foreign_keys=[("step_id", "steps")],
            )


def ensure_foreign_keys(db):
    for expected_foreign_key in FOREIGN_KEYS:
        table, column, table2, column2 = expected_foreign_key
        if (
            expected_foreign_key not in db[table].foreign_keys
            # Ensure all tables and columns exist
            and db[table].exists()
            and db[table2].exists()
            and column in db[table].columns_dict
            and column2 in db[table2].columns_dict
        ):
            db[table].add_foreign_key(column, table2, column2)


def ensure_db_shape(db):
    "Ensure FTS is configured and expected FKS, views and (soon) indexes are present"
    # Foreign keys:
    ensure_foreign_keys(db)
    db.index_foreign_keys()

    # FTS:
    existing_tables = set(db.table_names())
    for table, columns in FTS_CONFIG.items():
        if "{}_fts".format(table) in existing_tables:
            continue
        if table not in existing_tables:
            continue
        db[table].enable_fts(columns, create_triggers=True)

    # Views:
    existing_tables = set(db.table_names())
    for view, (tables, sql) in VIEWS.items():
        # Do all of the tables exist?
        if not tables.issubset(existing_tables):
            continue
        db.create_view(view, sql, replace=True)
