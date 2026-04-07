"""Nox testing"""

import nox


@nox.session(python=["3.12", "3.13", "3.14"])
def tests(session):
    session.run("pip", "install", "-r", "requirements-dev.txt")
    session.run("pip", "install", ".")
    session.run("pytest", "--cov=aiopvapi",
                "--cov-report=xml:cov.xml", "tests")
