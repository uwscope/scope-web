from aws_infrastructure.tasks.collection import compose_collection
import aws_infrastructure.tasks.library.config
from invoke import Collection

import tasks.celery
import tasks.database
import tasks.dependencies
import tasks.flask
import tasks.web

# Build our task collection
ns = Collection()

# Tasks for Invoke configuration
compose_collection(
    ns,
    aws_infrastructure.tasks.library.config.create_tasks(),
    name='config'
)

# Compose from celery.py
compose_collection(ns, tasks.celery.ns, name='celery')

# Compose from database.py
compose_collection(ns, tasks.database.ns, name='database')

# Compose from dependencies.py
compose_collection(ns, tasks.dependencies.ns, name='dependencies')

# Compose from flask.py
compose_collection(ns, tasks.flask.ns, name='flask')

# Compose from web.py
compose_collection(ns, tasks.web.ns, name='web')
