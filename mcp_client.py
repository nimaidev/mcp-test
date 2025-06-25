#!/usr/bin/env python3
"""
MCP Math Client

A simple client to interact with the MCP math server.
This client can discover and use mathematical tools provided by the server.
"""

import asyncio
import json
from typing import Dict, Any, List
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


class MCPMathClient:
    """Client for connecting to and using the MCP math server."""
    
    def __init__(self, command: str = "uv", args: List[str] = None):
        """Initialize the MCP client.
        
        Args:
            command: Command to start the MCP server
            args: Arguments for the server command
        """
        self.server_params = StdioServerParameters(
            command=command,
            args=args or ["run", "maths.py"]
        )
        self.available_tools = {}
    
    async def connect_and_discover(self):
        """Connect to the server and discover available tools."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List available tools
                tools_result = await session.list_tools()
                self.available_tools = {
                    tool.name: tool for tool in tools_result.tools
                }
                
                print(f"Connected to MCP math server!")
                print(f"Available tools: {list(self.available_tools.keys())}")
                return session
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool with given arguments.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            The result from the tool execution
        """
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                if tool_name not in self.available_tools:
                    # Refresh tools list
                    tools_result = await session.list_tools()
                    self.available_tools = {
                        tool.name: tool for tool in tools_result.tools
                    }
                
                if tool_name not in self.available_tools:
                    raise ValueError(f"Tool '{tool_name}' not found. Available: {list(self.available_tools.keys())}")
                
                result = await session.call_tool(tool_name, arguments)
                
                # Extract the result value
                if result and hasattr(result, 'content') and result.content:
                    if isinstance(result.content, list) and len(result.content) > 0:
                        content = result.content[0]
                        if hasattr(content, 'text'):
                            try:
                                # Try to parse as JSON first
                                return json.loads(content.text)
                            except json.JSONDecodeError:
                                # If not JSON, return as text
                                return content.text
                        return str(content)
                    return result.content
                return str(result)
    
    async def add(self, num1: float, num2: float) -> float:
        """Add two numbers."""
        result = await self.call_tool("add_numbers", {"num1": num1, "num2": num2})
        return result
    
    async def subtract(self, num1: float, num2: float) -> float:
        """Subtract two numbers."""
        result = await self.call_tool("subtract_numbers", {"num1": num1, "num2": num2})
        return result
    
    async def multiply(self, num1: float, num2: float) -> float:
        """Multiply two numbers."""
        result = await self.call_tool("multiply_numbers", {"num1": num1, "num2": num2})
        return result
    
    async def divide(self, num1: float, num2: float) -> float:
        """Divide two numbers."""
        result = await self.call_tool("divide_numbers", {"num1": num1, "num2": num2})
        return result
    
    async def power(self, base: float, exponent: float) -> float:
        """Raise base to the power of exponent."""
        result = await self.call_tool("power", {"base": base, "exponent": exponent})
        return result
    
    async def square_root(self, number: float) -> float:
        """Calculate square root of a number."""
        result = await self.call_tool("square_root", {"number": number})
        return result
    
    async def factorial(self, number: int) -> int:
        """Calculate factorial of a number."""
        result = await self.call_tool("factorial", {"number": number})
        return result
    
    async def interactive_mode(self):
        """Run an interactive session with the math server."""
        print("\n=== MCP Math Client - Interactive Mode ===")
        print("Available operations:")
        print("1. add <num1> <num2>")
        print("2. subtract <num1> <num2>") 
        print("3. multiply <num1> <num2>")
        print("4. divide <num1> <num2>")
        print("5. power <base> <exponent>")
        print("6. sqrt <number>")
        print("7. factorial <number>")
        print("8. list - show available tools")
        print("9. quit - exit the client")
        print("=" * 40)
        
        # Connect and discover tools
        await self.connect_and_discover()
        
        while True:
            try:
                user_input = input("\n> ").strip().lower()
                
                if user_input in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if user_input == 'list':
                    print(f"Available tools: {list(self.available_tools.keys())}")
                    continue
                
                parts = user_input.split()
                if len(parts) < 2:
                    print("Invalid command. Use format: <operation> <numbers...>")
                    continue
                
                operation = parts[0]
                
                if operation == 'add' and len(parts) == 3:
                    result = await self.add(float(parts[1]), float(parts[2]))
                    print(f"Result: {parts[1]} + {parts[2]} = {result}")
                
                elif operation == 'subtract' and len(parts) == 3:
                    result = await self.subtract(float(parts[1]), float(parts[2]))
                    print(f"Result: {parts[1]} - {parts[2]} = {result}")
                
                elif operation == 'multiply' and len(parts) == 3:
                    result = await self.multiply(float(parts[1]), float(parts[2]))
                    print(f"Result: {parts[1]} × {parts[2]} = {result}")
                
                elif operation == 'divide' and len(parts) == 3:
                    result = await self.divide(float(parts[1]), float(parts[2]))
                    print(f"Result: {parts[1]} ÷ {parts[2]} = {result}")
                
                elif operation == 'power' and len(parts) == 3:
                    result = await self.power(float(parts[1]), float(parts[2]))
                    print(f"Result: {parts[1]} ^ {parts[2]} = {result}")
                
                elif operation in ['sqrt', 'square_root'] and len(parts) == 2:
                    result = await self.square_root(float(parts[1]))
                    print(f"Result: √{parts[1]} = {result}")
                
                elif operation == 'factorial' and len(parts) == 2:
                    result = await self.factorial(int(parts[1]))
                    print(f"Result: {parts[1]}! = {result}")
                
                else:
                    print("Invalid command or wrong number of arguments.")
                    print("Type 'list' to see available operations.")
            
            except ValueError as e:
                print(f"Error: {e}")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")


async def demo():
    """Run a demonstration of the MCP math client."""
    client = MCPMathClient()
    
    print("=== MCP Math Client Demo ===")
    
    try:
        # Connect and discover tools
        await client.connect_and_discover()
        
        # Perform some calculations
        print("\nPerforming calculations...")
        
        result1 = await client.add(15, 25)
        print(f"15 + 25 = {result1}")
        
        result2 = await client.multiply(result1, 2)
        print(f"{result1} × 2 = {result2}")
        
        result3 = await client.square_root(result2)
        print(f"√{result2} = {result3}")
        
        result4 = await client.factorial(5)
        print(f"5! = {result4}")
        
        print(f"\nFinal calculation: (15 + 25) × 2 = {result2}, √{result2} = {result3}, 5! = {result4}")
        
    except Exception as e:
        print(f"Demo failed: {e}")


async def main():
    """Main function - choose between demo or interactive mode."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        await demo()
    else:
        client = MCPMathClient()
        await client.interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
