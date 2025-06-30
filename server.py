# main.py
import asyncio
from typing import Any

from dotenv import load_dotenv
import httpx
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

load_dotenv(override=True)

iqnext_mcp = Server("iqnext_mcp")

@iqnext_mcp.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_energy_consumption_or_cost",
            description="Get Energy consumption for specific period of time as per the user request",
            inputSchema={
                "type": "object",
                "properties": {
                    "startDate": {
                        "type": "string",
                        "description": "A date with YYYY-MM-DD format"
                    },
                    "endDate": {
                        "type": "string",
                        "description": "A date with YYYY-MM-DD format"
                    },
                }
            }
        ),
        types.Tool(
            name="get_iqnext_cloud_version",
            description="Get the IQNext Cloud version information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
    
@iqnext_mcp.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    if name == "get_iqnext_cloud_version":
        response = httpx.get("https://faraday.iqnext.io/api/iqnext/v1/nc/about")    
        res = response.json()
        if res:
            data = res.get("success").get("data")
            return [types.TextContent(type="text", text=str(data))]
        return [types.TextContent(type="text", text="Failed to get cloud version")]
    
    elif name == "get_energy_consumption_or_cost":
        start_date = arguments.get("startDate", "")
        end_date = arguments.get("endDate", "")
        try:
            print(f"Input DTO : {start_date} : {end_date}")
            result = f"Energy consumption from {start_date} to {end_date} is 200kWh"
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Failed to get energy data: {str(e)}")]
    
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Run the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await iqnext_mcp.run(
            read_stream, 
            write_stream, 
            iqnext_mcp.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())