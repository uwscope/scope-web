import aws_infrastructure.task_templates.config
from invoke import Collection

import tasks.database
import tasks.flask
import tasks.web

# Build our task collection
ns = Collection()

# Tasks for Invoke configuration
ns.add_collection(
    aws_infrastructure.task_templates.config.create_tasks(),
    name='config'
)

# Tasks from database.py
ns.add_collection(tasks.database, name='database')

# Tasks from flask.py
ns.add_collection(tasks.flask, name='flask')

# Tasks from web.py
ns.add_collection(tasks.web, name='web')
