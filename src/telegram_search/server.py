"""Telegram Search MCP Server — read-only search through Telegram chats/groups."""

from __future__ import annotations

import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Optional

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import (
    Channel,
    Chat,
    InputMessagesFilterDocument,
    InputMessagesFilterGeo,
    InputMessagesFilterMusic,
    InputMessagesFilterPhotos,
    InputMessagesFilterRoundVideo,
    InputMessagesFilterUrl,
    InputMessagesFilterVideo,
    InputMessagesFilterVoice,
    User,
)

from telegram_search.client import AppContext, LazyTelegramClient
from telegram_search.helpers import _format_message, _parse_date, _resolve_entity

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("telegram-search")


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    lazy = LazyTelegramClient()
    try:
        logger.info("Telegram Search MCP server starting")
        yield AppContext(lazy_client=lazy)
    finally:
        await lazy.close()
        logger.info("Telegram Search MCP server stopped")


mcp = FastMCP("telegram-search", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_client(ctx: Context[ServerSession, AppContext]) -> TelegramClient:
    return await ctx.request_context.lifespan_context.lazy_client.get()


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_dialogs(
    limit: int = 50,
    folder: Optional[str] = None,
    ctx: Context[ServerSession, AppContext] = None,
) -> str:
    """List all chats, groups, and channels.

    Args:
        limit: Maximum number of dialogs to return (default 50).
        folder: Optional folder name to filter by (e.g. "Personal", "Work").
    """
    client = await _get_client(ctx)
    lines = []
    count = 0
    try:
        async for dialog in client.iter_dialogs():
            if count >= limit:
                break

            if folder and hasattr(dialog, "folder_id"):
                pass

            entity = dialog.entity
            if isinstance(entity, Channel):
                kind = "channel" if entity.broadcast else "group/supergroup"
            elif isinstance(entity, Chat):
                kind = "group"
            elif isinstance(entity, User):
                kind = "user"
            else:
                kind = "unknown"

            unread = dialog.unread_count
            line = "{name}  |  type: {kind}  |  id: {id}  |  unread: {unread}".format(
                name=dialog.name or "(no name)",
                kind=kind,
                id=dialog.entity.id,
                unread=unread,
            )
            lines.append(line)
            count += 1
    except FloodWaitError as e:
        return "Rate-limited by Telegram. Retry after {s} seconds.".format(s=e.seconds)

    if not lines:
        return "No dialogs found."
    return "\n".join(lines)


@mcp.tool()
async def search_messages(
    chat: str,
    query: str,
    limit: int = 20,
    from_user: Optional[str] = None,
    offset_date: Optional[str] = None,
    min_date: Optional[str] = None,
    max_date: Optional[str] = None,
    offset_id: int = 0,
    ctx: Context[ServerSession, AppContext] = None,
) -> str:
    """Search messages within a specific chat by keyword.

    Args:
        chat: Chat name, @username, or numeric ID.
        query: Search keyword or phrase.
        limit: Max messages to return (default 20).
        from_user: Filter by sender name or username.
        offset_date: ISO date — only messages before this date.
        min_date: ISO date — only messages after this date.
        max_date: ISO date — only messages before this date.
        offset_id: Message ID to paginate from (for cursor-based pagination).
    """
    client = await _get_client(ctx)

    try:
        entity = await _resolve_entity(client, chat)
    except Exception as e:
        return "Could not resolve chat '{chat}': {err}".format(chat=chat, err=e)

    from_entity = None
    if from_user:
        try:
            from_entity = await _resolve_entity(client, from_user)
        except Exception:
            return "Could not resolve from_user '{u}'.".format(u=from_user)

    parsed_offset = _parse_date(offset_date)
    parsed_min = _parse_date(min_date)
    parsed_max = _parse_date(max_date)

    messages = []
    try:
        async for msg in client.iter_messages(
            entity,
            search=query,
            limit=limit,
            offset_date=parsed_offset or parsed_max,
            offset_id=offset_id,
            from_user=from_entity,
        ):
            if parsed_min and msg.date and msg.date < parsed_min:
                break
            messages.append(msg)
    except FloodWaitError as e:
        return "Rate-limited by Telegram. Retry after {s} seconds.".format(s=e.seconds)

    if not messages:
        return "No messages found."

    blocks = []
    for msg in messages:
        blocks.append(_format_message(msg))
    blocks.append("\n[{n} messages returned, last offset_id={oid}]".format(
        n=len(messages),
        oid=messages[-1].id if messages else 0,
    ))
    return "\n---\n".join(blocks)


@mcp.tool()
async def search_global(
    query: str,
    limit: int = 20,
    filter_type: Optional[str] = None,
    ctx: Context[ServerSession, AppContext] = None,
) -> str:
    """Search messages across all chats globally.

    Args:
        query: Search keyword or phrase.
        limit: Max messages to return (default 20).
        filter_type: Optional filter — one of: photos, documents, links, music, video, voice, round_video, geo.
    """
    client = await _get_client(ctx)

    filter_map = {
        "photos": InputMessagesFilterPhotos(),
        "documents": InputMessagesFilterDocument(),
        "links": InputMessagesFilterUrl(),
        "music": InputMessagesFilterMusic(),
        "video": InputMessagesFilterVideo(),
        "voice": InputMessagesFilterVoice(),
        "round_video": InputMessagesFilterRoundVideo(),
        "geo": InputMessagesFilterGeo(),
    }

    msg_filter = None
    if filter_type:
        msg_filter = filter_map.get(filter_type.lower())
        if msg_filter is None:
            return "Unknown filter_type '{ft}'. Choose from: {opts}".format(
                ft=filter_type,
                opts=", ".join(sorted(filter_map.keys())),
            )

    messages = []
    try:
        kwargs = dict(entity=None, search=query, limit=limit)
        if msg_filter is not None:
            kwargs["filter"] = msg_filter
        async for msg in client.iter_messages(**kwargs):
            messages.append(msg)
    except FloodWaitError as e:
        return "Rate-limited by Telegram. Retry after {s} seconds.".format(s=e.seconds)

    if not messages:
        return "No messages found."

    blocks = []
    for msg in messages:
        chat_name = ""
        if msg.chat:
            chat_name = getattr(msg.chat, "title", None) or getattr(msg.chat, "first_name", None) or str(msg.chat_id)
        header = "[in: {chat}] ".format(chat=chat_name) if chat_name else ""
        blocks.append(header + _format_message(msg))
    blocks.append("\n[{n} messages returned]".format(n=len(messages)))
    return "\n---\n".join(blocks)


@mcp.tool()
async def get_chat_history(
    chat: str,
    limit: int = 50,
    offset_date: Optional[str] = None,
    offset_id: int = 0,
    ctx: Context[ServerSession, AppContext] = None,
) -> str:
    """Get recent messages from a chat.

    Args:
        chat: Chat name, @username, or numeric ID.
        limit: Max messages to return (default 50).
        offset_date: ISO date — only messages before this date.
        offset_id: Message ID to paginate from (for cursor-based pagination).
    """
    client = await _get_client(ctx)

    try:
        entity = await _resolve_entity(client, chat)
    except Exception as e:
        return "Could not resolve chat '{chat}': {err}".format(chat=chat, err=e)

    parsed_offset = _parse_date(offset_date)

    messages = []
    try:
        async for msg in client.iter_messages(
            entity,
            limit=limit,
            offset_date=parsed_offset,
            offset_id=offset_id,
        ):
            messages.append(msg)
    except FloodWaitError as e:
        return "Rate-limited by Telegram. Retry after {s} seconds.".format(s=e.seconds)

    if not messages:
        return "No messages found."

    blocks = [_format_message(msg) for msg in messages]
    blocks.append("\n[{n} messages returned, last offset_id={oid}]".format(
        n=len(messages),
        oid=messages[-1].id if messages else 0,
    ))
    return "\n---\n".join(blocks)


@mcp.tool()
async def get_chat_info(
    chat: str,
    ctx: Context[ServerSession, AppContext] = None,
) -> str:
    """Get metadata about a chat, group, or channel.

    Args:
        chat: Chat name, @username, or numeric ID.
    """
    client = await _get_client(ctx)

    try:
        entity = await _resolve_entity(client, chat)
    except Exception as e:
        return "Could not resolve chat '{chat}': {err}".format(chat=chat, err=e)

    lines = []

    if isinstance(entity, User):
        lines.append("Type: User")
        lines.append("ID: {id}".format(id=entity.id))
        name = " ".join(p for p in [entity.first_name, entity.last_name] if p)
        lines.append("Name: {name}".format(name=name or "(none)"))
        if entity.username:
            lines.append("Username: @{u}".format(u=entity.username))
        if entity.phone:
            lines.append("Phone: {p}".format(p=entity.phone))
        lines.append("Bot: {b}".format(b=entity.bot))
    elif isinstance(entity, Channel):
        kind = "Channel (broadcast)" if entity.broadcast else "Supergroup"
        lines.append("Type: {k}".format(k=kind))
        lines.append("ID: {id}".format(id=entity.id))
        lines.append("Title: {t}".format(t=entity.title))
        if entity.username:
            lines.append("Username: @{u}".format(u=entity.username))
        if hasattr(entity, "participants_count") and entity.participants_count:
            lines.append("Members: {m}".format(m=entity.participants_count))
        lines.append("Restricted: {r}".format(r=entity.restricted))
        if entity.date:
            lines.append("Created: {d}".format(d=entity.date.strftime("%Y-%m-%d")))
    elif isinstance(entity, Chat):
        lines.append("Type: Group")
        lines.append("ID: {id}".format(id=entity.id))
        lines.append("Title: {t}".format(t=entity.title))
        if entity.participants_count:
            lines.append("Members: {m}".format(m=entity.participants_count))
        if entity.date:
            lines.append("Created: {d}".format(d=entity.date.strftime("%Y-%m-%d")))
    else:
        lines.append("Type: {t}".format(t=type(entity).__name__))
        lines.append("ID: {id}".format(id=getattr(entity, "id", "unknown")))

    return "\n".join(lines)


@mcp.tool()
async def get_message_context(
    chat: str,
    message_id: int,
    context_size: int = 5,
    ctx: Context[ServerSession, AppContext] = None,
) -> str:
    """Get messages around a specific message ID for context.

    Args:
        chat: Chat name, @username, or numeric ID.
        message_id: The target message ID to get context around.
        context_size: Number of messages before and after the target (default 5).
    """
    client = await _get_client(ctx)

    try:
        entity = await _resolve_entity(client, chat)
    except Exception as e:
        return "Could not resolve chat '{chat}': {err}".format(chat=chat, err=e)

    after_msgs = []
    try:
        async for msg in client.iter_messages(
            entity,
            min_id=message_id,
            limit=context_size,
        ):
            after_msgs.append(msg)
    except FloodWaitError as e:
        return "Rate-limited by Telegram. Retry after {s} seconds.".format(s=e.seconds)

    before_msgs = []
    try:
        async for msg in client.iter_messages(
            entity,
            offset_id=message_id + 1,
            limit=context_size + 1,
        ):
            before_msgs.append(msg)
    except FloodWaitError as e:
        return "Rate-limited by Telegram. Retry after {s} seconds.".format(s=e.seconds)

    all_msgs = list(reversed(after_msgs)) + before_msgs
    seen = set()
    unique = []
    for m in all_msgs:
        if m.id not in seen:
            seen.add(m.id)
            unique.append(m)
    unique.sort(key=lambda m: m.id)

    if not unique:
        return "No messages found around message ID {mid}.".format(mid=message_id)

    blocks = []
    for msg in unique:
        marker = " <<< TARGET" if msg.id == message_id else ""
        blocks.append(_format_message(msg) + marker)
    return "\n---\n".join(blocks)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Entry point for the telegram-search MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
