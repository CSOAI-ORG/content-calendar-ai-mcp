#!/usr/bin/env python3
"""MEOK AI Labs — content-calendar-ai-mcp MCP Server. Content planning, scheduling, and calendar management."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any
import uuid
import sys, os

sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
import mcp.types as types

from collections import defaultdict

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None


_store = {"content": [], "calendar": {}, "campaigns": []}
server = Server("content-calendar-ai-mcp")


def create_id():
    return str(uuid.uuid4())[:8]


PLATFORMS = [
    "linkedin",
    "twitter",
    "instagram",
    "facebook",
    "youtube",
    "tiktok",
    "blog",
    "newsletter",
]
CONTENT_TYPES = [
    "post",
    "article",
    "video",
    "infographic",
    "thread",
    "poll",
    "announcement",
]


@server.list_resources()
async def handle_list_resources():
    return [
        Resource(
            uri="content://calendar",
            name="Content Calendar",
            mimeType="application/json",
        ),
        Resource(
            uri="content::campaigns", name="Campaigns", mimeType="application/json"
        ),
    ]


@server.list_tools()
async def handle_list_tools():
    return [
        Tool(
            name="schedule_content",
            description="Schedule content for publishing",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "platform": {"type": "string", "enum": PLATFORMS},
                    "content_type": {"type": "string", "enum": CONTENT_TYPES},
                    "publish_date": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["draft", "scheduled", "published"],
                    },
                    "api_key": {"type": "string"},
                },
            },
        ),
        Tool(
            name="get_calendar",
            description="Get content calendar",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "platform": {"type": "string"},
                },
            },
        ),
        Tool(
            name="get_upcoming",
            description="Get upcoming content",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {"type": "number"},
                    "platform": {"type": "string"},
                },
            },
        ),
        Tool(
            name="update_content",
            description="Update scheduled content",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_id": {"type": "string"},
                    "updates": {"type": "object"},
                },
            },
        ),
        Tool(
            name="delete_content",
            description="Delete scheduled content",
            inputSchema={
                "type": "object",
                "properties": {"content_id": {"type": "string"}},
            },
        ),
        Tool(
            name="create_campaign",
            description="Create content campaign",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "goal": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                },
            },
        ),
        Tool(
            name="add_to_campaign",
            description="Add content to campaign",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_id": {"type": "string"},
                    "campaign_id": {"type": "string"},
                },
            },
        ),
        Tool(
            name="get_campaign_content",
            description="Get all content in campaign",
            inputSchema={
                "type": "object",
                "properties": {"campaign_id": {"type": "string"}},
            },
        ),
        Tool(
            name="get_platform_schedule",
            description="Get schedule overview by platform",
            inputSchema={
                "type": "object",
                "properties": {"platforms": {"type": "array"}},
            },
        ),
        Tool(
            name="get_content_stats",
            description="Get content statistics",
            inputSchema={"type": "object", "properties": {"days": {"type": "number"}}},
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Any = None) -> list[types.TextContent]:
    args = arguments or {}
    api_key = args.get("api_key", "")
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
                ),
            )
        ]
    err = _rl()
    if err: return [TextContent(type="text", text=err)]

    if name == "schedule_content":
        content = {
            "id": create_id(),
            "title": args["title"],
            "content": args["content"],
            "platform": args["platform"],
            "content_type": args.get("content_type", "post"),
            "publish_date": args.get("publish_date"),
            "status": args.get("status", "draft"),
            "created_at": datetime.now().isoformat(),
        }
        _store["content"].append(content)

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "scheduled": True,
                        "content_id": content["id"],
                        "title": content["title"],
                        "platform": content["platform"],
                    },
                    indent=2,
                ),
            )
        ]

    elif name == "get_calendar":
        start = args.get("start_date", datetime.now().strftime("%Y-%m-%d"))
        end = args.get(
            "end_date", (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        )
        platform = args.get("platform")

        items = _store["content"]
        if platform:
            items = [c for c in items if c.get("platform") == platform]

        items = [
            c
            for c in items
            if c.get("publish_date", "") >= start and c.get("publish_date", "") <= end
        ]
        items.sort(key=lambda x: x.get("publish_date", ""))

        return [
            TextContent(
                type="text",
                text=json.dumps({"items": items, "count": len(items)}, indent=2),
            )
        ]

    elif name == "get_upcoming":
        days = args.get("days", 7)
        platform = args.get("platform")
        cutoff = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

        items = [
            c
            for c in _store["content"]
            if c.get("publish_date", "") >= datetime.now().strftime("%Y-%m-%d")
            and c.get("publish_date", "") <= cutoff
        ]
        if platform:
            items = [c for c in items if c.get("platform") == platform]

        items.sort(key=lambda x: x.get("publish_date", ""))

        return [
            TextContent(
                type="text",
                text=json.dumps({"upcoming": items, "count": len(items)}, indent=2),
            )
        ]

    elif name == "update_content":
        content_id = args.get("content_id")
        for c in _store["content"]:
            if c["id"] == content_id:
                c.update(args.get("updates", {}))
                c["updated_at"] = datetime.now().isoformat()
                return [
                    TextContent(
                        type="text", text=json.dumps({"updated": True, "content": c})
                    )
                ]

        return [
            TextContent(type="text", text=json.dumps({"error": "Content not found"}))
        ]

    elif name == "delete_content":
        content_id = args.get("content_id")
        _store["content"] = [c for c in _store["content"] if c["id"] != content_id]

        return [TextContent(type="text", text=json.dumps({"deleted": True}))]

    elif name == "create_campaign":
        campaign = {
            "id": create_id(),
            "name": args["name"],
            "goal": args.get("goal", ""),
            "start_date": args.get("start_date"),
            "end_date": args.get("end_date"),
            "content_ids": [],
            "created_at": datetime.now().isoformat(),
        }
        _store["campaigns"].append(campaign)

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "created": True,
                        "campaign_id": campaign["id"],
                        "name": campaign["name"],
                    },
                    indent=2,
                ),
            )
        ]

    elif name == "add_to_campaign":
        content_id = args.get("content_id")
        campaign_id = args.get("campaign_id")

        for camp in _store["campaigns"]:
            if camp["id"] == campaign_id:
                if content_id not in camp["content_ids"]:
                    camp["content_ids"].append(content_id)
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"added": True, "campaign": camp["name"]}),
                    )
                ]

        return [
            TextContent(type="text", text=json.dumps({"error": "Campaign not found"}))
        ]

    elif name == "get_campaign_content":
        campaign_id = args.get("campaign_id")

        camp = next((c for c in _store["campaigns"] if c["id"] == campaign_id), None)
        if not camp:
            return [
                TextContent(
                    type="text", text=json.dumps({"error": "Campaign not found"})
                )
            ]

        content_items = [c for c in _store["content"] if c["id"] in camp["content_ids"]]

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "campaign": camp["name"],
                        "content": content_items,
                        "count": len(content_items),
                    },
                    indent=2,
                ),
            )
        ]

    elif name == "get_platform_schedule":
        platforms = args.get("platforms", PLATFORMS)

        schedule = {}
        for platform in platforms:
            items = [
                c
                for c in _store["content"]
                if c.get("platform") == platform and c.get("status") == "scheduled"
            ]
            schedule[platform] = len(items)

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"schedule": schedule, "total": sum(schedule.values())}, indent=2
                ),
            )
        ]

    elif name == "get_content_stats":
        days = args.get("days", 30)
        cutoff = datetime.now() - timedelta(days=days)

        recent = [
            c
            for c in _store["content"]
            if datetime.fromisoformat(c["created_at"]) >= cutoff
        ]

        by_platform = {}
        by_type = {}
        by_status = {}

        for c in recent:
            by_platform[c.get("platform", "unknown")] = (
                by_platform.get(c.get("platform", "unknown"), 0) + 1
            )
            by_type[c.get("content_type", "unknown")] = (
                by_type.get(c.get("content_type", "unknown"), 0) + 1
            )
            by_status[c.get("status", "unknown")] = (
                by_status.get(c.get("status", "unknown"), 0) + 1
            )

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "period_days": days,
                        "total_content": len(recent),
                        "by_platform": by_platform,
                        "by_type": by_type,
                        "by_status": by_status,
                    },
                    indent=2,
                ),
            )
        ]

    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}))]


async def main():
    async with stdio_server(server._read_stream, server._write_stream) as (
        read_stream,
        write_stream,
    ):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="content-calendar-ai-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
