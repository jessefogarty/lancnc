# lancnc.py

"""This module defines the LanCNC class responsible for managing remote hosts
and executing commands on them using SSH. It relies on the Config class to
handle host registration and configuration.
"""

import asyncio
from config import Config
from models import HostResponse
from asyncssh import connect
from rich.progress import Progress


class LanCNC:
    """LanCNC class to manage remote hosts and execute commands on them.

    Attributes:
        config: An instance of the Config class to manage host configuration.
        logger: Logger object to handle logging.
        hosts: List of registered hosts.
    """

    def __init__(self, debug=False):
        """Initializes LanCNC with a Config object and logger."""
        self.config = Config(debug=debug)
        self.logger = self.config.logger
        self.hosts = self.config.hosts

    async def execute_command(self, host, command):
        """Execute a command on a remote host using SSH.

        Args:
            host (Host): Configuration of the host to execute on.
            command (str): Command to execute.

        Returns:
            tuple: (host name, command output, return code).
        """
        try:
            connection_info = host.connection
            async with connect(
                connection_info.ip,
                port=connection_info.port,
                username=connection_info.username,
                client_keys=connection_info.ssh_key,
            ) as conn:
                result = await conn.run(command)
                return HostResponse(
                    host=host.name,
                    response=result.stdout,
                    status_code=result.returncode,
                )
        except Exception as e:
            self.logger.error(
                f"[red]Failed to execute command on {host.name}: {str(e)}"
            )
            return HostResponse(host=host.name, response=str(e), status_code=-1)

    async def run_commands_on_hosts(self, command, specific_hosts=None):
        """Execute a command on specific or all registered hosts.

        Args:
            command (str): Command to execute.
            specific_hosts (list, optional): List of specific host names to run on. Defaults to None.

        Returns:
            dict: Response with host names, command output, and status codes.
        """
        hosts_to_run = (
            [host for host in self.hosts if host.name in specific_hosts]
            if specific_hosts
            else self.hosts
        )

        progress = Progress(
            "[progress.description]{task.description}",
            "[progress.percentage]{task.percentage:>3.0f}%",
            transient=True,
        )
        progress.start()
        tasks = [
            progress.add_task(f"Executing on {host.name}", total=1)
            for host in hosts_to_run
        ]

        async def execute_with_progress(task_id, host):
            result = await self.execute_command(host, command)
            progress.update(task_id, advance=1)
            return result

        results = await asyncio.gather(
            *(
                execute_with_progress(task_id, host)
                for task_id, host in zip(tasks, hosts_to_run)
            )
        )
        progress.stop()

        response = {
            result.host: {
                "response": result.response,
                "status_code": result.status_code,
            }
            for result in results
        }
        return response
