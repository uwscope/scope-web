import aws_infrastructure.task_templates.config
from invoke import Collection
from invoke import task
from pathlib import Path

# Build our task collection
ns = Collection()

# Tasks for Invoke configuration
ns_config = aws_infrastructure.task_templates.config.create_tasks()
ns.add_collection(ns_config)
ns.configure(ns_config.configuration())

#
# Tasks for the web client
#
ns_web = Collection('web')

# Tasks for development
ns_web_dev = Collection('dev')


@task
def web_start(context):
    """
    Start a development build of the client, listening on `localhost:3000`.

    Builds a development bundle according to 'config/webpack.dev.js', including hot reloading.
    """

    context.run(
        command=' '.join([
            'yarn',
            'start',
        ])
    )


ns_web_dev.add_task(web_start, name='start')

# Tasks for production
ns_web_prod = Collection('prod')


@task
def web_build(context):
    """
    Build a production bundle of the client.

    Invokes `scripts/build.js`, which builds a production bundle according to `config/webpack.prod.js`.
    """

    context.run(
        command=' '.join([
            'yarn',
            'build',
        ])
    )


@task
def web_serve(context):
    """
    Serve a production bundle of the client, listening on `localhost:3000`.
    """

    context.run(
        command=' '.join([
            'yarn',
            'serve',
        ])
    )


ns_web_prod.add_task(web_build, name='build')
ns_web_prod.add_task(web_serve, name='serve')

ns_web.add_collection(ns_web_dev)
ns_web.add_collection(ns_web_prod)
ns.add_collection(ns_web)

#
# Tasks for the Flask server
#
ns_flask = Collection('flask')

ns_flask_dev = Collection('dev')


@task
def flask_start(context):
    """
    Start a development build of Flask, listening on `localhost:4000`.
    """

    with context.cd(Path('server', 'flask')):
        context.run(
            command=' '.join([
                'flask',
                'run',
            ])
        )


ns_flask_dev.add_task(flask_start, name='start')

ns_flask.add_collection(ns_flask_dev)
ns.add_collection(ns_flask)
