"""
Task for sending email notification.
"""

from pathlib import Path
from aws_infrastructure.tasks.collection import compose_collection
from invoke import Collection

import scope.tasks.notifications

INSTANCE_SSH_CONFIG_PATH = "./secrets/configuration/instance_ssh.yaml"
DOCUMENTDB_CONFIG_PATH = "./secrets/configuration/documentdb.yaml"
DATABASE_DEV_CONFIG_PATH = "./secrets/configuration/database_dev.yaml"
ALLOWLIST_EMAIL_REMINDER_PATH = "./secrets/configuration/allowlist_email_reminder.yaml"
DENYLIST_EMAIL_REMINDER_PATH = "./secrets/configuration/denylist_email_reminder.yaml"
TEMPLATE_EMAIL_REMINDER_BODY_PATH = "./templates/email_reminder_body.html"
TEMPLATE_EMAIL_REMINDER_TESTING_HEADER_PATH = (
    "./templates/email_reminder_testing_header.html"
)

# Build task collection
ns = Collection("notifications")

if Path(DATABASE_DEV_CONFIG_PATH).exists():
    ns_dev = Collection("dev")
    ns_dev.add_task(
        scope.tasks.notifications.task_email(
            instance_ssh_config_path=INSTANCE_SSH_CONFIG_PATH,
            documentdb_config_path=DOCUMENTDB_CONFIG_PATH,
            database_config_path=DATABASE_DEV_CONFIG_PATH,
            allowlist_email_reminder_path=ALLOWLIST_EMAIL_REMINDER_PATH,
            denylist_email_reminder_path=DENYLIST_EMAIL_REMINDER_PATH,
            template_email_reminder_body_path=TEMPLATE_EMAIL_REMINDER_BODY_PATH,
            template_email_reminder_testing_header_path=TEMPLATE_EMAIL_REMINDER_TESTING_HEADER_PATH,
        ),
        "email",
    )
    compose_collection(ns, ns_dev, name="dev")
