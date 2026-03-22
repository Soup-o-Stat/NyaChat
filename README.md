# NyaChat :3

**NyaChat** is a simple terminal-based chat application built with Python. It allows multiple users to connect to a server, exchange messages in real-time, and optionally use a server password for security. The client features sound notifications for incoming messages and supports nickname customization

## Features

* Connect multiple clients to a single server
* Optional server password protection
* Customizable nickname for each client
* Real-time message broadcasting
* Display list of online users (`/list` command)
* Exit cleanly with `/exit`
* Sound notifications for new messages
* Easy configuration using a `config.json` file

## Requirements

* Python 3.8+
* `prompt_toolkit` library (for enhanced input handling)
* Windows only (for `winsound` notifications)

Install dependencies using pip:

```bash
pip install prompt_toolkit
```

## Files

* `server.py` – The server script. Handles multiple clients, broadcasting messages, and optional password protection
* `nyachat.py` – The client script. Connects to the server, sends/receives messages, and plays notification sounds
* `config.json` – Client configuration file (created automatically if missing)
* `sounds/received.wav` – Notification sound for incoming messages

## Usage

### Server

1. Run the server script:

```bash
python server.py
```

2. Follow the menu:

```
=== Server Menu ===
1 - Start server
2 - Set password
0 - Exit
```

3. Clients can now connect to the server using its IP and port `1234`

### Client

1. Run the client script:

```bash
python nyachat.py
```

2. Main menu:

```
=== NyaChat ===
1 - Connect
2 - Settings
0 - Exit
```

3. Before connecting, set your IP, nickname, and optional password in the **Settings** menu
4. Use `/exit` to disconnect from the server
5. Use `/list` to see all online users
6. Use `/help` to see available commands

## Configuration (`config.json`)

The client stores settings in `config.json`. Example:

```json
{
    "ip": "192.168.1.10",
    "nickname": "Alice",
    "password": "mypassword"
}
```

* `ip` – Server IP address
* `nickname` – Your chat nickname
* `password` – Server password (if required)

