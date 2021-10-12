from aws_infrastructure.tasks.collection import compose_collection
import aws_infrastructure.tasks.library.config
from invoke import Collection

import tasks.celery
import tasks.database
import tasks.install_dependencies
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

# Collections for development and production
ns_dev = Collection('dev')
ns_prod = Collection('prod')

# Compose from celery.py
# compose_collection(ns, tasks.celery.ns, name='celery')

# Compose from database.py
# compose_collection(ns, tasks.database.ns, name='database')

# Compose from dependencies.py
compose_collection(
    ns_dev,
    tasks.install_dependencies.ns.collections['dev'],
    sub=False,
)

# Compose from flask.py
compose_collection(
    ns_dev,
    tasks.flask.ns.collections['dev'],
    sub=False,
)
compose_collection(
    ns_prod,
    tasks.flask.ns.collections['prod'],
    sub=False,
)

# Compose from web.py
compose_collection(
    ns_dev,
    tasks.web.ns.collections['dev'],
    sub=False,
)
compose_collection(
    ns_prod,
    tasks.web.ns.collections['prod'],
    sub=False,
)

# Compose development and production
compose_collection(ns, ns_dev, 'dev')
compose_collection(ns, ns_prod, 'prod')
