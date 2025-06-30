import asyncio
from fastmcp import Client

async def main():
    async with Client(
        "http://127.0.0.1:8000/mcp/", 
        auth="<your-token>",
    ) as client:
        res = await client.ping()
        print(res)
        
asyncio.run(main())