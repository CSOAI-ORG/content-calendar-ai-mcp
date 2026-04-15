#!/usr/bin/env python3
"""MEOK AI Labs — content-calendar-ai-mcp MCP Server. Content planning, scheduling, and calendar management."""

import json
from datetime import datetime, timedelta, timezone
from typing import Any
import uuid
import sys, os

sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access
from mcp.server.fastmcp import FastMCP
from collections import defaultdict

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None


_store = {"content": [], "calendar": {}, "campaigns": []}
mcp = FastMCP("content-calendar-ai", instructions="Content planning, scheduling, and calendar management.")


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


@mcp.tool()
def schedule_content(title: str, content: str, platform: str, content_type: str = "post", publish_date: str = "", status: str = "draft", api_key: str = "") -> str:
    """Schedule content for publishing"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    item = {
        "id": create_id(),
        "title": title,
        "content": content,
        "platform": platform,
        "content_type": content_type,
        "publish_date": publish_date or None,
        "status": status,
        "created_at": datetime.now().isoformat(),
    }
    _store["content"].append(item)

    return json.dumps(
        {
            "scheduled": True,
            "content_id": item["id"],
            "title": item["title"],
            "platform": item["platform"],
        },
        indent=2,
    )


@mcp.tool()
def get_calendar(start_date: str = "", end_date: str = "", platform: str = "", api_key: str = "") -> str:
    """Get content calendar"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    start = start_date or datetime.now().strftime("%Y-%m-%d")
    end = end_date or (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    items = _store["content"]
    if platform:
        items = [c for c in items if c.get("platform") == platform]

    items = [
        c
        for c in items
        if c.get("publish_date", "") >= start and c.get("publish_date", "") <= end
    ]
    items.sort(key=lambda x: x.get("publish_date", ""))

    return json.dumps({"items": items, "count": len(items)}, indent=2)


@mcp.tool()
def get_upcoming(days: int = 7, platform: str = "", api_key: str = "") -> str:
    """Get upcoming content"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

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

    return json.dumps({"upcoming": items, "count": len(items)}, indent=2)


@mcp.tool()
def update_content(content_id: str, updates: dict = None, api_key: str = "") -> str:
    """Update scheduled content"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    for c in _store["content"]:
        if c["id"] == content_id:
            c.update(updates or {})
            c["updated_at"] = datetime.now().isoformat()
            return json.dumps({"updated": True, "content": c})

    return json.dumps({"error": "Content not found"})


@mcp.tool()
def delete_content(content_id: str, api_key: str = "") -> str:
    """Delete scheduled content"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    _store["content"] = [c for c in _store["content"] if c["id"] != content_id]
    return json.dumps({"deleted": True})


@mcp.tool()
def create_campaign(name: str, goal: str = "", start_date: str = "", end_date: str = "", api_key: str = "") -> str:
    """Create content campaign"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    campaign = {
        "id": create_id(),
        "name": name,
        "goal": goal,
        "start_date": start_date or None,
        "end_date": end_date or None,
        "content_ids": [],
        "created_at": datetime.now().isoformat(),
    }
    _store["campaigns"].append(campaign)

    return json.dumps(
        {"created": True, "campaign_id": campaign["id"], "name": campaign["name"]},
        indent=2,
    )


@mcp.tool()
def add_to_campaign(content_id: str, campaign_id: str, api_key: str = "") -> str:
    """Add content to campaign"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    for camp in _store["campaigns"]:
        if camp["id"] == campaign_id:
            if content_id not in camp["content_ids"]:
                camp["content_ids"].append(content_id)
            return json.dumps({"added": True, "campaign": camp["name"]})

    return json.dumps({"error": "Campaign not found"})


@mcp.tool()
def get_campaign_content(campaign_id: str, api_key: str = "") -> str:
    """Get all content in campaign"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    camp = next((c for c in _store["campaigns"] if c["id"] == campaign_id), None)
    if not camp:
        return json.dumps({"error": "Campaign not found"})

    content_items = [c for c in _store["content"] if c["id"] in camp["content_ids"]]

    return json.dumps(
        {"campaign": camp["name"], "content": content_items, "count": len(content_items)},
        indent=2,
    )


@mcp.tool()
def get_platform_schedule(platforms: list = None, api_key: str = "") -> str:
    """Get schedule overview by platform"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    platforms_list = platforms or PLATFORMS

    schedule = {}
    for platform in platforms_list:
        items = [
            c
            for c in _store["content"]
            if c.get("platform") == platform and c.get("status") == "scheduled"
        ]
        schedule[platform] = len(items)

    return json.dumps(
        {"schedule": schedule, "total": sum(schedule.values())}, indent=2
    )


@mcp.tool()
def get_content_stats(days: int = 30, api_key: str = "") -> str:
    """Get content statistics"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

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

    return json.dumps(
        {
            "period_days": days,
            "total_content": len(recent),
            "by_platform": by_platform,
            "by_type": by_type,
            "by_status": by_status,
        },
        indent=2,
    )


if __name__ == "__main__":
    mcp.run()
