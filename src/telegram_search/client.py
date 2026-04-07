"""Telegram client with lazy connection management."""

from __future__ import annotations

import logging
import os
import shutil
import tempfile
from dataclasses import dataclass
from typing import Optional

from telethon import TelegramClient

from telegram_search.config import API_HASH, API_ID, PHONE, SESSION_PATH

logger = logging.getLogger("telegram-search")


class LazyTelegramClient:
    """Connects to Telegram lazily on first use so MCP init is instant."""

    def __init__(self) -> None:
        self._client: Optional[TelegramClient] = None
        self._tmp_dir: Optional[str] = None

    async def get(self) -> TelegramClient:
        if self._client is None:
            logger.info("Connecting to Telegram...")
            session_path = self._copy_session()
            self._client = TelegramClient(session_path, API_ID, API_HASH)
            await self._client.start(phone=PHONE)
            logger.info("Connected to Telegram")
        return self._client

    def _copy_session(self) -> str:
        master = SESSION_PATH + ".session"
        if not os.path.exists(master):
            return SESSION_PATH
        self._tmp_dir = tempfile.mkdtemp(prefix="tg-mcp-")
        tmp_session = os.path.join(self._tmp_dir, "telegram_session")
        shutil.copy2(master, tmp_session + ".session")
        return tmp_session

    async def close(self) -> None:
        if self._client is not None:
            await self._client.disconnect()
            logger.info("Disconnected from Telegram")
        if self._tmp_dir is not None:
            shutil.rmtree(self._tmp_dir, ignore_errors=True)


@dataclass
class AppContext:
    lazy_client: LazyTelegramClient
