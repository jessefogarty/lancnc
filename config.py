# config.py

"""This module defines the configuration classes for managing remote host
information. It includes the Config class to handle loading, saving, registering,
deleting, and updating host configurations.
"""

from models import Host
import yaml
import logging
from rich.logging import RichHandler
from pathlib import Path
import os
from cryptography.fernet import Fernet
import ipaddress

CONFIG_DIR: Path = Path(os.path.expanduser("~/.config/lancnc"))
CONFIG_FILE: Path = CONFIG_DIR / "config.yaml"


class Config:
    """Handles host configuration management.

    Attributes:
        logger: Logger object to handle logging.
        hosts: List of Host objects representing registered hosts.
        key_location: Path to the secret key file.
        cipher_suite: Cryptographic suite for encryption and decryption.
    """

    def __init__(self, debug=False):
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        self.logger.addHandler(RichHandler())
        self.hosts = self.load_hosts()
        self.key_location = self.load_key_location()
        self.cipher_suite = self.load_cipher_suite()

    def load_hosts(self):
        """Load hosts from the configuration file."""
        try:
            with open(CONFIG_FILE, "r") as file:
                config_data = yaml.load(file, Loader=yaml.FullLoader)
                hosts_data = config_data.get("hosts", [])
                return [Host(**host) for host in hosts_data]
        except FileNotFoundError:
            return []

    def save_hosts(self):
        """Save hosts to the configuration file."""
        if not CONFIG_DIR.exists():
            CONFIG_DIR.mkdir(parents=True)
        with open(CONFIG_FILE, "w") as file:
            yaml.dump(
                {
                    "hosts": [host.model_dump() for host in self.hosts],
                    "key_location": self.key_location,
                },
                file,
            )

    def register_host(self, host):
        """Register a new host.

        Args:
            host (Host): Host object to register.
        """
        self.hosts.append(host)
        self.save_hosts()

    def delete_host(self, name):
        """Delete a host by its name.

        Args:
            name (str): Name of the host to delete.
        """
        self.hosts = [host for host in self.hosts if host.name != name]
        self.save_hosts()

    def update_host(self, name, updated_host):
        """Update an existing host.

        Args:
            name (str): Name of the host to update.
            updated_host (Host): Updated Host object.
        """
        self.hosts = [
            updated_host if host.name == name else host for host in self.hosts
        ]
        self.save_hosts()

    def load_key_location(self):
        """Load or create the secret key location."""
        try:
            with open(CONFIG_FILE, "r") as file:
                config_data = yaml.load(file, Loader=yaml.FullLoader)
                return config_data.get("key_location", "")
        except FileNotFoundError:
            return ""

    def generate_secret_key(self):
        """Generate a new secret key and save it to a file."""
        key = Fernet.generate_key()
        key_file = CONFIG_DIR / "secret.key"
        with open(key_file, "wb") as file:
            file.write(key)
        self.key_location = str(key_file)
        self.save_hosts()

    def load_cipher_suite(self):
        """Load the cryptographic suite for encryption and decryption."""
        if not self.key_location:
            self.generate_secret_key()
        with open(self.key_location, "rb") as file:
            key = file.read()
        return Fernet(key)

    def encrypt_password(self, password):
        """Encrypt a password using the secret key.

        Args:
            password (str): Password to encrypt.

        Returns:
            str: Encrypted password.
        """
        return self.cipher_suite.encrypt(password.encode()).decode()

    def decrypt_password(self, encrypted_password):
        """Decrypt a password using the secret key.

        Args:
            encrypted_password (str): Encrypted password.

        Returns:
            str: Decrypted password.
        """
        return self.cipher_suite.decrypt(encrypted_password.encode()).decode()
