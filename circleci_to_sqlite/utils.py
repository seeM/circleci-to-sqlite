import requests


FTS_CONFIG = {}

FOREIGN_KEYS = ()

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


def save_projects(db, projects):
    for original in projects:
        columns = ["vcs_type", "username", "reponame", "vcs_url", "default_branch"]
        project = {c: original[c] for c in columns}
        # Delete existing project
        existing = list(
            db["projects"].rows_where(
                "vcs_type = ? and username = ? and reponame = ?",
                [project["vcs_type"], project["username"], project["reponame"]],
            ),
        )
        if existing:
            existing_id = existing[0]["id"]
            db["projects"].delete_where("id = ?", [existing_id])
        db["projects"].insert(
            project,
            pk="id",
            alter=True,
            column_order=["id", *columns],
        )
        db["projects"].create_index(
            ["vcs_type", "username", "reponame"], unique=True, if_not_exists=True
        )


def ensure_foreign_keys(db):
    for expected_foreign_key in FOREIGN_KEYS:
        table, column, table2, column2 = expected_foreign_key
        if (
            expected_foreign_key not in db[table].foreign_keys
            and
            # Ensure all tables and columns exist
            db[table].exists()
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
