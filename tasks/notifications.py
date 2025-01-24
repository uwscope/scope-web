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
BLOCKLIST_EMAIL_REMINDER_PATH = "./secrets/configuration/blocklist_email_reminder.yaml"
TEMPLATE_EMAIL_BODY_REMINDER_PATH = "./templates/email_reminder_body.html"
TEMPLATE_EMAIL_BODY_REMINDER_TESTING_HEADER_PATH = (
    "./templates/testing_email_reminder_body_header.html"
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
            blocklist_email_reminder_path=BLOCKLIST_EMAIL_REMINDER_PATH,
            template_email_body_reminder_path=TEMPLATE_EMAIL_BODY_REMINDER_PATH,
            template_email_body_reminder_testing_header_path=TEMPLATE_EMAIL_BODY_REMINDER_TESTING_HEADER_PATH,
        ),
        "email",
    )
    compose_collection(ns, ns_dev, name="dev")
