# circleci-to-sqlite

[![PyPI](https://img.shields.io/pypi/v/circleci-to-sqlite.svg)](https://pypi.org/project/circleci-to-sqlite/)
[![Changelog](https://img.shields.io/circleci/v/release/seem/circleci-to-sqlite?include_prereleases&label=changelog)](https://circleci.com/seem/circleci-to-sqlite/releases)
[![Tests](https://circleci.com/seem/circleci-to-sqlite/workflows/Test/badge.svg)](https://circleci.com/seem/circleci-to-sqlite/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://circleci.com/seem/circleci-to-sqlite/blob/main/LICENSE)

Save data from CircleCI to a SQLite database.

## How to install

    $ pip install circleci-to-sqlite

## Authentication

Create a CircleCI personal access token: https://app.circleci.com/settings/user/tokens

Run this command and paste in your new token:

    $ circleci-to-sqlite auth

This will create a file called `auth.json` in your current directory containing the required value. To save the file at a different path or filename, use the `--auth=myauth.json` option.

As an alternative to using an `auth.json` file you can add your access token to an environment variable called `CIRCLECI_TOKEN`.
