# Telegram Search MCP Server

Read-only MCP server for searching Telegram chats, groups, and channels. Integrates with Claude Code and other MCP-compatible clients.

## Features

- **Message Search** — search by keyword within specific chats
- **Global Search** — search across all chats with optional media filters
- **Chat Management** — list dialogs with metadata
- **Chat History** — retrieve recent messages with pagination
- **Chat Info** — get metadata about users, groups, channels
- **Message Context** — get surrounding messages around a specific message

## Requirements

- Python 3.10+ (3.12+ recommended)
- Telegram API credentials from [my.telegram.org](https://my.telegram.org/)

## Installation

```bash
# Clone and install
git clone https://github.com/Neanderthal/telegram-search.git
cd telegram-search

# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

## Setup

### 1. Set environment variables

```bash
export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"
export TELEGRAM_PHONE="+1234567890"

# Optional: custom session file path (default: ~/.telegram-search/session)
export TELEGRAM_SESSION_PATH="/path/to/session"
```

### 2. Create a Telegram session

```bash
python create_session.py
```

Follow the prompts to authenticate. A `.session` file will be created at the configured path.

### 3. Run the server

```bash
# Via installed entry point
telegram-search

# Or directly
python -m telegram_search.server
```

## Claude Code / MCP Client Configuration

Add to your MCP client config:

```json
{
  "mcpServers": {
    "telegram-search": {
      "command": "telegram-search",
      "env": {
        "TELEGRAM_API_ID": "your_api_id",
        "TELEGRAM_API_HASH": "your_api_hash",
        "TELEGRAM_PHONE": "+1234567890",
        "TELEGRAM_SESSION_PATH": "/path/to/session"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `list_dialogs` | List all chats, groups, and channels |
| `search_messages` | Search messages in a specific chat by keyword |
| `search_global` | Search across all chats globally |
| `get_chat_history` | Get recent messages from a chat |
| `get_chat_info` | Get metadata about a chat/group/channel |
| `get_message_context` | Get messages around a specific message ID |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_API_ID` | Yes | — | Telegram API ID from my.telegram.org |
| `TELEGRAM_API_HASH` | Yes | — | Telegram API hash |
| `TELEGRAM_PHONE` | Yes | — | Phone number for the Telegram account |
| `TELEGRAM_SESSION_PATH` | No | `~/.telegram-search/session` | Path to session file (without `.session` extension) |

## Project Structure

```
telegram-search/
├── pyproject.toml
├── src/
│   └── telegram_search/
│       ├── __init__.py        # Package version
│       ├── config.py          # Environment variable configuration
│       ├── client.py          # Lazy Telegram client management
│       ├── helpers.py         # Message formatting and utilities
│       └── server.py          # MCP server, tools, and entry point
├── create_session.py          # One-time session creation script
└── README.md
```

## License

MIT
