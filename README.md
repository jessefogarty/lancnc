# LanCNC

LanCNC is a command-line tool that allows users to manage and execute commands on remote hosts within a local area network (LAN) using SSH. It includes a user-friendly interface for registering, updating, deleting, and executing commands on one or many remote hosts.

## Features

- **Host Management**: Easily register, update, delete, and list remote hosts with SSH connection details.
- **Command Execution**: Execute shell commands on one or all registered hosts asynchronously.
- **Colorful Output**: Utilizes the rich Python library to provide colorful and user-friendly output.
- **Secure Password Handling**: Encrypts and decrypts passwords using a secret key.
- **Logging**: Supports both standard and debug logging levels.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/jessefogarty/lancnc.git
   ```

2. Navigate to the project directory:
   ```
   cd lancnc
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Register a Host

```
./cli.py register <name> <ip> [--port] [--ssh_key] [--username] [--password]
```

### Delete a Host

```
./cli.py delete <name>
```

### Update a Host

```
./cli.py update <name> [--ip] [--port] [--ssh_key] [--username] [--password]
```

### Execute a Command

```
./cli.py execute <command> [--hosts]
```

## Testing

A test script (`test_lancnc.py`) is included in the repository to validate the functionality. Run the test using:

```
python test_lancnc.py
```

## Contributing

Please feel free to open an issue or submit a pull request with any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
