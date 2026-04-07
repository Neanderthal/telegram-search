```
 _____ _           _                         _
|_   _| | __ _ ___| | __ _ _ __   __ _ _ __ | | __
  | | | |/ _` / __| |/ _` | '_ \ / _` | '_ \| |/ _` |
  | | | | (_| \__ \ | (_| | | | | (_| | | | | | (_| |
  |_| |_|\__,_|___/_|\__,_|_| |_|\__,_|_| |_|_|\__,_|
```

# Telegram Search Plugin

This project provides a robust and efficient Telegram search plugin, designed to integrate with platforms like OpenClaw or other Micro-Claw Process (MCP) systems. It enables powerful message searching within Telegram chats, offering a foundational component for various automation and data retrieval tasks.

## Features

*   **Comprehensive Search:** Search messages across Telegram chats by keywords.
*   **Session Management:** Tools for creating and managing Telegram sessions.
*   **API Integration:** Built to interface with Telegram's API via `Telethon` or similar libraries.
*   **Production Ready:** Designed with best practices for deployment in mind.

## Table of Contents

*   [Installation](#installation)
*   [Setup](#setup)
*   [Usage](#usage)
*   [Deployment for Production](#deployment-for-production)
*   [Project Structure](#project-structure)
*   [Requirements](#requirements)
*   [License](#license)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Neanderthal/telegram-search.git
cd telegram-search
```

### 2. Install dependencies

It is highly recommended to use a virtual environment.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Setup

### 1. Obtain Telegram API Credentials

You need `api_id` and `api_hash` from Telegram. Follow these steps:
1.  Go to [my.telegram.org](https://my.telegram.org/).
2.  Log in using your Telegram phone number.
3.  Click on "API Development Tools".
4.  Create a new application. You will get `api_id` and `api_hash`.

### 2. Create a Telegram Session

Run the `create_session.py` script to generate a session file for your Telegram account. This will store your session authorization securely.

```bash
python3 create_session.py
```
Follow the prompts: enter your `api_id`, `api_hash`, and phone number. A file named `telegram_session.session` will be created. Keep this file secure.

### 3. Configure the Server

The `server.py` script will likely need configuration to specify which session file to use and potentially other settings like listening address/port or database connections for search indexing (if applicable).

Example configuration (you might need to modify `server.py` or create a config file):

```python
# In server.py or a separate config.py
API_ID = 1234567 # Replace with your api_id
API_HASH = 'your_api_hash_here' # Replace with your api_hash
SESSION_NAME = 'telegram_session' # Name of the session file created by create_session.py
```

## Usage

### 1. Run the search server

Start the `server.py` script. This will likely expose an API endpoint that can be queried for Telegram messages.

```bash
python3 server.py
```

### 2. Interact with the server (e.g., via OpenClaw/MCP)

Once the server is running, you can send requests to its API endpoints to perform searches. The exact method will depend on the API implemented in `server.py`.

Example (conceptual, actual implementation in `server.py` may vary):

```python
# Example of how an MCP might interact
import requests

response = requests.post("http://localhost:5000/search", json={"query": "your search term", "chat_id": -123456789})
print(response.json())
```

## Deployment for Production

For production environments, consider the following:

*   **Containerization:** Use Docker to containerize the application for consistent environments.
*   **Process Management:** Use a process manager like `systemd`, `Supervisor`, or `pm2` to ensure the `server.py` script runs continuously and restarts automatically on failure.
*   **Environment Variables:** Store sensitive information (like `API_HASH`) as environment variables rather than directly in code.
*   **Security:** Ensure the server's API endpoints are properly secured, especially if exposed over a network.
*   **Logging:** Implement robust logging for monitoring and debugging.
*   **Scalability:** If searching a large number of chats or messages, consider adding a database for indexing and faster queries.

## Project Structure

```
.
├── create_session.py    # Script to create Telegram session file
├── requirements.txt     # Python dependencies
├── server.py            # Main search server application
└── README.md            # This file
```

## Requirements

*   Python 3.8+
*   `Telethon` library (specified in `requirements.txt`)
*   Telegram API `api_id` and `api_hash`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
