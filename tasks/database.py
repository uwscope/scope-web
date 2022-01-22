from aws_infrastructure.tasks.collection import compose_collection
from invoke import Collection

import scope.tasks.database

INSTANCE_SSH_CONFIG_PATH = './secrets/configuration/instance_ssh.yaml'
DOCUMENTDB_CONFIG_PATH = './secrets/configuration/documentdb.yaml'
DEMO_DATABASE_CONFIG_PATH = "./secrets/configuration/demo_database.yaml"
DEV_DATABASE_CONFIG_PATH = "./secrets/configuration/dev_database.yaml"


# Build task collection
ns = Collection("database")

ns_demo = Collection("demo")
ns_demo.add_task(scope.tasks.database.task_initialize(
    instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
    documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
    database_config_path=DEMO_DATABASE_CONFIG_PATH,
), "initialize")
ns_demo.add_task(scope.tasks.database.task_reset(
    instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
    documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
    database_config_path=DEMO_DATABASE_CONFIG_PATH,
), "reset")

ns_dev = Collection("dev")
ns_dev.add_task(scope.tasks.database.task_initialize(
    instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
    documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
    database_config_path=DEV_DATABASE_CONFIG_PATH,
), "initialize")
ns_dev.add_task(scope.tasks.database.task_reset(
    instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
    documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
    database_config_path=DEV_DATABASE_CONFIG_PATH,
), "reset")

compose_collection(ns, ns_demo, name="demo")
compose_collection(ns, ns_dev, name="dev")
