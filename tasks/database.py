"""
Tasks for working directly with the database cluster.
"""

import pprint
import urllib.parse
from collections import namedtuple
from pathlib import Path

import aws_infrastructure.tasks.library.documentdb
import aws_infrastructure.tasks.ssh
import ruamel.yaml
from invoke import Collection, task
from pymongo import MongoClient
from pymongo.errors import OperationFailure

from tasks.terminal import spawn_new_terminal

SSH_CONFIG_PATH = "./secrets/server/prod/ssh_config.yaml"
DOCUMENTDB_CONFIG_PATH = "./secrets/server/prod/documentdb_config.yaml"

# TODO - check with james where can this file sit. Contains db users and their details.
DOCUMENTDB_ACCOUNTS_CONFIG_PATH = "./secrets/tests/accounts_config.yaml"

DocumentDBAccount = namedtuple(
    "DocumentDBAccount", ["user", "password", "database", "role"]
)
with open(Path(DOCUMENTDB_ACCOUNTS_CONFIG_PATH)) as db_accounts_config_file:
    db_accounts_config = ruamel.yaml.safe_load(db_accounts_config_file)

DOCUMENTDB_ACCOUNTS = [
    DocumentDBAccount(
        user=account_current["user"],
        password=account_current["password"],
        database=account_current["database"],
        role=account_current["role"],
    )
    for account_current in db_accounts_config["accounts"]
]


@task
def database_forward(context):
    """
    Forward the database cluster, listening on `localhost:5000`.

    Use a fixed port because Studio 3T will save the connection information.
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
                local_port=5000,
            ) as ssh_port_forward:
                mongodbcompass_connection_string = "mongodb://{}:{}@{}:{}/?{}".format(
                    urllib.parse.quote_plus(documentdb_config.admin_user),
                    urllib.parse.quote_plus(documentdb_config.admin_password),
                    "localhost",
                    ssh_port_forward.local_port,
                    "&".join(
                        [
                            "ssl=true",
                            "sslMethod=UNVALIDATED",
                            "serverSelectionTimeoutMS=5000",
                            "connectTimeoutMS=10000",
                            "authSource=admin",
                            "authMechanism=SCRAM-SHA-1",
                        ]
                    ),
                )

                studio3t_connection_string = "mongodb://{}:{}@{}:{}/?{}".format(
                    urllib.parse.quote_plus(documentdb_config.admin_user),
                    urllib.parse.quote_plus(documentdb_config.admin_password),
                    "localhost",
                    ssh_port_forward.local_port,
                    "&".join(
                        [
                            "ssl=true",
                            "sslInvalidHostNameAllowed=true",
                            "serverSelectionTimeoutMS=5000",
                            "connectTimeoutMS=10000",
                            "authSource=admin",
                            "authMechanism=SCRAM-SHA-1",
                            "3t.uriVersion=3",
                            "3t.connection.name={}".format(
                                urllib.parse.quote_plus("UWScope Production Cluster")
                            ),
                            "3t.alwaysShowAuthDB=true",
                            "3t.alwaysShowDBFromUserRole=true",
                            "3t.sslTlsVersion=TLS",
                            "3t.proxyType=none",
                        ]
                    ),
                )

                print("")
                print("MongoDB Compass Connection String:")
                print(mongodbcompass_connection_string)
                print("")
                print("Studio 3T Connection String:")
                print(studio3t_connection_string)
                print("")

                ssh_port_forward.serve_forever()


@task
def database_initialize(context):
    """
    Create multiple schemas with access control. Only needs to run once, or each time accounts_config.yaml file is changed.
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
                local_port=5000,
            ) as ssh_port_forward:
                # Connect to DocumentDB
                client = MongoClient(
                    host=["localhost"],
                    port=ssh_port_forward.local_port,
                    connect=True,
                    username=documentdb_config.admin_user,
                    password=documentdb_config.admin_password,
                    tls=True,
                    tlsInsecure=True,
                )
                # Below line confirms if connection was a success!
                print(client.server_info())

                for db_account in DOCUMENTDB_ACCOUNTS:
                    print(db_account)

                    db = client[db_account.database]

                    # Create a collection "metadata".
                    coll = db.metadata

                    metadata_doc = {
                        "db_user": db_account.user,
                        "role": db_account.role,
                    }

                    # Check if metadata already exists? If yes, then we already have an initalized database.
                    if coll.find_one(metadata_doc) == None:
                        # Need to insert a document for database and collection creation. Database doesn't get created without a collection.
                        coll.insert_one(
                            {
                                "db_user": db_account.user,
                                "role": db_account.role,
                            }
                        )
                        db.command(
                            "createUser",
                            db_account.user,
                            pwd=db_account.password,
                            roles=[
                                {"role": db_account.role, "db": db_account.database}
                            ],
                        )
                    else:
                        print(
                            "In {}: Metadata document already exists.".format(
                                db_account.database
                            )
                        )

                # Verification
                print("List of databases")
                print(client.list_database_names())
                # ssh_port_forward.serve_forever()


