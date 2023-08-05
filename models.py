from pydantic import BaseModel, Field, root_validator, FilePath
from typing import Optional, List
from cryptography.fernet import Fernet
import os
from pathlib import Path


class HostConnection(BaseModel):
    ip: str
    ssh_key: Optional[str] = Field(default_factory=lambda: os.environ.get("SSH_KEY"))
    username: Optional[str] = Field(default_factory=lambda: os.environ.get("USER"))
    password: Optional[str] = Field(default_factory=str)

    @root_validator(pre=True)
    @classmethod
    def validate_credentials(cls, values):
        ssh_key = values.get("ssh_key")
        username = values.get("username")
        password = values.get("password")

        if ssh_key:
            return values

        if username and password:
            return values

        raise ValueError(
            "Either ssh_key must be provided or both username and password must be supplied"
        )


class Host(BaseModel):
    name: str
    connection: HostConnection
    secret_key: str

    @root_validator(pre=True)
    @classmethod
    def validate_connection_object(cls, values):
        connection = values.get("connection")
        if not isinstance(connection, HostConnection):
            raise ValueError(
                "The connection field must contain a valid HostConnection object"
            )
        return values

    @root_validator(pre=True)
    @classmethod
    def validate_secret_key_path(cls, values):
        secret_key = values.get("secret_key")
        secret_key_path = Path(secret_key)
        if not secret_key_path.exists():
            raise FileNotFoundError(
                f"The secret key file does not exist: {secret_key_path}"
            )
        return values


class Config(BaseModel):
    hosts: List[Host]
    secret_key: str
    error_log: str | FilePath
    output_log: str | FilePath
