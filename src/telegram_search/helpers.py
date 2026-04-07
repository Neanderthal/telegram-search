"""Formatting and utility helpers for Telegram messages."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from telethon import TelegramClient
from telethon.tl.types import (
    Channel,
    Chat,
    Document,
    MessageMediaDocument,
    MessageMediaGeo,
    MessageMediaPhoto,
    MessageMediaWebPage,
    User,
)


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    """Parse an ISO-8601 date string into a timezone-aware datetime."""
    if not value:
        return None
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _media_indicator(message) -> str:
    """Return a short text tag describing attached media."""
    media = message.media
    if media is None:
        return ""
    if isinstance(media, MessageMediaPhoto):
        return "\n[media: photo]"
    if isinstance(media, MessageMediaDocument):
        doc = media.document
        if isinstance(doc, Document):
            for attr in doc.attributes:
                type_name = type(attr).__name__
                if "Audio" in type_name or "Voice" in type_name:
                    return "\n[media: audio/voice]"
                if "Video" in type_name:
                    return "\n[media: video]"
                if "Sticker" in type_name:
                    return "\n[media: sticker]"
            return "\n[media: document]"
        return "\n[media: document]"
    if isinstance(media, MessageMediaWebPage):
        return "\n[media: link preview]"
    if isinstance(media, MessageMediaGeo):
        return "\n[media: location]"
    return "\n[media: other]"


def _format_message(msg) -> str:
    """Format a single Telethon Message into a readable text block."""
    date_str = msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else "unknown date"

    sender = msg.sender
    if sender is None:
        sender_name = "Unknown"
    elif isinstance(sender, User):
        parts = [sender.first_name or "", sender.last_name or ""]
        sender_name = " ".join(p for p in parts if p) or sender.username or str(sender.id)
    elif isinstance(sender, (Chat, Channel)):
        sender_name = sender.title or str(sender.id)
    else:
        sender_name = str(getattr(sender, "id", "Unknown"))

    text = msg.text or ""
    media = _media_indicator(msg)

    return "[{date}] {sender}:\n{text}{media}".format(
        date=date_str,
        sender=sender_name,
        text=text,
        media=media,
    )


async def _resolve_entity(client: TelegramClient, chat: str):
    """Resolve a chat identifier (name, username, or numeric ID) to an entity."""
    try:
        numeric = int(chat)
        return await client.get_entity(numeric)
    except (ValueError, TypeError):
        pass

    return await client.get_entity(chat)
