# circleci-to-sqlite

[![PyPI](https://img.shields.io/pypi/v/circleci-to-sqlite.svg)](https://pypi.org/project/circleci-to-sqlite/)
[![Changelog](https://img.shields.io/github/v/release/seem/circleci-to-sqlite?include_prereleases&label=changelog)](https://github.com/seem/circleci-to-sqlite/releases)
[![Tests](https://github.com/seem/circleci-to-sqlite/workflows/Test/badge.svg)](https://github.com/seem/circleci-to-sqlite/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/seem/circleci-to-sqlite/blob/main/LICENSE)

Save data from CircleCI to a SQLite database.

## How to install

    $ pip install circleci-to-sqlite

## Authentication

Create a CircleCI personal access token: https://app.circleci.com/settings/user/tokens

Run this command and paste in your new token:

    $ circleci-to-sqlite auth

This will create a file called `auth.json` in your current directory containing the required value. To save the file at a different path or filename, use the `--auth=myauth.json` option.

As an alternative to using an `auth.json` file you can add your access token to an environment variable called `CIRCLECI_TOKEN`.

## Fetching projects for the current user

The `projects` command retrieves all of the projects for the current user.

    $ circleci-to-sqlite projects circleci.db

## Fetching jobs for a project

The `jobs` command retrieves all of the jobs belonging to a project. A project is specified by its slug, which has the form `{vcs_type}/{username}/{reponame}`.

    $ circleci-to-sqlite jobs circleci.db github/seem/circleci-to-sqlite

## Fetching steps for a job

The `steps` command retrieves all of the steps and their actions belonging to a job.

    $ circleci-to-sqlite steps circleci.db github/seem/circleci-to-sqlite 8

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd circleci-to-sqlite
    python -mvenv venv
    source venv/bin/activate

Or if you are using `pipenv`:

    pipenv shell

Now install the dependencies and tests:

    pip install -e '.[test]'

To run the tests:

    pytest
