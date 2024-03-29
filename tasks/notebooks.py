"""
Task for running Jupyter Lab.
"""

from pathlib import Path
from invoke import Collection, task

import aws_infrastructure.tasks.terminal

NOTEBOOKS_PATH = "./notebooks"


@task
def build(context):
    """
    Rebuild JupyterLab.
    """

    with context.cd(Path(NOTEBOOKS_PATH)):
        context.run(
            command=" ".join(
                [
                    "pipenv",
                    "run",
                    "jupyter",
                    "lab",
                    "clean",
                    "--all",
                ]
            ),
        )

        context.run(
            command=" ".join(
                [
                    "pipenv",
                    "run",
                    "jupyter",
                    "lab",
                    "build",
                ]
            ),
        )


@task
def serve(context):
    """
    Serve JupyterLab.
    """

    if aws_infrastructure.tasks.terminal.spawn_new_terminal(context):
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

ns.add_task(build, "build")
ns.add_task(serve, "serve")
