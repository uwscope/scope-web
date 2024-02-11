"""
Task for applying code formatting.
"""

from invoke import Collection, task


@task
def format(context):
    """
    Apply code formatting.
    """

    context.run(
        command=" ".join(
            [
                "pipenv",
                "run",
                "black",
                ".",
            ]
        ),
    )

    result = context.run(
        command=" ".join(
            [
                "yarn",
                "prettier",
                ".",
                "--list-different",
            ]
        ),
        warn=True,
    )
    if result.exited > 0:
        result = context.run(
            command=" ".join(
                [
                    "yarn",
                    "format",
                ]
            ),
        )


# Build task collection
ns = Collection("format")

ns.add_task(format, "format")
