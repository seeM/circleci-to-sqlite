from click.testing import CliRunner
import json
import pathlib
import sqlite_utils
from circleci_to_sqlite.cli import cli


def test_projects(requests_mock):
    requests_mock.get(
        "https://circleci.com/api/v1.1/projects",
        json=json.load(open(pathlib.Path(__file__).parent / "projects.json")),
    )
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["projects", "projects.db"])
        assert 0 == result.exit_code
        db = sqlite_utils.Database("projects.db")
        assert {"projects"}.issubset(set(db.table_names()))
        assert set() == set(db["projects"].foreign_keys)
        assert {
            (1, ("vcs_type", "username", "reponame")),
        } == {(i.unique, tuple(i.columns)) for i in db["projects"].indexes}
        project_rows = list(db["projects"].rows)
        assert [
            {
                "id": 1,
                "vcs_type": "github",
                "username": "seeM",
                "reponame": "circleci-to-sqlite",
                "vcs_url": "https://github.com/seeM/circleci-to-sqlite",
                "default_branch": "main",
            }
        ] == project_rows
