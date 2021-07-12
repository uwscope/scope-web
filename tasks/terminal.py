"""
Helpers for invoking tasks in new terminals.

Included in project for initial testing, will be moved to aws_infrastructure.
"""

from invoke.context import Context
import os
import platform
import sys
from typing import Dict


def run_new_terminal(
    context: Context,
    command: str,                # Original non-augmented command string
    env: Dict[str, str] = None,  # Environment variables to pass through
) -> None:
    """
    Run a command, augmenting the command so it runs in a new terminal.
    """

    # Modify the command according to platform
    platform_current = platform.system()

    if platform_current.casefold() == 'windows':
        command = 'start cmd /k {}'.format(command)
    elif platform_current.casefold() == 'darwin':
        command = 'open -a Terminal "{}"'.format(command)
    else:
        raise ValueError('Unsupported platform "{}"'.format(platform_current))

    # Execute the modified command and disown the resulting process
    context.run(
        command=command,
        disown=True,
        # Passthrough unmodified
        env=env,
    )


def spawn_new_terminal(
    context: Context,
) -> bool:
    """
    Spawn a new terminal to run the current command.

    Returns True in the new terminal, False in the original terminal.

    Currently implemented using an environment variable to flag being in a new terminal.
    This implementation likely does not allow spawned terminals to further spawn additional terminals.
    """

    if os.getenv('INVOKE_SPAWN_NEW_TERMINAL'):
        return True

    command = "invoke"
    for arg_current in sys.argv[1:]:
        if ' ' in arg_current:
            command = '{} "{}"'.format(command, arg_current)
        else:
            command = '{} {}'.format(command, arg_current)

    run_new_terminal(
        context=context,
        command=command,
        env={
            'INVOKE_SPAWN_NEW_TERMINAL': 'True'
        }
    )

    return False
