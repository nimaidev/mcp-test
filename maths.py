from mcp.server import FastMCP

# Create the MCP server
math_mcp = FastMCP("math_mcp")

@math_mcp.tool()
def add_numbers(num1: int, num2: int) -> int:
    """Add two numbers together"""
    return num1 + num2

@math_mcp.tool()
def subtract_numbers(num1: int, num2: int) -> int:
    """Subtract the second number from the first"""
    return num1 - num2

@math_mcp.tool()
def multiply_numbers(num1: int, num2: int) -> int:
    """Multiply two numbers"""
    return num1 * num2

if __name__ == "__main__":
    print("Running Math MCP")
    math_mcp.run(transport="stdio")

