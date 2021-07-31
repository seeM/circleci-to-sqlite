import click
import json
import os
import pathlib
import sqlite_utils
from . import utils


@click.group()
@click.version_option()
def cli():
    "Save data from CircleCI to a SQLite database"


@cli.command()
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    default="auth.json",
    help="Path to save tokens to, defaults to auth.json",
)
def auth(auth):
    "Save authentication credentials to a JSON file"
    click.echo("Create a CircleCI personal user token and pase it here:")
    click.echo()
    personal_token = click.prompt("Personal token")
    if pathlib.Path(auth).exists():
        auth_data = json.load(open(auth))
    else:
        auth_data = {}
    auth_data["circleci_personal_token"] = personal_token
    open(auth, "w").write(json.dumps(auth_data, indent=4) + "\n")


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=True),
    default="auth.json",
    help="Path to auth.json token file",
)
def projects(db_path, auth):
    "Save all projects for the current user"
    db = sqlite_utils.Database(db_path)
    token = load_token(auth)
    projects = utils.fetch_projects(token)
    utils.save_projects(db, projects)
    utils.ensure_db_shape(db)


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.argument("project_slug")
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=True),
    default="auth.json",
    help="Path to auth.json token file",
)
def jobs(db_path, project_slug, auth):
    "Save all jobs belonging to a project"
    db = sqlite_utils.Database(db_path)
    token = load_token(auth)
    jobs = utils.fetch_jobs(project_slug, token)
    utils.save_jobs(db, jobs)
    utils.ensure_db_shape(db)


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.argument("project_slug")
@click.argument("build_num")
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=True),
    default="auth.json",
    help="Path to auth.json token file",
)
def steps(db_path, project_slug, build_num, auth):
    "Save all steps and their actions belonging to a job"
    db = sqlite_utils.Database(db_path)
    token = load_token(auth)
    steps = utils.fetch_steps(project_slug, build_num, token)
    utils.save_steps(db, steps)
    utils.ensure_db_shape(db)


def load_token(auth):
    try:
        token = json.load(open(auth))["circleci_personal_token"]
    except (KeyError, FileNotFoundError):
        token = None
    if token is None:
        # Fallback to CIRCLECI_TOKEN environment variable
        token = os.environ.get("CIRCLECI_TOKEN") or None
    return token
