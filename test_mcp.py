#!/usr/bin/env python3

"""
Simple test to check if MCP server works
"""

from mcp.server import FastMCP

# Create a simple server
test_server = FastMCP("test_server")

@test_server.tool
def hello_world(name: str = "World") -> str:
    """Say hello to someone"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print("Starting MCP server...")
    test_server.run(transport="stdio")
