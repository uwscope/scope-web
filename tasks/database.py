from aws_infrastructure.tasks.collection import compose_collection
import aws_infrastructure.tasks.library.documentdb
import aws_infrastructure.tasks.ssh
import contextlib
from invoke import Collection, task
import pymongo

import scope.config
import scope.database.initialize

INSTANCE_SSH_CONFIG_PATH = './secrets/configuration/instance_ssh.yaml'
DOCUMENTDB_CONFIG_PATH = './secrets/configuration/documentdb.yaml'
DEV_DATABASE_CONFIG_PATH = "./secrets/configuration/dev_database.yaml"


def _documentdb_client_admin(
    *,
    context_manager: contextlib.ExitStack,
    instance_ssh_config: aws_infrastructure.tasks.ssh.SSHConfig,
    documentdb_config: scope.config.DocumentDBConfig,
) -> pymongo.MongoClient:
    """
    Utility function for obtaining a DocumentDB client.
    """

    ssh_client = context_manager.enter_context(
        aws_infrastructure.tasks.ssh.SSHClientContextManager(ssh_config=instance_ssh_config)
    )

    documentdb_port_forward = context_manager.enter_context(
        aws_infrastructure.tasks.ssh.SSHPortForwardContextManager(
            ssh_client=ssh_client,
            remote_host=documentdb_config.endpoint,
            remote_port=documentdb_config.port,
        )
    )

    documentdb_client_admin = pymongo.MongoClient(
        # Synchronously initiate the connection
        connect=True,
        # Connect via SSH port forward
        host="127.0.0.1",
        port=documentdb_port_forward.local_port,
        # Because of the port forward, must not attempt to access the replica set
        directConnection=True,
        # DocumentDB requires SSL, but port forwarding means the certificate will not match
        tls=True,
        tlsInsecure=True,
        # PyMongo defaults to retryable writes, which are not supported by DocumentDB
        # https://docs.aws.amazon.com/documentdb/latest/developerguide/functional-differences.html#functional-differences.retryable-writes
        retryWrites=False,
        # Connect as admin
        username=documentdb_config.admin_user,
        password=documentdb_config.admin_password,
    )

    return documentdb_client_admin


@task
def dev_initialize(context):
    """
    Initialize the database.
    """
    instance_ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(INSTANCE_SSH_CONFIG_PATH)
    documentdb_config = aws_infrastructure.tasks.library.documentdb.DocumentDBConfig.load(DOCUMENTDB_CONFIG_PATH)
    database_config = scope.config.DatabaseConfig.load(DEV_DATABASE_CONFIG_PATH)

    with contextlib.ExitStack() as context_manager:
        documentdb_client_admin = _documentdb_client_admin(
            context_manager=context_manager,
            instance_ssh_config=instance_ssh_config,
            documentdb_config=documentdb_config,
        )

        database = documentdb_client_admin.get_database(
            name=database_config.name,
        )

        scope.database.initialize.initialize(database=database)


@task
def dev_reset(context):
    """
    Reset and initialize the database.
    """

    instance_ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(INSTANCE_SSH_CONFIG_PATH)
    documentdb_config = aws_infrastructure.tasks.library.documentdb.DocumentDBConfig.load(DOCUMENTDB_CONFIG_PATH)
    database_config = scope.config.DatabaseConfig.load(DEV_DATABASE_CONFIG_PATH)

    with contextlib.ExitStack() as context_manager:
        documentdb_client_admin = _documentdb_client_admin(
            context_manager=context_manager,
            instance_ssh_config=instance_ssh_config,
            documentdb_config=documentdb_config,
        )

        documentdb_client_admin.drop_database(
            name_or_database=database_config.name
        )
        database = documentdb_client_admin.get_database(
            name=database_config.name
        )

        scope.database.initialize.initialize(database=database)


# Build task collection
ns = Collection("database")

ns_dev = Collection("dev")
ns_dev.add_task(dev_initialize, "initialize")
ns_dev.add_task(dev_reset, "reset")

compose_collection(ns, ns_dev, name="dev")