@task
def get_all_db_users(context):
    """Get all document db databases and their users."""

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
                local_port=5000,
            ) as ssh_port_forward:
                # Connect to DocumentDB
                client = MongoClient(
                    host=["localhost"],
                    port=ssh_port_forward.local_port,
                    connect=True,
                    username=documentdb_config.admin_user,
                    password=documentdb_config.admin_password,
                    tls=True,
                    tlsInsecure=True,
                )

                db = client.admin
                print("Admin DB Users:")

                pprint.pprint(db.command("usersInfo", 1)["users"])
                print("")


@task
def delete_db_user(context):
    """Takes the username and deletes that user from the database. Prints out an error message if the user doesn't exist."""

    if spawn_new_terminal(context):

        user_name = input("Please enter the db username you'd like to delete:")

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
                local_port=5000,
            ) as ssh_port_forward:
                # Connect to DocumentDB
                client = MongoClient(
                    host=["localhost"],
                    port=ssh_port_forward.local_port,
                    connect=True,
                    username=documentdb_config.admin_user,
                    password=documentdb_config.admin_password,
                    tls=True,
                    tlsInsecure=True,
                )

                db = client.admin
                print("Users before deletion:")
                pprint.pprint(db.command("usersInfo", 1)["users"])

                # NOTE: 2nd argument below is the username.
                db.command("dropUser", user_name)

                print("Users after deletion:")
                pprint.pprint(db.command("usersInfo", 1)["users"])
                print("")


@task
def test_db_user(context):
    """
    Tests if "dev" db user is able to access "dev" db documents. Should pass.
    Tests if "dev" db user is able to access "demo" db documents. Should fail.
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
                local_port=5000,
            ) as ssh_port_forward:
                # Connect to DocumentDB
                client = MongoClient(
                    host=["localhost"],
                    port=ssh_port_forward.local_port,
                    connect=True,
                    username="scope_dev",
                    password="9CUdahxuuJCRplG3YBhcFkhfnq2lAq11",
                    tls=True,
                    tlsInsecure=True,
                )

                db = client.dev
                coll = db.metadata
                # Should print the documents in metadata collection.
                for doc in coll.find({}):
                    print(doc)

                db = client.demo
                coll = db.metadata
                # Should fail
                try:
                    for doc in coll.find({}):
                        print(doc)
                except OperationFailure as err:
                    # Prints out 'Authorization failure'
                    print(err)


# Build task collection
ns = Collection("database")

ns.add_task(database_forward, "forward")
ns.add_task(database_initialize, "initialize")
ns.add_task(test_db_user, "test_db_user")
ns.add_task(get_all_db_users, "get_all_db_users")
ns.add_task(delete_db_user, "delete_db_user")
