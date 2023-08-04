# test_lancnc.py

import asyncio
from lancnc import LanCNC
from models import Host, HostConnection
from rich.console import Console
from config import CONFIG_DIR, CONFIG_FILE
import logging
from rich.logging import RichHandler
import os


def setup_logging(debug=False):
    """Set up logging configuration."""
    log_file = os.path.join(os.getcwd(), "lancnc_test.log")
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO, filename=log_file, filemode="w"
    )
    logging.getLogger().addHandler(RichHandler())


def cleanup():
    """Clean up the configuration and key files created by the test."""
    if CONFIG_DIR.exists():
        for file in CONFIG_DIR.iterdir():
            file.unlink()
        CONFIG_DIR.rmdir()


def main():
    """Main function to test LanCNC with hardcoded values."""
    debug = True
    setup_logging(debug)
    console = Console()
    lancnc = LanCNC(debug=debug)

    # Host details for testing
    hosts_details = [
        {"name": "host1", "ip": "10.42.0.1", "ssh_key": "~/.ssh/id_rsa"},
        {"name": "host2", "ip": "10.42.0.2", "ssh_key": "~/.ssh/id_rsa"},
        {"name": "host3", "ip": "10.42.0.3", "ssh_key": "~/.ssh/id_rsa"},
    ]

    # Register hosts
    for host_detail in hosts_details:
        connection = HostConnection(
            ip=host_detail["ip"], ssh_key=host_detail["ssh_key"]
        )
        host = Host(name=host_detail["name"], connection=connection)
        lancnc.config.register_host(host)
        console.print(f"[green]Registered host {host_detail['name']}")

    # Execute command on all hosts
    command = "echo `hostname -f`"
    response = asyncio.run(lancnc.run_commands_on_hosts(command))
    console.print(response)

    # Clean up
    cleanup()
    console.print("[yellow]Cleaned up test configuration")


if __name__ == "__main__":
    main()
