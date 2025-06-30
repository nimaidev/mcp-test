#!/usr/bin/env python3
"""
Simple MCP Server with HTTP Transport and External JWT Authentication
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
import aiohttp
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    ListToolsResult,
)
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx

# Configuration
AUTH_SERVICE_URL = "http://localhost:8080/validate-token"
SERVER_NAME = "add-number-server"
HTTP_PORT = 3000

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticatedMCPServer:
    """MCP Server with external JWT authentication over HTTP"""
    
    def __init__(self):
        self.server = Server(SERVER_NAME)
        self.current_user = None
        self.setup_handlers()
    
    async def validate_token_with_auth_service(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate token with external auth service"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                
                response = await client.post(AUTH_SERVICE_URL, headers=headers)
                
                if response.status_code == 200:
                    auth_data = response.json()
                    logger.info(f"Token validated successfully for user: {auth_data.get('username')}")
                    return auth_data
                else:
                    logger.error(f"Token validation failed with status: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error validating token with auth service: {e}")
            return None
    
    async def authenticate_request(self, token: str) -> bool:
        """Authenticate incoming request and set current user"""
        if not token:
            logger.warning("No token provided in request")
            return False
        
        auth_data = await self.validate_token_with_auth_service(token)
        
        if auth_data:
            self.current_user = {
                "username": auth_data.get("username"),
                "user_id": auth_data.get("user_id"),
                "permissions": auth_data.get("permissions", []),
                "authenticated_at": datetime.utcnow().isoformat()
            }
            return True
        
        self.current_user = None
        return False
    
    def log_user_activity(self, tool_name: str, arguments: Dict[str, Any], result: Any = None):
        """Log user activity with username from auth service"""
        if not self.current_user:
            logger.warning(f"Tool '{tool_name}' called without authentication")
            return
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "username": self.current_user["username"],
            "user_id": self.current_user["user_id"],
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
            "server": SERVER_NAME
        }
        
        logger.info(f"USER_ACTIVITY: {json.dumps(log_entry)}")
    
    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="add_numbers",
                        description="Add two numbers together (requires authentication)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "auth_token": {
                                    "type": "string",
                                    "description": "JWT authentication token"
                                },
                                "a": {
                                    "type": "number", 
                                    "description": "First number"
                                },
                                "b": {
                                    "type": "number",
                                    "description": "Second number"
                                }
                            },
                            "required": ["auth_token", "a", "b"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls with authentication"""
            
            # Extract auth token from arguments
            auth_token = arguments.get("auth_token")
            
            # Authenticate the request
            is_authenticated = await self.authenticate_request(auth_token)
            
            if not is_authenticated:
                error_msg = "Authentication failed. Invalid or expired token."
                self.log_user_activity(name, arguments, {"error": error_msg})
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({
                        "error": error_msg,
                        "success": False
                    }, indent=2))]
                )
            
            # Handle add_numbers tool
            if name == "add_numbers":
                return await self.handle_add_numbers(arguments)
            else:
                error_msg = f"Unknown tool: {name}"
                self.log_user_activity(name, arguments, {"error": error_msg})
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({
                        "error": error_msg,
                        "success": False
                    }, indent=2))]
                )
    
    async def handle_add_numbers(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle add numbers tool"""
        try:
            a = args.get("a")
            b = args.get("b")
            result = a + b
            
            response = {
                "success": True,
                "operation": "addition",
                "operands": [a, b],
                "result": result,
                "performed_by": self.current_user["username"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Log the activity
            self.log_user_activity("add_numbers", args, response)
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(response, indent=2))]
            )
        
        except Exception as e:
            error_msg = f"Error in add_numbers: {str(e)}"
            self.log_user_activity("add_numbers", args, {"error": error_msg})
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "error": error_msg,
                    "success": False
                }, indent=2))]
            )

# HTTP Server setup
app = FastAPI(title="MCP Add Numbers Server")
mcp_server = AuthenticatedMCPServer()

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Handle MCP requests over HTTP with streaming"""
    
    async def generate_response():
        try:
            # Read the request body
            body = await request.body()
            request_data = json.loads(body)
            
            # Process MCP request
            if request_data.get("method") == "tools/list":
                tools_result = await mcp_server.server._list_tools_handler()
                response = {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "result": tools_result.model_dump()
                }
                yield json.dumps(response) + "\n"
                
            elif request_data.get("method") == "tools/call":
                params = request_data.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                call_result = await mcp_server.server._call_tool_handler(tool_name, arguments)
                response = {
                    "jsonrpc": "2.0", 
                    "id": request_data.get("id"),
                    "result": call_result.model_dump()
                }
                yield json.dumps(response) + "\n"
            
            else:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "error": {
                        "code": -32601,
                        "message": "Method not found"
                    }
                }
                yield json.dumps(error_response) + "\n"
                
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request_data.get("id", None),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            yield json.dumps(error_response) + "\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache"}
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "server": SERVER_NAME}

@app.get("/")
async def root():
    """Root endpoint with server info"""
    return {
        "name": SERVER_NAME,
        "description": "MCP Server with JWT Authentication",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health"
        },
        "tools": ["add_numbers"]
    }

async def main():
    """Main function to run the HTTP server"""
    logger.info(f"Starting {SERVER_NAME} on port {HTTP_PORT}")
    
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=HTTP_PORT,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())


# Example client request to /mcp endpoint:
"""
POST /mcp
Content-Type: application/json

{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "add_numbers",
        "arguments": {
            "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "a": 10,
            "b": 5
        }
    }
}
"""