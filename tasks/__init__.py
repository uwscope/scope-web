import aws_infrastructure.tasks.library.color
from aws_infrastructure.tasks.collection import compose_collection
import aws_infrastructure.tasks.library.aws_configure
from invoke import Collection

import tasks.aws
import tasks.celery
import tasks.database
import tasks.documentdb
import tasks.dependencies
import tasks.server_flask
import tasks.web_patient
import tasks.web_registry
import tasks.test

# Enable color
aws_infrastructure.tasks.library.color.enable_color()
# Apply the current AWS configuration
aws_infrastructure.tasks.library.aws_configure.apply_aws_env(
    aws_env_path=tasks.aws.AWS_ENV_PATH
)

# Build our task collection
ns = Collection()

# Compose from aws.py
# compose_collection(ns, tasks.aws.ns, name="aws")

# Compose from database_populate.py
compose_collection(ns, tasks.database.ns, name="database")

# Compose from documentdb.py
compose_collection(ns, tasks.documentdb.ns, name="documentdb")

# Compose from dependencies.py
compose_collection(ns, tasks.dependencies.ns, name="depend")

# Compose from test.py
compose_collection(ns, tasks.test.ns, name="test")

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

# Compose from server_flask.py
compose_collection(ns_dev_server, tasks.server_flask.ns.collections["dev"], name="flask")
compose_collection(ns_prod_server, tasks.server_flask.ns.collections["prod"], name="flask")

compose_collection(ns_dev, ns_dev_server, name="server")
compose_collection(ns_prod, ns_prod_server, name="server")

#
# A patient collection in each of development and production
#

# Compose from web_patient.py
compose_collection(ns_dev, tasks.web_patient.ns.collections["dev"], name="patient")
compose_collection(ns_prod, tasks.web_patient.ns.collections["prod"], name="patient")

#
# A registry collection in each of development and production
#

# Compose from web_registry.py
compose_collection(ns_dev, tasks.web_registry.ns.collections["dev"], name="registry")
compose_collection(ns_prod, tasks.web_registry.ns.collections["prod"], name="registry")

#
# Compose development and production
#
compose_collection(ns, ns_dev, name="dev")
compose_collection(ns, ns_prod, name="prod")
