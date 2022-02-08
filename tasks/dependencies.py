"""
Tasks for ensuring project dependencies are installed.
"""

from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.dependencies
from invoke import Collection


CONFIG_KEY = "dependencies"
DEPENDENCIES = {
    "all": aws_infrastructure.tasks.library.dependencies.Dependency(
        pipfile_dirs=[
            ".",
            "./server_celery",
            "./server_flask",
        ],
        yarn_dirs=[
            "./web_patient",
            "./web_registry",
            "./web_shared",
        ],
    ),
    "javascript": aws_infrastructure.tasks.library.dependencies.Dependency(
        pipfile_dirs=None,
        yarn_dirs=[
            "./web_patient",
            "./web_registry",
            "./web_shared",
        ],
    ),
    "python": aws_infrastructure.tasks.library.dependencies.Dependency(
        pipfile_dirs=[
            ".",
            "./server_celery",
            "./server_flask",
        ],
        yarn_dirs=None,
    ),
    "root": aws_infrastructure.tasks.library.dependencies.Dependency(
        pipfile_dirs=["."],
        yarn_dirs=None,
    ),
    "server_celery": aws_infrastructure.tasks.library.dependencies.Dependency(
        pipfile_dirs=["./server_celery"],
        yarn_dirs=None,
    ),
    "server_flask": aws_infrastructure.tasks.library.dependencies.Dependency(
        pipfile_dirs=["./server_flask"],
        yarn_dirs=None,
    ),
    "web_patient": aws_infrastructure.tasks.library.dependencies.Dependency(
        pipfile_dirs=None,
        yarn_dirs=[
            "./web_patient",
            "./web_shared",
        ],
    ),
    "web_registry": aws_infrastructure.tasks.library.dependencies.Dependency(
        pipfile_dirs=None,
        yarn_dirs=[
            "./web_registry",
            "./web_shared",
        ],
    ),
}


ns = Collection("dependencies")

ns_dependencies = aws_infrastructure.tasks.library.dependencies.create_tasks(
    config_key=CONFIG_KEY,
    dependencies=DEPENDENCIES,
)

compose_collection(
    ns,
    ns_dependencies,
    sub=False,
)
