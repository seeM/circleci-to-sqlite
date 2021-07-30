from click.testing import CliRunner
import json
import pathlib
import sqlite_utils
from sqlite_utils.db import ForeignKey
from circleci_to_sqlite.cli import cli


def test_jobs(requests_mock):
    requests_mock.get(
        "https://circleci.com/api/v1.1/project/github/seem/circleci-to-sqlite",
        json=json.load(open(pathlib.Path(__file__).parent / "jobs.json")),
    )
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ["jobs", "jobs.db", "github/seem/circleci-to-sqlite"],
            catch_exceptions=False,
        )
        assert 0 == result.exit_code
        db = sqlite_utils.Database("jobs.db")
        assert {"jobs"}.issubset(set(db.table_names()))
        assert {
            ForeignKey(
                table="jobs",
                column="project_id",
                other_table="projects",
                other_column="id",
            ),
        } == set(db["jobs"].foreign_keys)
        assert {
            (1, ("project_id", "build_num")),
            (0, ("project_id",)),
        } == {(i.unique, tuple(i.columns)) for i in db["jobs"].indexes}
        job_rows = list(db["jobs"].rows)
        assert [
            {
                "id": 1,
                "usage_queued_at": "2021-07-25T19:05:57.081Z",
                "build_url": "https://circleci.com/gh/seeM/circleci-to-sqlite/8",
                "parallel": 1,
                "failed": 0,
                "branch": "main",
                "build_num": 8,
                "status": "success",
                "stop_time": "2021-07-25T19:06:10.095Z",
                "start_time": "2021-07-25T19:06:00.760Z",
                "queued_at": "2021-07-25T19:05:57.124Z",
                "canceled": 0,
                "user_id": 559360,
                "user_name": "seeM",
                "job_name": "build-and-test",
                "job_id": "49b34cdd-748a-48ae-b989-c879daa046bc",
                "workflow_id": "0ae884c6-d352-4f4d-9591-92902d6c78fe",
                "workspace_id": "0ae884c6-d352-4f4d-9591-92902d6c78fe",
                "workflow_name": "build-and-test",
                "project_id": 1,
            },
            {
                "id": 2,
                "usage_queued_at": "2021-07-25T17:21:27.309Z",
                "build_url": "https://circleci.com/gh/seeM/circleci-to-sqlite/2",
                "parallel": 1,
                "failed": 1,
                "branch": "main",
                "build_num": 2,
                "status": "failed",
                "stop_time": "2021-07-25T17:21:37.904Z",
                "start_time": "2021-07-25T17:21:30.268Z",
                "queued_at": "2021-07-25T17:21:27.363Z",
                "canceled": 0,
                "user_id": 559360,
                "user_name": "seeM",
                "job_name": "build-and-test",
                "job_id": "05a2f80d-12a9-417c-8ce6-03e840e6110d",
                "workflow_id": "11b0a96f-8e0a-4285-ba22-3a2801f2ebbd",
                "workspace_id": "11b0a96f-8e0a-4285-ba22-3a2801f2ebbd",
                "workflow_name": "build-and-test",
                "project_id": 1,
            },
        ] == job_rows
