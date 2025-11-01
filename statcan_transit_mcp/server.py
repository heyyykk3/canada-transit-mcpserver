#!/usr/bin/env python3
"""
MCP Server for Statistics Canada LODE Dataset - Canadian Public Transit Network Database
"""

import asyncio
import json
from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp import types

STATCAN_BASE_URL = "https://www150.statcan.gc.ca/n1/pub/23-26-0003/232600032025001-eng.htm"

app = Server("statcan-transit-mcp")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="get_dataset_info",
            description="Get information about the Canadian Public Transit Network Database",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="search_transit_agencies",
            description="Search for transit agencies",
            inputSchema={
                "type": "object",
                "properties": {
                    "province": {"type": "string", "description": "Province code (e.g., ON, QC)"},
                    "city": {"type": "string", "description": "City name"},
                },
            },
        ),
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Handle tool execution."""
    if name == "get_dataset_info":
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "dataset": "Canadian Public Transit Network Database",
                "source": "Statistics Canada",
                "url": STATCAN_BASE_URL,
                "coverage": "150 transit agencies across Canada",
            }, indent=2)
        )]
    elif name == "search_transit_agencies":
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "note": "Placeholder data - integrate real GTFS data",
                "example": [
                    {"id": "ttc", "name": "Toronto Transit Commission", "province": "ON"},
                    {"id": "stm", "name": "STM Montreal", "province": "QC"},
                ]
            }, indent=2)
        )]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="statcan-transit-mcp",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())

