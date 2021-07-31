from click.testing import CliRunner
import json
import pathlib
import sqlite_utils
from sqlite_utils.db import ForeignKey
from circleci_to_sqlite.cli import cli


def test_steps(requests_mock):
    requests_mock.get(
        "https://circleci.com/api/v1.1/project/github/seem/circleci-to-sqlite/8",
        json=json.load(open(pathlib.Path(__file__).parent / "steps.json")),
    )
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ["steps", "steps.db", "github/seem/circleci-to-sqlite", "8"],
            catch_exceptions=False,
        )
        assert 0 == result.exit_code

        db = sqlite_utils.Database("steps.db")

        assert {"projects", "jobs", "steps", "actions"}.issubset(set(db.table_names()))

        assert {
            ForeignKey(
                table="steps",
                column="job_id",
                other_table="jobs",
                other_column="id",
            ),
        } == set(db["steps"].foreign_keys)
        assert {
            (1, ("job_id", "index")),
            (0, ("job_id",)),
        } == {(i.unique, tuple(i.columns)) for i in db["steps"].indexes}

        assert {
            ForeignKey(
                table="actions",
                column="step_id",
                other_table="steps",
                other_column="id",
            ),
        } == set(db["actions"].foreign_keys)
        assert {
            (1, ("step_id", "index")),
            (0, ("step_id",)),
        } == {(i.unique, tuple(i.columns)) for i in db["actions"].indexes}

        step_rows = list(db["steps"].rows)
        assert [
            {"id": 1, "job_id": 1, "index": 0, "name": "Spin up environment"},
            {
                "id": 2,
                "job_id": 1,
                "index": 1,
                "name": "Preparing environment variables",
            },
            {"id": 3, "job_id": 1, "index": 2, "name": "Checkout code"},
            {"id": 4, "job_id": 1, "index": 3, "name": "Install packages"},
            {"id": 5, "job_id": 1, "index": 4, "name": "Run tests"},
        ] == step_rows

        action_rows = list(db["actions"].rows)
        assert [
            {
                "id": 1,
                "step_id": 1,
                "truncated": 0,
                "index": 0,
                "parallel": 1,
                "failed": None,
                "infrastructure_fail": None,
                "name": "Spin up environment",
                "bash_command": None,
                "status": "success",
                "timedout": None,
                "continue": None,
                "end_time": "2021-07-25T19:06:03.723Z",
                "type": "test",
                "allocation_id": "60fdb6159f9e936400251553-0-build/4A6B4A04",
                "output_url": "https://circle-production-action-output.s3.amazonaws.com/b87bc204b47dbf5a816bdf06-60fd9d5221f8453d11154053-0-0?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20210731T044756Z&X-Amz-SignedHeaders=host&X-Amz-Expires=432000&X-Amz-Credential=AKIAIJNI6FA5RIAFFQ7Q%2F20210731%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=f94deade6dbd0dfe586037073730b76b0dfd7fd14b516bc0dbcf5eafc52df9eb",
                "start_time": "2021-07-25T19:06:00.808Z",
                "background": 0,
                "exit_code": None,
                "insignificant": 0,
                "canceled": None,
                "step": 0,
                "run_time_millis": 2915,
                "has_output": 1,
            },
            {
                "id": 2,
                "step_id": 2,
                "truncated": 0,
                "index": 0,
                "parallel": 1,
                "failed": None,
                "infrastructure_fail": None,
                "name": "Preparing environment variables",
                "bash_command": None,
                "status": "success",
                "timedout": None,
                "continue": None,
                "end_time": "2021-07-25T19:06:03.920Z",
                "type": "test",
                "allocation_id": "60fdb6159f9e936400251553-0-build/4A6B4A04",
                "output_url": "https://circle-production-action-output.s3.amazonaws.com/2a945bb62404dfd2b16bdf06-60fd9d5221f8453d11154053-99-0?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20210731T044756Z&X-Amz-SignedHeaders=host&X-Amz-Expires=432000&X-Amz-Credential=AKIAIJNI6FA5RIAFFQ7Q%2F20210731%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=2851fe590e5171f48f42977615fbe48f4fbf6b676966657edff195b85fc17c88",
                "start_time": "2021-07-25T19:06:03.891Z",
                "background": 0,
                "exit_code": None,
                "insignificant": 0,
                "canceled": None,
                "step": 99,
                "run_time_millis": 29,
                "has_output": 1,
            },
            {
                "id": 3,
                "step_id": 3,
                "truncated": 0,
                "index": 0,
                "parallel": 1,
                "failed": None,
                "infrastructure_fail": None,
                "name": "Checkout code",
                "bash_command": '#!/bin/sh\nset -e\n\n# Workaround old docker images with incorrect $HOME\n# check https://github.com/docker/docker/issues/2968 for details\nif [ "${HOME}" = "/" ]\nthen\n  export HOME=$(getent passwd $(id -un) | cut -d: -f6)\nfi\n\necho "Using SSH Config Dir \'$SSH_CONFIG_DIR\'"\ngit --version \n\nmkdir -p "$SSH_CONFIG_DIR"\nchmod 0700 "$SSH_CONFIG_DIR"\n\nprintf "%s" \'github.com ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==\nbitbucket.org ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAubiN81eDcafrgMeLzaFPsw2kNvEcqTKl/VqLat/MaB33pZy0y3rJZtnqwR2qOOvbwKZYKiEO1O6VqNEBxKvJJelCq0dTXWT5pbO2gDXC6h6QDXCaHo6pOHGPUy+YBaGQRGuSusMEASYiWunYN0vCAI8QaXnWMXNMdFP3jHAJH0eDsoiGnLPBlBp4TNm6rYI74nMzgz3B9IikW4WVK+dc8KZJZWYjAuORU3jc1c/NPskD2ASinf8v3xnfXeukU0sJ5N6m5E8VLjObPEO+mN2t/FZTMZLiFqPWc/ALSqnMnnhwrNi2rbfg/rd/IpL8Le3pSBne8+seeFVBoGqzHM9yXw==\n\' >> "$SSH_CONFIG_DIR/known_hosts"\nchmod 0600 "$SSH_CONFIG_DIR/known_hosts"\n\nrm -f "$SSH_CONFIG_DIR/id_rsa"\nprintf "%s" "$CHECKOUT_KEY" > "$SSH_CONFIG_DIR/id_rsa"\nchmod 0600 "$SSH_CONFIG_DIR/id_rsa"\nif (: "${CHECKOUT_KEY_PUBLIC?}") 2>/dev/null; then\n  rm -f "$SSH_CONFIG_DIR/id_rsa.pub"\n  printf "%s" "$CHECKOUT_KEY_PUBLIC" > "$SSH_CONFIG_DIR/id_rsa.pub"\nfi\n\nexport GIT_SSH_COMMAND=\'ssh -i "$SSH_CONFIG_DIR/id_rsa" -o UserKnownHostsFile="$SSH_CONFIG_DIR/known_hosts"\'\n\n# use git+ssh instead of https\ngit config --global url."ssh://git@github.com".insteadOf "https://github.com" || true\ngit config --global gc.auto 0 || true\n\nif [ -e \'/home/circleci/project/.git\' ] ; then\n  echo \'Fetching into existing repository\'\n  existing_repo=\'true\'\n  cd \'/home/circleci/project\'\n  git remote set-url origin "$CIRCLE_REPOSITORY_URL" || true\nelse\n  echo \'Cloning git repository\'\n  existing_repo=\'false\'\n  mkdir -p \'/home/circleci/project\'\n  cd \'/home/circleci/project\'\n  git clone --no-checkout "$CIRCLE_REPOSITORY_URL" .\nfi\n\nif [ "$existing_repo" = \'true\' ] || [ \'false\' = \'true\' ]; then\n  echo \'Fetching from remote repository\'\n  if [ -n "$CIRCLE_TAG" ]; then\n    git fetch --force --tags origin\n  else\n    git fetch --force origin \'+refs/heads/main:refs/remotes/origin/main\'\n  fi\nfi\n\nif [ -n "$CIRCLE_TAG" ]; then\n  echo \'Checking out tag\'\n  git checkout --force "$CIRCLE_TAG"\n  git reset --hard "$CIRCLE_SHA1"\nelse\n  echo \'Checking out branch\'\n  git checkout --force -B "$CIRCLE_BRANCH" "$CIRCLE_SHA1"\n  git --no-pager log --no-color -n 1 --format=\'HEAD is now at %h %s\'\nfi\n',
                "status": "success",
                "timedout": None,
                "continue": None,
                "end_time": "2021-07-25T19:06:04.216Z",
                "type": "test",
                "allocation_id": "60fdb6159f9e936400251553-0-build/4A6B4A04",
                "output_url": "https://circle-production-action-output.s3.amazonaws.com/3a945bb62404dfd2b16bdf06-60fd9d5221f8453d11154053-101-0?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20210731T044756Z&X-Amz-SignedHeaders=host&X-Amz-Expires=432000&X-Amz-Credential=AKIAIJNI6FA5RIAFFQ7Q%2F20210731%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=95f1548d217113725cf7bc4101ac4f0dbc39715a310ef253cc0bd5d73e3f078e",
                "start_time": "2021-07-25T19:06:03.933Z",
                "background": 0,
                "exit_code": None,
                "insignificant": 0,
                "canceled": None,
                "step": 101,
                "run_time_millis": 283,
                "has_output": 1,
            },
            {
                "id": 4,
                "step_id": 4,
                "truncated": 0,
                "index": 0,
                "parallel": 1,
                "failed": None,
                "infrastructure_fail": None,
                "name": "Install packages",
                "bash_command": "#!/bin/bash -eo pipefail\npip install -e '.[test]'",
                "status": "success",
                "timedout": None,
                "continue": None,
                "end_time": "2021-07-25T19:06:09.506Z",
                "type": "test",
                "allocation_id": "60fdb6159f9e936400251553-0-build/4A6B4A04",
                "output_url": "https://circle-production-action-output.s3.amazonaws.com/4a945bb62404dfd2c16bdf06-60fd9d5221f8453d11154053-102-0?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20210731T044756Z&X-Amz-SignedHeaders=host&X-Amz-Expires=432000&X-Amz-Credential=AKIAIJNI6FA5RIAFFQ7Q%2F20210731%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=9f32acf0ea0257d4fb3783e960a6fb6b18ccfe7e78cfcc1674e147aebf3bd5b4",
                "start_time": "2021-07-25T19:06:04.226Z",
                "background": 0,
                "exit_code": "0",
                "insignificant": 0,
                "canceled": None,
                "step": 102,
                "run_time_millis": 5280,
                "has_output": 1,
            },
            {
                "id": 5,
                "step_id": 5,
                "truncated": 0,
                "index": 0,
                "parallel": 1,
                "failed": None,
                "infrastructure_fail": None,
                "name": "Run tests",
                "bash_command": "#!/bin/bash -eo pipefail\npytest",
                "status": "success",
                "timedout": None,
                "continue": None,
                "end_time": "2021-07-25T19:06:10.015Z",
                "type": "test",
                "allocation_id": "60fdb6159f9e936400251553-0-build/4A6B4A04",
                "output_url": "https://circle-production-action-output.s3.amazonaws.com/5a72483276c61940126bdf06-60fd9d5221f8453d11154053-103-0?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20210731T044756Z&X-Amz-SignedHeaders=host&X-Amz-Expires=432000&X-Amz-Credential=AKIAIJNI6FA5RIAFFQ7Q%2F20210731%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=1f949dce99c983fef7387cb2f89da93eb1a64081250a80595cb29124fa1d5783",
                "start_time": "2021-07-25T19:06:09.514Z",
                "background": 0,
                "exit_code": "0",
                "insignificant": 0,
                "canceled": None,
                "step": 103,
                "run_time_millis": 501,
                "has_output": 1,
            },
        ] == action_rows
