"""
Tasks for working directly with the database cluster.
"""

from aws_infrastructure.tasks.collection import compose_collection
import aws_infrastructure.tasks.library.documentdb
import aws_infrastructure.tasks.ssh
import aws_infrastructure.tasks.terminal
from invoke import Collection
from invoke import task
import urllib.parse

INSTANCE_SSH_CONFIG_PATH = './secrets/configuration/instance_ssh.yaml'
DOCUMENTDB_CONFIG_PATH = './secrets/configuration/documentdb.yaml'


@task
def documentdb_forward(context):
    """
    Forward the DocumentDB cluster, listening on `localhost:5000`.

    Use a fixed port so clients can save the connection information.
    """

    if aws_infrastructure.tasks.terminal.spawn_new_terminal(context):
        ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(INSTANCE_SSH_CONFIG_PATH)
        documentdb_config = aws_infrastructure.tasks.library.documentdb.DocumentDBConfig.load(DOCUMENTDB_CONFIG_PATH)

        with aws_infrastructure.tasks.ssh.SSHClientContextManager(ssh_config=ssh_config) as ssh_client:
            with aws_infrastructure.tasks.ssh.SSHPortForwardContextManager(
                ssh_client=ssh_client,
                remote_host=documentdb_config.endpoint,
                remote_port=documentdb_config.port,
                local_port=5000,
            ) as ssh_port_forward:
                mongodbcompass_connection_string = 'mongodb://{}:{}@{}:{}/?{}'.format(
                    urllib.parse.quote_plus(documentdb_config.admin_user),
                    urllib.parse.quote_plus(documentdb_config.admin_password),
                    'localhost',
                    ssh_port_forward.local_port,
                    '&'.join([
                        'ssl=true',
                        'directConnection=true',
                        'serverSelectionTimeoutMS=5000',
                        'connectTimeoutMS=10000',
                        'authSource=admin',
                        'authMechanism=SCRAM-SHA-1',
                    ]),
                )

                studio3t_connection_string = 'mongodb://{}:{}@{}:{}/?{}'.format(
                    urllib.parse.quote_plus(documentdb_config.admin_user),
                    urllib.parse.quote_plus(documentdb_config.admin_password),
                    'localhost',
                    ssh_port_forward.local_port,
                    '&'.join([
                        'ssl=true',
                        'sslInvalidHostNameAllowed=true',
                        'serverSelectionTimeoutMS=5000',
                        'connectTimeoutMS=10000',
                        'authSource=admin',
                        'authMechanism=SCRAM-SHA-1',
                        '3t.uriVersion=3',
                        '3t.connection.name={}'.format(
                            urllib.parse.quote_plus('UWScope Production Cluster')
                        ),
                        '3t.alwaysShowAuthDB=true',
                        '3t.alwaysShowDBFromUserRole=true',
                        '3t.sslTlsVersion=TLS',
                        '3t.proxyType=none',
                    ]),
                )

                print('')
                print('MongoDB Compass Connection String:')
                print(mongodbcompass_connection_string)
                print('')
                print('Studio 3T Connection String:')
                print(studio3t_connection_string)
                print('')

                ssh_port_forward.serve_forever()


# Build task collection
ns = Collection('documentdb')

ns.add_task(documentdb_forward, 'forward')
