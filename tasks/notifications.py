"""
Task for sending email notification.
"""

from pathlib import Path
from aws_infrastructure.tasks.collection import compose_collection
from invoke import Collection

import scope.tasks.notifications

INSTANCE_SSH_CONFIG_PATH = "./secrets/configuration/instance_ssh.yaml"
COGNITO_CONFIG_PATH = "./secrets/configuration/cognito.yaml"
DOCUMENTDB_CONFIG_PATH = "./secrets/configuration/documentdb.yaml"
DATABASE_DEMO_CONFIG_PATH = "./secrets/configuration/database_demo.yaml"
DATABASE_DEV_CONFIG_PATH = "./secrets/configuration/database_dev.yaml"
DATABASE_MULTICARE_CONFIG_PATH = "./secrets/configuration/database_multicare.yaml"
DATABASE_SCCA_CONFIG_PATH = "./secrets/configuration/database_scca.yaml"
ALLOWLIST_EMAIL_REMINDER_PATH = "./secrets/configuration/allowlist_email_reminder.yaml"
DENYLIST_EMAIL_REMINDER_PATH = "./secrets/configuration/denylist_email_reminder.yaml"
TEMPLATE_EMAIL_REMINDER_BODY_PATH = "./templates/email_reminder_body.html"
TEMPLATE_EMAIL_REMINDER_SUBJECT_PATH = "./templates/email_reminder_subject.txt"
TEMPLATE_EMAIL_REMINDER_TESTING_BODY_HEADER_PATH = (
    "./templates/email_reminder_testing_body_header.html"
)
TEMPLATE_EMAIL_REMINDER_TESTING_SUBJECT_PREFIX_PATH = (
    "./templates/email_reminder_testing_subject_prefix.txt"
)


task_email_args = {
    "instance_ssh_config_path": INSTANCE_SSH_CONFIG_PATH,
    "cognito_config_path": COGNITO_CONFIG_PATH,
    "documentdb_config_path": DOCUMENTDB_CONFIG_PATH,
    "allowlist_email_reminder_path": ALLOWLIST_EMAIL_REMINDER_PATH,
    "denylist_email_reminder_path": DENYLIST_EMAIL_REMINDER_PATH,
    "templates_email_reminder": scope.tasks.notifications.TemplatesEmailReminder.from_paths(
        template_email_reminder_body_path=TEMPLATE_EMAIL_REMINDER_BODY_PATH,
        template_email_reminder_subject_path=TEMPLATE_EMAIL_REMINDER_SUBJECT_PATH,
        template_email_reminder_testing_body_header_path=TEMPLATE_EMAIL_REMINDER_TESTING_BODY_HEADER_PATH,
        template_email_reminder_testing_subject_prefix_path=TEMPLATE_EMAIL_REMINDER_TESTING_SUBJECT_PREFIX_PATH,
    ),
}

# Build task collection
ns = Collection("notifications")

database_configs = {
    "demo": DATABASE_DEMO_CONFIG_PATH,
    "dev": DATABASE_DEV_CONFIG_PATH,
    "multicare": DATABASE_MULTICARE_CONFIG_PATH,
    "scca": DATABASE_SCCA_CONFIG_PATH,
}

for name, config_path in database_configs.items():
    if Path(config_path).exists():
        ns_collection = Collection(name)
        ns_collection.add_task(
            scope.tasks.notifications.task_email(
                **task_email_args,
                database_config_path=config_path,
            ),
            "email",
        )
        compose_collection(ns, ns_collection, name=name)
