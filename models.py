from pydantic import BaseModel, validator, ConfigDict
from typing import Optional
import os


class HostConfig(BaseModel):
    """Defines the structure of individual host configurations."""

    name: str
    host: str
    username: str
    ssh_key: str | None = None
    password: str | None = None
    secret_key: str | None = None


class HostConnection(BaseModel):
    ip: str
    port: int = 22
    ssh_key: Optional[str]
    username: str = os.getlogin()
    password: Optional[str] = None

    @validator("ssh_key", pre=True, always=True)
    def validate_ssh_key(cls, value: Optional[str]) -> Optional[str]:
        if value:
            return os.path.expanduser(os.path.expandvars(value))
        return value


class Host(BaseModel):
    """A model representing a Host configuration.
    properties: name, connection* (*validated)
    """

    name: str
    connection: HostConnection

    @validator("connection", pre=True, always=True)
    def validate_connection(cls, value: HostConnection) -> HostConnection:
        if not (value.ssh_key or value.password):
            raise ValueError(
                "Either ssh_key or password must be provided for the host connection."
            )
        return value


class HostResponse(BaseModel):
    """A model representing the response from a command run on a Host.
    properties: host, response, status_code
    """

    host: str
    response: bytes | str | None
    status_code: int | None
