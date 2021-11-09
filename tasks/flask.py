"""
Tasks for the Flask server.
"""

from pathlib import Path

import aws_infrastructure.tasks.library.documentdb
import aws_infrastructure.tasks.ssh
from aws_infrastructure.tasks.collection import compose_collection
from invoke import Collection, task

from tasks.terminal import spawn_new_terminal

FLASK_DIR = "./server_flask"
SSH_CONFIG_PATH = "./secrets/server/prod/ssh_config.yaml"
DOCUMENTDB_CONFIG_PATH = "./secrets/server/prod/documentdb_config.yaml"


@task
def dev_serve(context):
    """
    Start Flask, listening on `localhost:4000`, including hot reloading.

    For development purposes, asynchronously starts in a new terminal.
    """

    if spawn_new_terminal(context):
        ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(SSH_CONFIG_PATH)
        documentdb_config = (
            aws_infrastructure.tasks.library.documentdb.DocumentDBConfig.load(
                DOCUMENTDB_CONFIG_PATH
            )
        )

        with aws_infrastructure.tasks.ssh.SSHClientContextManager(
            ssh_config=ssh_config
        ) as ssh_client:
            with aws_infrastructure.tasks.ssh.SSHPortForwardContextManager(
                ssh_client=ssh_client,
                remote_host=documentdb_config.endpoint,
                remote_port=documentdb_config.port,
            ) as ssh_port_forward:
                with context.cd(Path(FLASK_DIR)):
                    context.run(
                        # Instead of using `flask run`, import the app normally, then run it.
                        # Did this because `flask run` was eating an ImportError, not giving a useful error message.
                        command=" ".join(
                            [
                                "pipenv",
                                "run",
                                "python",
                                "app.py",
                            ]
                        ),
                        env={
                            "FLASK_ENV": "development",
                            "FLASK_RUN_HOST": "localhost",
                            "FLASK_RUN_PORT": "4000",
                            "LOCAL_DOCUMENTDB_PORT": str(ssh_port_forward.local_port),
                        },
                    )


@task
def prod_serve(context):
    """
    Start Flask, listening on `0.0.0.0:4000`.

    For production purposes, synchronously executes in the current terminal.
    """

    with context.cd(Path(FLASK_DIR)):
        context.run(
            command=" ".join(
                [
                    "pipenv",
                    "run",
                    "waitress-serve",
                    "--port=4000",
                    '--call "app:create_app"',
                ]
            ),
            env={"FLASK_ENV": "production"},
        )


# Build task collection
ns = Collection("flask")

ns_dev = Collection("dev")
ns_dev.add_task(dev_serve, "serve")

ns_prod = Collection("prod")
ns_prod.add_task(prod_serve, "serve")

compose_collection(ns, ns_dev, name="dev")
compose_collection(ns, ns_prod, name="prod")
