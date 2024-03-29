"""
Tasks for maintaining the project.

Execute 'invoke --list' for guidance on using Invoke
"""
import webbrowser
from pathlib import Path

from invoke import Failure, Result, task  # type: ignore

ROOT_DIR = Path(__file__).parent
TEST_DIR = ROOT_DIR.joinpath("tests")
SOURCE_DIR = ROOT_DIR.joinpath("mediaarchiver")
TASKS_PY = ROOT_DIR.joinpath("tasks.py")
COVERAGE_DIR = ROOT_DIR.joinpath("htmlcov")
COVERAGE_REPORT = COVERAGE_DIR.joinpath("index.html")
PYTHON_DIRS = [str(d) for d in [TASKS_PY, SOURCE_DIR, TEST_DIR]]


@task(help={"check": "Checks if source is formatted without applying changes"})
def style(context, check=False):
    """
    Format code
    """
    for result in [
        isort(context, check),
        black(context, check),
    ]:
        if result.failed:
            raise Failure(result)


def isort(context, check=False) -> Result:
    """Runs isort."""
    isort_options = "{}".format("--check-only --diff" if check else "")
    return context.run("isort {} {}".format(isort_options, " ".join(PYTHON_DIRS)), warn=True)


def black(context, check=False) -> Result:
    """Runs black."""
    black_options = "{}".format("--check --diff" if check else "")
    return context.run("black {} {}".format(black_options, " ".join(PYTHON_DIRS)), warn=True)


@task
def lint_flake8(context):
    """
    Lint code with flake8
    """
    context.run("flake8 {} {}".format("--radon-show-closures", " ".join(PYTHON_DIRS)))


@task
def lint_pylint(context):
    """
    Lint code with pylint
    """
    context.run("pylint {}".format(" ".join(PYTHON_DIRS)))


@task
def lint_mypy(context):
    """
    Lint code with pylint
    """
    context.run("mypy {}".format(" ".join(PYTHON_DIRS)))


@task(lint_flake8, lint_pylint, lint_mypy)
def lint(_context):
    """
    Run all linting
    """


@task
def radon_cc(context):
    """
    Reports code complexity.
    """
    context.run("radon cc {}".format(" ".join(PYTHON_DIRS)))


@task
def radon_mi(context):
    """
    Reports maintainability index.
    """
    context.run("radon mi {}".format(" ".join(PYTHON_DIRS)))


@task(radon_cc, radon_mi)
def radon(_context):
    """
    Reports radon.
    """


@task
def xenon(context):
    """
    Check code complexity.
    """
    context.run(("xenon --max-absolute B --max-modules B --max-average B {}").format(" ".join(PYTHON_DIRS)))


@task(help={"publish": "Publish the result via coveralls", "xml": "Export report as xml format"})
def coverage(context, publish=False, xml=False):
    """
    Create coverage report
    """
    context.run("coverage run --source {} -m pytest".format(SOURCE_DIR))
    context.run("coverage report")
    if publish:
        # Publish the results via coveralls
        context.run("coveralls")
        return
    # Build a local report
    if xml:
        context.run("coverage xml")
    else:
        context.run("coverage html")
        webbrowser.open(COVERAGE_REPORT.as_uri())
