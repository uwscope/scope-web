import aws_infrastructure.tasks.library.color
from aws_infrastructure.tasks.collection import compose_collection
from invoke import Collection

import tasks.celery
import tasks.database
import tasks.dependencies
import tasks.flask
import tasks.registry
import tasks.tests

# Enable color
aws_infrastructure.tasks.library.color.enable_color()

# Build our task collection
ns = Collection()

# Compose from database.py
# TODO: Move onto new secrets and structure
# compose_collection(ns, tasks.database.ns, name="database")

# Compose from dependencies.py
compose_collection(ns, tasks.dependencies.ns, name="depend")

# Compose from test.py
compose_collection(ns, tasks.tests.ns, name="test")

#
# Collections for development and production
#
ns_dev = Collection("dev")
ns_prod = Collection("prod")

#
# A server collection in each of development and production
#
ns_dev_server = Collection("server")
ns_prod_server = Collection("server")

# Compose from celery.py
# compose_collection(ns_dev_server, tasks.celery.ns.collections["dev"], name="celery")
# compose_collection(ns_prod_server, tasks.celery.ns.collections["prod"], name="celery")

# Compose from flask.py
compose_collection(ns_dev_server, tasks.flask.ns.collections["dev"], name="flask")
compose_collection(ns_prod_server, tasks.flask.ns.collections["prod"], name="flask")

compose_collection(ns_dev, ns_dev_server, name="server")
compose_collection(ns_prod, ns_prod_server, name="server")

#
# A registry collection in each of development and production
#

# Compose from web.py
compose_collection(ns_dev, tasks.registry.ns.collections["dev"], name="registry")
compose_collection(ns_prod, tasks.registry.ns.collections["prod"], name="registry")

#
# Compose development and production
#
compose_collection(ns, ns_dev, name="dev")
compose_collection(ns, ns_prod, name="prod")
