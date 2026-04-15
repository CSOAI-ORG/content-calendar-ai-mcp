# Content Calendar AI MCP Server

> By [MEOK AI Labs](https://meok.ai) — Content planning, scheduling, and calendar management across platforms

## Installation

```bash
pip install content-calendar-ai-mcp
```

## Usage

```bash
python server.py
```

## Tools

### `schedule_content`
Schedule content for publishing on a platform.

**Parameters:**
- `title` (str): Content title
- `content` (str): Content body
- `platform` (str): Target platform (linkedin, twitter, instagram, facebook, youtube, tiktok, blog, newsletter)
- `content_type` (str): Content type (post, article, video, infographic, thread, poll, announcement)
- `publish_date` (str): Publish date
- `status` (str): Status (default 'draft')

### `get_calendar`
Get content calendar for a date range with optional platform filter.

**Parameters:**
- `start_date` (str): Start date
- `end_date` (str): End date
- `platform` (str): Platform filter

### `get_upcoming`
Get upcoming content for the next N days.

**Parameters:**
- `days` (int): Days ahead (default 7)
- `platform` (str): Platform filter

### `update_content`
Update scheduled content.

**Parameters:**
- `content_id` (str): Content identifier
- `updates` (dict): Fields to update

### `delete_content`
Delete scheduled content.

**Parameters:**
- `content_id` (str): Content identifier

### `create_campaign`
Create a content campaign with goals and timeline.

**Parameters:**
- `name` (str): Campaign name
- `goal` (str): Campaign goal
- `start_date` (str): Start date
- `end_date` (str): End date

### `add_to_campaign`
Add content to a campaign.

**Parameters:**
- `content_id` (str): Content identifier
- `campaign_id` (str): Campaign identifier

### `get_campaign_content`
Get all content in a campaign.

**Parameters:**
- `campaign_id` (str): Campaign identifier

### `get_platform_schedule`
Get schedule overview by platform.

**Parameters:**
- `platforms` (list): Platforms to include

### `get_content_stats`
Get content statistics for a period.

**Parameters:**
- `days` (int): Period in days (default 30)

## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
