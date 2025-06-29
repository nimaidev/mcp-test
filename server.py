
# main.py
import asyncio
from typing import Any

from dotenv import load_dotenv
import httpx
from mcp.server import FastMCP



load_dotenv(override=True)


iqnext_mcp = FastMCP()
    
@iqnext_mcp.tool(name="get_cloud_version")
async def get_iqnext_cloud_version() -> Any | None:
    """
        This method will call a api to get the IQNext Cloud Version
    """
    response =  httpx.get("https://faraday.iqnext.io/api/iqnext/v1/nc/about")    
    res = response.json()
    if res:
        return res.get("success").get("data")


if __name__ == "__main__":
    iqnext_mcp.run(transport="stdio")
