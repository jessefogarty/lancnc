# cli.py

#!/usr/bin/env python3

"""This module provides a command-line interface for registering, updating,
deleting, editing, and executing commands on remote hosts using SSH.
"""

import argparse
import asyncio
from lancnc import LanCNC
from models import Host, HostConnection
from rich.console import Console
import ipaddress

def validate_ip(ip):
    """Validate an IP address.

    Args:
        ip (str): IP address to validate.

    Returns:
        str: Validated IP address.
    """
    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        raise argparse.ArgumentTypeError(f"{ip} is not a valid IPv4 address.")

def main():
    """Main function to parse command-line arguments and execute actions."""
    parser = argparse.ArgumentParser(description="LanCNC: Manage and execute commands on remote hosts")
    parser.add_argument('--debug', action='store_true', help="Enable debug logging")
    subparsers = parser.add_subparsers(dest='action', help="Action to perform")

    # Register command
    register_parser = subparsers.add_parser('register')
    register_parser.add_argument('name', help="Name of the host")
    register_parser.add_argument('ip', type=validate_ip, help="IP address of the host")
    register_parser.add_argument('--port', type=int, default=22, help="SSH port (default is 22)")
    register_parser.add_argument('--ssh_key', help="Path to the SSH key")
    register_parser.add_argument('--username', help="Username for the SSH connection")
    register_parser.add_argument('--password', help="Password for the SSH connection")

    # Delete command
    delete_parser = subparsers.add_parser('delete')
    delete_parser.add_argument('name', help="Name of the host to delete")

    # Update command
    update_parser = subparsers.add_parser('update')
    update_parser.add_argument('name', help="Name of the host to update")
    update_parser.add_argument('--ip', type=validate_ip, help="New IP address of the host")
    update_parser.add_argument('--port', type=int, help="New SSH port")
    update_parser.add_argument('--ssh_key', help="New path to the SSH key")
    update_parser.add_argument('--username', help="New username for the SSH connection")
    update_parser.add_argument('--password', help="New password for the SSH connection")

    # Execute command
    execute_parser = subparsers.add_parser('execute')
    execute_parser.add_argument('command', help="Command to execute on hosts")
    execute_parser.add_argument('--hosts', help="Comma-separated names of specific hosts to run on (default is all)", default=None)

    args = parser.parse_args()
    console = Console()

    lancnc = LanCNC(debug=args.debug)

    if args.action == 'register':
        connection = HostConnection(ip=args.ip, port=args.port, ssh_key=args.ssh_key, username=args.username, password=args.password)
        host = Host(name=args.name, connection=connection)
        lancnc.config.register_host(host)
        console.print(f"[green]Registered host {args.name}")

    elif args.action == 'delete':
        lancnc.config.delete_host(args.name)
        console.print(f"[green]Deleted host {args.name}")

    elif args.action == 'update':
        connection_data = {
            "ip": args.ip,
            "port": args.port,
            "ssh_key": args.ssh_key,
            "username": args.username,
            "password": args.password,
        }
        connection_data = {key: value for key, value in connection_data.items() if value is not None}
        connection = HostConnection(**connection_data)
        host = Host(name=args.name, connection=connection)
        lancnc.config.update_host(args.name, host)
        console.print(f"[green]Updated host {args.name}")

    elif args.action == 'execute':
        specific_hosts = args.hosts.split(',') if args.hosts else None
        response = asyncio.run(lancnc.run_commands_on_hosts(args.command, specific_hosts))
        console.print(response)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
