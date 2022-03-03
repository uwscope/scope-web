from aws_infrastructure.tasks.collection import compose_collection
from pathlib import Path
from invoke import Collection

import scope.tasks.database_initialize
import scope.tasks.database_populate
import scope.tasks.database_reset

INSTANCE_SSH_CONFIG_PATH = './secrets/configuration/instance_ssh.yaml'
DOCUMENTDB_CONFIG_PATH = './secrets/configuration/documentdb.yaml'

DATABASE_DEMO_CONFIG_PATH = "./secrets/configuration/database_demo.yaml"
POPULATE_DEMO_DIR_PATH = "./secrets/configuration/populate_demo"
POPULATE_RESET_DEMO_DIR_PATH = "./secrets/configuration/populate_reset_demo"

DATABASE_DEV_CONFIG_PATH = "./secrets/configuration/database_dev.yaml"
POPULATE_DEV_DIR_PATH = "./secrets/configuration/populate_dev"
POPULATE_RESET_DEV_DIR_PATH = "./secrets/configuration/populate_reset_dev"


# Build task collection
ns = Collection("database")

if Path(DATABASE_DEMO_CONFIG_PATH).exists():
    ns_demo = Collection("demo")
    ns_demo.add_task(scope.tasks.database_initialize.task_initialize(
        instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
        documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
        database_config_path=DATABASE_DEMO_CONFIG_PATH,
    ), "initialize")
    ns_demo.add_task(scope.tasks.database_populate.task_populate(
        instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
        documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
        database_config_path=DATABASE_DEMO_CONFIG_PATH,
        populate_dir_path=POPULATE_DEMO_DIR_PATH,
    ), "populate")
    ns_demo.add_task(scope.tasks.database_reset.task_reset(
        instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
        documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
        database_config_path=DATABASE_DEMO_CONFIG_PATH,
        populate_dir_path=POPULATE_DEMO_DIR_PATH,
        populate_reset_dir_path=POPULATE_RESET_DEMO_DIR_PATH,
    ), "reset")

    compose_collection(ns, ns_demo, name="demo")

if Path(DATABASE_DEV_CONFIG_PATH).exists():
    ns_dev = Collection("dev")
    ns_dev.add_task(scope.tasks.database_initialize.task_initialize(
        instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
        documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
        database_config_path=DATABASE_DEV_CONFIG_PATH,
    ), "initialize")
    ns_dev.add_task(scope.tasks.database_populate.task_populate(
        instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
        documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
        database_config_path=DATABASE_DEV_CONFIG_PATH,
        populate_dir_path=POPULATE_DEV_DIR_PATH,
    ), "populate")
    ns_dev.add_task(scope.tasks.database_reset.task_reset(
        instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
        documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
        database_config_path=DATABASE_DEV_CONFIG_PATH,
        populate_dir_path=POPULATE_DEV_DIR_PATH,
        populate_reset_dir_path=POPULATE_RESET_DEV_DIR_PATH,
    ), "reset")

    compose_collection(ns, ns_dev, name="dev")
