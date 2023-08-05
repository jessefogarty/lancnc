import json
import yaml
from pathlib import Path
from cryptography.fernet import Fernet
from models import Host, Config
from typing import Optional


class ConfigManager:
    CONFIG_DIR = Path("~/.config/lancnc").expanduser()
    CONFIG_FILE = CONFIG_DIR / "config.yaml"
    ERROR_LOG_FILE = CONFIG_DIR / "error.log"
    OUTPUT_LOG_FILE = CONFIG_DIR / "output.log"

    def __init__(self):
        self.config = self._load_config()

    @classmethod
    def _load_config(cls) -> Optional[Config]:
        if cls.CONFIG_FILE.exists():
            with open(cls.CONFIG_FILE, "r") as file:
                data = yaml.safe_load(file)
                if data:
                    return Config(**data)
        return None

    @classmethod
    def _save_config(cls, config: Config):
        with open(cls.CONFIG_FILE, "w") as file:
            yaml.dump(config.model_dump(), file)

    @classmethod
    def create(cls) -> "ConfigManager":
        config_dir = cls.CONFIG_DIR
        config_file = cls.CONFIG_FILE
        error_log = cls.ERROR_LOG_FILE
        output_log = cls.OUTPUT_LOG_FILE
        secret_key = Fernet.generate_key().decode()

        # Ensure the config directory exists
        config_dir.mkdir(parents=True, exist_ok=True)

        # Create log files if they do not exist
        error_log.touch(exist_ok=True)
        output_log.touch(exist_ok=True)

        # Create default configuration
        config = Config(
            hosts=[],
            secret_key=secret_key,
            error_log=str(error_log),
            output_log=str(output_log),
        )

        # Save the configuration to file
        with open(config_file, "w") as file:
            yaml.dump(config.model_dump(), file)

        return cls()

    @classmethod
    def register_host(cls, host: Host):
        config = cls._load_config()
        if config:
            config.hosts.append(host)
            cls._save_config(config)

    @classmethod
    def update_host(cls, name: str, host: Host):
        config = cls._load_config()
        if config:
            config.hosts = [host if h.name == name else h for h in config.hosts]
            cls._save_config(config)

    @classmethod
    def delete_host(cls, name: str):
        config = cls._load_config()
        if config:
            config.hosts = [h for h in config.hosts if h.name != name]
            cls._save_config(config)