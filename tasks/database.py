"""
Tasks for working directly with the database cluster.
"""

import json
import pprint
import urllib.parse
from collections import namedtuple
from pathlib import Path

import aws_infrastructure.tasks.library.documentdb
import aws_infrastructure.tasks.ssh
import ruamel.yaml
from aws_infrastructure.tasks.collection import compose_collection
from invoke import Collection, task
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from tasks.terminal import spawn_new_terminal

SSH_CONFIG_PATH = "./secrets/server/prod/ssh_config.yaml"
DOCUMENTDB_CONFIG_PATH = "./secrets/server/prod/documentdb_config.yaml"

# TODO - check with james where can this file sit.
DOCUMENTDB_ACCOUNTS_CONFIG_PATH = "./secrets/tests/accounts_config.yaml"

DocumentDBAccount = namedtuple("DocumentDBAccount", ["user", "password", "database"])
with open(Path(DOCUMENTDB_ACCOUNTS_CONFIG_PATH)) as db_accounts_config_file:
    db_accounts_config = ruamel.yaml.safe_load(db_accounts_config_file)

DOCUMENTDB_ACCOUNTS = [
    DocumentDBAccount(
        user=account_current["user"],
        password=account_current["password"],
        database=account_current["database"],
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
    Create multiple schemas with access control.
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
                db = client.demo
                coll = db.patients
                # Need to insert a document for database and collection creation. Database doesn't get created without a collection.
                db.patients.insert_one(
                    {
                        "Item": "Ruler",
                        "Colors": ["Red", "Green", "Blue", "Clear", "Yellow"],
                        "Inventory": {"OnHand": 47, "MinOnHand": 40},
                        "UnitPrice": 0.89,
                    }
                )
                db.command(
                    "createUser",
                    "admin",
                    pwd="password",
                    roles=[{"role": "read", "db": "demo"}],
                )
                return
                client.demo.createUser(
                    {
                        "user": "anant",
                        "pwd": "mittal",
                        "roles": [
                            {"db": "demo", "role": "dbOwner"},
                        ],
                    }
                )
                return

                for db_account in DOCUMENTDB_ACCOUNTS:
                    if db_account.database == "dev":
                        print("Create database and its user")
                        print(db_account)
                        print(type(db_account.database))
                        db_name = db_account.database
                        db = client.dev
                        coll = db.patients
                        db.createUser(
                            {
                                "user": db_account.user,
                                "pwd": db_account.password,
                                "roles": [
                                    {"db": db_name, "role": "readWrite"},
                                ],
                            }
                        )

                # Verification
                print("List of databases")
                print(client.list_database_names())
                # ssh_port_forward.serve_forever()


@task
def test_user(context):
    """
    Create multiple schemas with access control.
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
                    username="admin",
                    password="password",
                    tls=True,
                    tlsInsecure=True,
                )
                # Below line confirms if connection was a success!
                print(client.server_info())
                db = client.demo
                coll = db.patients
                # Need to insert a document for database and collection creation. Database doesn't get created without a collection.
                for doc in db.patients.find({}):
                    print(doc)


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


# Build task collection
ns = Collection("database")

ns.add_task(database_forward, "forward")
ns.add_task(database_initialize, "initialize")
ns.add_task(test_user, "test_user")
ns.add_task(get_all_db_users, "get_all_db_users")
