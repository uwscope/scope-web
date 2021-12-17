import aws_infrastructure.tasks.ssh
import pytest
import requests
from typing import Callable
from urllib.parse import urljoin

import scope.config


@pytest.fixture(name="documentdb_port_forward")
def fixture_documentdb_port_forward(
    instance_ssh_config: aws_infrastructure.tasks.ssh.SSHConfig,
    documentdb_config: scope.config.DocumentDBConfig,
    testing_fixtures: bool,
) -> aws_infrastructure.tasks.ssh.SSHPortForward:
    """
    Fixture for opening a local port that forwards to the DocumentDB cluster.

    Use a single fixture for the entire session.
    Establishing the SSH tunnel is an expensive operation that then has no state across tests.
    """

    ssh_client = aws_infrastructure.tasks.ssh.SSHClient(ssh_config=instance_ssh_config)
    ssh_client.open()

    ssh_port_forward = aws_infrastructure.tasks.ssh.SSHPortForward(
        ssh_client=ssh_client,
        remote_host=documentdb_config.endpoint,
        remote_port=documentdb_config.port,
    )
    ssh_port_forward.open()

    yield ssh_port_forward

    ssh_port_forward.close()
    ssh_client.close()
