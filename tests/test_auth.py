import json
import os
import pathlib
import pytest
from click.testing import CliRunner
from circleci_to_sqlite.cli import cli


@pytest.fixture
def mocked_projects(requests_mock):
    return requests_mock.get(
        "https://circleci.com/api/v1.1/projects",
        json=json.load(open(pathlib.Path(__file__).parent / "projects.json")),
    )


def test_auth():
    runner = CliRunner()
    with runner.isolated_filesystem():
        assert [] == os.listdir(".")
        result = runner.invoke(cli, ["auth"], input="zzz")
        assert 0 == result.exit_code
        assert ["auth.json"] == os.listdir(".")
        assert {"circleci_personal_token": "zzz"} == json.load(open("auth.json"))


def test_auth_file(mocked_projects):
    runner = CliRunner()
    with runner.isolated_filesystem():
        open("auth.json", "w").write(json.dumps({"circleci_personal_token": "xxx"}))
        result = runner.invoke(cli, ["projects", "projects.db"], catch_exceptions=False)
        assert 0 == result.exit_code
        assert mocked_projects.called
        assert "Basic eHh4Og==" == mocked_projects.last_request.headers["Authorization"]


def test_auth_environment_variable(mocked_projects, monkeypatch):
    monkeypatch.setenv("CIRCLECI_TOKEN", "xyz")
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["projects", "projects.db"], catch_exceptions=False)
        assert 0 == result.exit_code
        assert mocked_projects.called
        assert "Basic eHl6Og==" == mocked_projects.last_request.headers["Authorization"]
