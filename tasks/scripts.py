"""
Task for scripts that execute against the instances.
"""

from pathlib import Path
from aws_infrastructure.tasks.collection import compose_collection
from invoke import Collection

import scope.tasks.extend_schedules

INSTANCE_SSH_CONFIG_PATH = "./secrets/configuration/instance_ssh.yaml"
COGNITO_CONFIG_PATH = "./secrets/configuration/cognito.yaml"
DOCUMENTDB_CONFIG_PATH = "./secrets/configuration/documentdb.yaml"
DATABASE_DEMO_CONFIG_PATH = "./secrets/configuration/database_demo.yaml"
DATABASE_DEV_CONFIG_PATH = "./secrets/configuration/database_dev.yaml"
DATABASE_MULTICARE_CONFIG_PATH = "./secrets/configuration/database_multicare.yaml"
DATABASE_SCCA_CONFIG_PATH = "./secrets/configuration/database_scca.yaml"
ALLOWLIST_PATIENT_ID_EXTEND_SCHEDULES_PATH = (
    "./secrets/configuration/allowlist_patient_id_extend_schedules.yaml"
)
DENYLIST_PATIENT_ID_EXTEND_SCHEDULES_PATH = (
    "./secrets/configuration/denylist_patient_id_extend_schedules.yaml"
)


task_script_args = {
    "instance_ssh_config_path": INSTANCE_SSH_CONFIG_PATH,
    "cognito_config_path": COGNITO_CONFIG_PATH,
    "documentdb_config_path": DOCUMENTDB_CONFIG_PATH,
    "allowlist_patient_id_extend_schedules_path": ALLOWLIST_PATIENT_ID_EXTEND_SCHEDULES_PATH,
    "denylist_patient_id_extend_schedules_path": DENYLIST_PATIENT_ID_EXTEND_SCHEDULES_PATH,
}

# Build task collection
ns = Collection("scripts")

database_configs = {
    "demo": DATABASE_DEMO_CONFIG_PATH,
    "dev": DATABASE_DEV_CONFIG_PATH,
    "multicare": DATABASE_MULTICARE_CONFIG_PATH,
    "scca": DATABASE_SCCA_CONFIG_PATH,
}

for database_name, config_path in database_configs.items():
    if Path(config_path).exists():
        ns_collection = Collection(database_name)
        ns_collection.add_task(
            scope.tasks.extend_schedules.task_extend_schedules(
                **task_script_args,
                database_config_path=config_path,
            ),
            "extend-schedules",
        )
        compose_collection(ns, ns_collection, name=database_name)
