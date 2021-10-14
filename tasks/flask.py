"""
Tasks for the Flask server.
"""

from aws_infrastructure.tasks.collection import compose_collection
import aws_infrastructure.tasks.library.documentdb
import aws_infrastructure.tasks.ssh
from invoke import Collection
from invoke import task
from pathlib import Path

from tasks.terminal import spawn_new_terminal


SSH_CONFIG_PATH = './secrets/server/prod/ssh_config.yaml'
DOCUMENTDB_CONFIG_PATH = './secrets/server/prod/documentdb_config.yaml'


@task
def dev_flask(context):
    """
    Start Flask, listening on `localhost:4000`, including hot reloading.

    For development purposes, asynchronously starts in a new terminal.
    """

    if spawn_new_terminal(context):
        ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(SSH_CONFIG_PATH)
        documentdb_config = aws_infrastructure.tasks.library.documentdb.DocumentDBConfig.load(DOCUMENTDB_CONFIG_PATH)

        with aws_infrastructure.tasks.ssh.SSHClientContextManager(ssh_config=ssh_config) as ssh_client:
            with aws_infrastructure.tasks.ssh.SSHPortForwardContextManager(
                ssh_client=ssh_client,
                remote_host=documentdb_config.endpoint,
                remote_port=documentdb_config.port,
            ) as ssh_port_forward:
                # Run port forward in another thread
                ssh_port_forward.forward_forever(threaded=True)

                with context.cd(Path('server', 'flask')):
                    context.run(
                        command=' '.join([
                            'flask',
                            'run',
                        ]),
                        env={
                            'FLASK_ENV': 'development',
                            'FLASK_RUN_HOST': 'localhost',
                            'FLASK_RUN_PORT': '4000',
                        },
                    )


@task
def prod_flask(context):
    """
    Start Flask, listening on `0.0.0.0:4000`.

    For production purposes, synchronously executes in the current terminal.
    """

    with context.cd(Path('server', 'flask')):
        context.run(
            command=' '.join([
                'waitress-serve',
                '--port=4000',
                '--call "app:create_app"'
            ]),
            env={
                'FLASK_ENV': 'production'
            }
        )


# Build task collection
ns = Collection('flask')

ns_dev = Collection('dev')
ns_dev.add_task(dev_flask, 'flask')

ns_prod = Collection('prod')
ns_prod.add_task(prod_flask, 'flask')

compose_collection(ns, ns_dev, name='dev')
compose_collection(ns, ns_prod, name='prod')
