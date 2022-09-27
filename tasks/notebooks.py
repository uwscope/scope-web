"""
Task for running Jupyter Lab.
"""

from pathlib import Path
from invoke import Collection, task

NOTEBOOKS_PATH = "./notebooks"

@task
def run(context):
    """
    Start Jupyter Lab.

    """

    with context.cd(Path(NOTEBOOKS_PATH)):
        context.run(
            command=" ".join(
                [
                    "pipenv",
                    "run",
                    "jupyter",
                    "lab",
                ]
            ),
        )


# Build task collection
ns = Collection("notebooks")

ns.add_task(run, "run")
