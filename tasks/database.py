from aws_infrastructure.tasks.collection import compose_collection
from pathlib import Path
from invoke import Collection

import scope.tasks.database

INSTANCE_SSH_CONFIG_PATH = './secrets/configuration/instance_ssh.yaml'
DOCUMENTDB_CONFIG_PATH = './secrets/configuration/documentdb.yaml'
DATABASE_DEMO_CONFIG_PATH = "./secrets/configuration/database_demo.yaml"
DATABASE_DEV_CONFIG_PATH = "./secrets/configuration/database_dev.yaml"


# Build task collection
ns = Collection("database")

if Path(DATABASE_DEMO_CONFIG_PATH).exists():
    ns_demo = Collection("demo")
    ns_demo.add_task(scope.tasks.database.task_initialize(
        instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
        documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
        database_config_path=DATABASE_DEMO_CONFIG_PATH,
    ), "initialize")
    ns_demo.add_task(scope.tasks.database.task_populate(
        instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
        documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
        database_config_path=DATABASE_DEMO_CONFIG_PATH,
    ), "populate")
    ns_demo.add_task(scope.tasks.database.task_reset(
        instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
        documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
        database_config_path=DATABASE_DEMO_CONFIG_PATH,
    ), "reset")

    compose_collection(ns, ns_demo, name="demo")

if Path(DATABASE_DEV_CONFIG_PATH).exists():
    ns_dev = Collection("dev")
    ns_dev.add_task(scope.tasks.database.task_initialize(
        instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
        documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
        database_config_path=DATABASE_DEV_CONFIG_PATH,
    ), "initialize")
    ns_dev.add_task(scope.tasks.database.task_populate(
        instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
        documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
        database_config_path=DATABASE_DEV_CONFIG_PATH,
    ), "populate")
    ns_dev.add_task(scope.tasks.database.task_reset(
        instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
        documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
        database_config_path=DATABASE_DEV_CONFIG_PATH,
    ), "reset")

    compose_collection(ns, ns_dev, name="dev")
