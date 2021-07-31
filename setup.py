from setuptools import setup
import os

VERSION = "0.3.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="circleci-to-sqlite",
    description="Save data from CircleCI to a SQLite database",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Wasim Lorgat",
    url="https://github.com/seem/circleci-to-sqlite",
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["circleci_to_sqlite"],
    entry_points="""
        [console_scripts]
        circleci-to-sqlite=circleci_to_sqlite.cli:cli
    """,
    install_requires=["sqlite-utils>=2.7.2", "requests"],
    extras_require={"test": ["pytest", "requests-mock", "bs4"]},
    tests_require=["circleci-to-sqlite[test]"],
)
