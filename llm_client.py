#!/usr/bin/env python3
"""
LLM-Powered MCP Math Client

An intelligent math assistant that uses LLM to understand natural language
and automatically calls the appropriate MCP math tools.
"""

import asyncio
import json
from typing import Dict, Any, List
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class LLMMathClient:
    """LLM-powered client for the MCP math server."""
    
    def __init__(self, command: str = "uv", args: List[str] = None, model: str = "gpt-4o"):
        """Initialize the LLM-powered MCP client.
        
        Args:
            command: Command to start the MCP server
            args: Arguments for the server command
            model: OpenAI model to use for LLM capabilities
        """
        self.server_params = StdioServerParameters(
            command=command,
            args=args or ["run", "maths.py"]
        )
        self.available_tools = {}
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        
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
                
                print("🔗 Connected to MCP math server!")
                print(f"🛠️  Available tools: {list(self.available_tools.keys())}")
                return session
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool with given arguments."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                result = await session.call_tool(tool_name, arguments)
                
                # Extract the result value
                if result and hasattr(result, 'content') and result.content:
                    if isinstance(result.content, list) and len(result.content) > 0:
                        content = result.content[0]
                        if hasattr(content, 'text'):
                            try:
                                return json.loads(content.text)
                            except json.JSONDecodeError:
                                return content.text
                        return str(content)
                    return result.content
                return str(result)
    
    def get_tools_schema(self) -> List[Dict]:
        """Get OpenAI function calling schema for available tools."""
        tools_schema = []
        
        # Define the schemas for each tool
        schemas = {
            "add_numbers": {
                "name": "add_numbers",
                "description": "Add two numbers together",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num1": {"type": "number", "description": "First number"},
                        "num2": {"type": "number", "description": "Second number"}
                    },
                    "required": ["num1", "num2"]
                }
            },
            "subtract_numbers": {
                "name": "subtract_numbers", 
                "description": "Subtract the second number from the first",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num1": {"type": "number", "description": "Number to subtract from"},
                        "num2": {"type": "number", "description": "Number to subtract"}
                    },
                    "required": ["num1", "num2"]
                }
            },
            "multiply_numbers": {
                "name": "multiply_numbers",
                "description": "Multiply two numbers",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "num1": {"type": "number", "description": "First number"},
                        "num2": {"type": "number", "description": "Second number"}
                    },
                    "required": ["num1", "num2"]
                }
            },
            "divide_numbers": {
                "name": "divide_numbers",
                "description": "Divide the first number by the second",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num1": {"type": "number", "description": "Number to divide (numerator)"},
                        "num2": {"type": "number", "description": "Number to divide by (denominator)"}
                    },
                    "required": ["num1", "num2"]
                }
            },
            "power": {
                "name": "power",
                "description": "Raise base to the power of exponent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "base": {"type": "number", "description": "Base number"},
                        "exponent": {"type": "number", "description": "Exponent"}
                    },
                    "required": ["base", "exponent"]
                }
            },
            "square_root": {
                "name": "square_root",
                "description": "Calculate the square root of a number",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "number": {"type": "number", "description": "Number to find square root of"}
                    },
                    "required": ["number"]
                }
            },
            "factorial": {
                "name": "factorial",
                "description": "Calculate the factorial of a non-negative integer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "number": {"type": "integer", "description": "Non-negative integer to calculate factorial of"}
                    },
                    "required": ["number"]
                }
            }
        }
        
        for tool_name in self.available_tools.keys():
            if tool_name in schemas:
                tools_schema.append({"type": "function", "function": schemas[tool_name]})
        
        return tools_schema
    
    async def process_natural_language(self, user_input: str) -> str:
        """Process natural language input and execute appropriate math operations."""
        print(f"🤖 Processing: '{user_input}'")
        
        # Get available tools schema
        tools_schema = self.get_tools_schema()
        
        system_message = """You are an intelligent math assistant with access to mathematical tools through MCP.

            Your capabilities:
            - Add, subtract, multiply, divide numbers
            - Calculate powers and square roots  
            - Calculate factorials
            - Parse natural language math requests

            When users ask math questions:
            1. Identify the mathematical operations needed
            2. Use the appropriate tools to perform calculations
            3. Show your work step by step
            4. Provide clear, friendly explanations

            Examples of what you can handle:
            - "What's 15 plus 25?"
            - "Calculate the square root of 144"
            - "What's 5 factorial?"
            - "Raise 2 to the power of 8"
            - "Solve (10 + 5) × 3"
            - "What's 100 divided by 4?"

            Always be helpful and show your reasoning process."""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input}
        ]
        
        try:
            # Call OpenAI with function calling
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools_schema,
                tool_choice="auto",
                temperature=0.1
            )
            
            message = response.choices[0].message
            result_text = ""
            
            # Handle tool calls
            if message.tool_calls:
                print("🔧 Executing mathematical operations...")
                
                # Add assistant message to conversation
                messages.append({
                    "role": "assistant", 
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        } for tool_call in message.tool_calls
                    ]
                })
                
                # Execute each tool call
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    print(f"  📊 Calling {function_name} with {arguments}")
                    
                    try:
                        # Call the MCP tool
                        tool_result = await self.call_tool(function_name, arguments)
                        print(f"  ✅ Result: {tool_result}")
                        
                        # Add tool result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(tool_result)
                        })
                        
                    except Exception as e:
                        error_msg = f"Error executing {function_name}: {str(e)}"
                        print(f"  ❌ {error_msg}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": error_msg
                        })
                
                # Get final response with results
                final_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1
                )
                
                result_text = final_response.choices[0].message.content
                
            else:
                # No tool calls needed, just return the response
                result_text = message.content or "I understand your request, but I'm not sure how to help with that specific calculation."
            
            return result_text
            
        except Exception as e:
            return f"❌ Error processing request: {str(e)}"
    
    async def interactive_llm_mode(self):
        """Run an interactive session with LLM-powered natural language processing."""
        print("\n🧠 === LLM-Powered MCP Math Assistant ===")
        print("Ask me anything about math! I can understand natural language.")
        print("\nExamples:")
        print("• 'What's 15 plus 25 times 2?'")
        print("• 'Calculate the square root of 144'") 
        print("• 'What's 5 factorial?'")
        print("• 'Raise 2 to the power of 8'")
        print("• 'What's (10 + 5) divided by 3?'")
        print("\nType 'quit' to exit.")
        print("=" * 50)
        
        # Connect and discover tools
        await self.connect_and_discover()
        
        while True:
            try:
                user_input = input("\n🔤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
                    print("👋 Goodbye! Thanks for using the LLM Math Assistant!")
                    break
                
                if not user_input:
                    continue
                
                # Process the natural language input
                response = await self.process_natural_language(user_input)
                print(f"\n🤖 Assistant: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Thanks for using the LLM Math Assistant!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")


async def demo_llm():
    """Run a demonstration of the LLM-powered math client."""
    client = LLMMathClient()
    
    print("🧠 === LLM-Powered MCP Math Client Demo ===")
    
    try:
        # Connect and discover tools
        await client.connect_and_discover()
        
        # Test natural language queries
        test_queries = [
            "What's 15 plus 25?",
            "Calculate the square root of 144",
            "What's 5 factorial?", 
            "Raise 2 to the power of 8",
            "What's 100 divided by 4?",
            "Calculate (10 + 5) times 3"
        ]
        
        print(f"\n🧪 Testing {len(test_queries)} natural language queries...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Test {i}/{len(test_queries)} ---")
            response = await client.process_natural_language(query)
            print(f"🤖 Response: {response}")
            await asyncio.sleep(1)  # Brief pause between requests
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


async def main():
    """Main function - choose between demo or interactive mode."""
    import sys
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key in the .env file")
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        await demo_llm()
    else:
        client = LLMMathClient()
        await client.interactive_llm_mode()


if __name__ == "__main__":
    asyncio.run(main())
