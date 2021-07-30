import requests


FTS_CONFIG = {}

FOREIGN_KEYS = (
    ("jobs", "project_id", "projects", "id"),
)

VIEWS = {}


def make_session(token):
    session = requests.Session()
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


def save_project(db, project):
    # TODO: Make an issue: ideally this would be an upsert
    unique_columns = ["vcs_type", "username", "reponame"]
    # Delete existing project
    existing = list(
        db["projects"].rows_where(
            "vcs_type = ? and username = ? and reponame = ?",
            [project["vcs_type"], project["username"], project["reponame"]],
        ),
    )
    if existing:
        project_id = existing[0]["id"]
        to_update = {
            key: value
            for key, value in project.items()
            if key not in unique_columns
        }
        db["projects"].update(project_id, to_update)
    else:
        to_save = {
            key: value
            for key, value in project.items()
            if key in ("vcs_type", "username", "reponame", "vcs_url", "default_branch")
        }
        project_id = db["projects"].insert(to_save, pk="id", alter=True).last_pk
    db["projects"].create_index(
        unique_columns, unique=True, if_not_exists=True
    )
    return project_id


def save_projects(db, projects):
    for project in projects:
        save_project(db, project)


def save_jobs(db, jobs):
    # Each job contains its project's columns. Create a project using the first job.
    project_id = save_project(db, jobs[0])

    for original in jobs:
        # Delete existing job
        existing = list(
            db["jobs"].rows_where(
                "project_id = ? and build_num = ?",
                [project_id, original["build_num"]],
            ),
        )
        if existing:
            existing_id = existing[0]["id"]
            db["jobs"].delete_where("id = ?", [existing_id])
        to_save = {
            key: value
            for key, value in original.items()
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
        to_save["user_id"] = original["user"]["id"]
        to_save["user_name"] = original["user"]["login"]
        to_save.update(original["workflows"])
        to_save.pop("upstream_job_ids", None)
        to_save.pop("upstream_concurrency_map", None)
        to_save["project_id"] = project_id
        db["jobs"].insert(
            to_save,
            pk="id",
            alter=True,
            foreign_keys=[("project_id", "projects")],
        )
        db["jobs"].create_index(
            ["project_id", "build_num"], unique=True, if_not_exists=True
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
