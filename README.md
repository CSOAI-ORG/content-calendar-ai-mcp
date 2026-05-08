<div align="center">

# Content Calendar Ai MCP

**MCP server for content calendar ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-content-calendar-ai-mcp)](https://pypi.org/project/meok-content-calendar-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Content Calendar Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `schedule_content` | Schedule content for publishing |
| `get_calendar` | Get content calendar |
| `get_upcoming` | Get upcoming content |
| `update_content` | Update scheduled content |
| `delete_content` | Delete scheduled content |
| `create_campaign` | Create content campaign |
| `add_to_campaign` | Add content to campaign |
| `get_campaign_content` | Get all content in campaign |
| `get_platform_schedule` | Get schedule overview by platform |
| `get_content_stats` | Get content statistics |

## Installation

```bash
pip install meok-content-calendar-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "content-calendar-ai": {
      "command": "python",
      "args": ["-m", "meok_content_calendar_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 10 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
