import aws_infrastructure.task_templates.config
from invoke import Collection

# Build our task collection
ns = Collection()

# Tasks for Invoke configuration
ns_config = aws_infrastructure.task_templates.config.create_tasks()
ns.add_collection(ns_config)
ns.configure(ns_config.configuration())
