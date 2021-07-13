"""
Helpers for invoking tasks in new terminals.

Included in project for initial testing, will be moved to aws_infrastructure.
"""

from invoke.context import Context
import os
from pathlib import Path
import platform
import stat
import sys


def spawn_new_terminal(
    context: Context,
) -> bool:
    """
    Spawn a new terminal to run the current command.

    Returns True in the new terminal, False in the original terminal.

    Currently implemented using an environment variable to flag being in a new terminal.
    This implementation likely does not allow spawned terminals to further spawn additional terminals.
    """

    # Detect if we are already in a new terminal, return immediately
    if os.getenv('INVOKE_SPAWN_NEW_TERMINAL'):
        return True

    # Reconstruct the command line
    command = "invoke"
    for arg_current in sys.argv[1:]:
        command = '{} "{}"'.format(command, arg_current)

    # According to platform, run the reconstructed command in a new terminal
    platform_current = platform.system()

    if platform_current.casefold() == 'windows':
        # On Windows:
        # - Use `start` to open a new window.
        # - Use the `cmd` terminal.
        # - Provide `/k` to keep the `cmd` terminal open upon completion (e.g., to view output when debugging).
        #
        # The new terminal will start in the same directory with the same environment variables.

        # Construct the command we actually execute
        command = 'start cmd /k {}'.format(command)

        # Spawn the new terminal
        context.run(
            command=command,
            # Set the INVOKE_SPAWN_NEW_TERMINAL environment variable we will detect from the new terminal
            env={
                'INVOKE_SPAWN_NEW_TERMINAL': 'True'
            },
            # Asynchronously allow the task to proceed in the new terminal
            disown=True
        )
    elif platform_current.casefold() == 'darwin':
        # On Mac:
        # - Write out a command file.
        # - Make that file executable.
        # - `open` it via a new `Terminal`
        #
        # The new terminal will start in the person's home directory.

        path_cwd = Path.cwd()
        path_command = Path(path_cwd, 'INVOKE_SPAWN_NEW_TERMINAL.command')
        with open(path_command, 'w') as file_command:
            # Write a command file
            file_command.writelines('{}\n'.format(line_current) for line_current in [
                # '# Set environment variable that we will detect from the new terminal',
                # 'export INVOKE_SPAWN_NEW_TERMINAL = True',
                # '',
                '# Restore the working directory',
                'cd "{}"'.format(path_cwd),
                '',
                '# Delete this command file',
                'rm -f "{}"'.format(path_command),
                '',
                '# Finally, invoke the command in the new terminal',
                '{}'.format(command),
            ])

            # Make the command file executable
            path_command.chmod(path_command.stat().st_mode | stat.S_IXUSR)

            # Construct the command we actually execute
            command = 'open -a Terminal "{}"'.format(path_command)

            # Spawn the new terminal
            context.run(
                command=command,
                # Set the INVOKE_SPAWN_NEW_TERMINAL environment variable we will detect from the new terminal
                env={
                    'INVOKE_SPAWN_NEW_TERMINAL': 'True'
                },
                # Asynchronously allow the task to proceed in the new terminal
                disown=True
            )
    else:
        raise ValueError('Unsupported platform in spawn_new_terminal: "{}"'.format(platform_current))

    return False
