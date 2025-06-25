#!/usr/bin/env python3
"""
Simple MCP Math Client

A synchronous wrapper around the async MCP client for easier use.
"""

import asyncio
from mcp_client import MCPMathClient


class SimpleMathClient:
    """Synchronous wrapper for the MCP math client."""
    
    def __init__(self):
        self._client = MCPMathClient()
    
    def add(self, num1: float, num2: float) -> float:
        """Add two numbers."""
        return asyncio.run(self._client.add(num1, num2))
    
    def subtract(self, num1: float, num2: float) -> float:
        """Subtract two numbers."""
        return asyncio.run(self._client.subtract(num1, num2))
    
    def multiply(self, num1: float, num2: float) -> float:
        """Multiply two numbers."""
        return asyncio.run(self._client.multiply(num1, num2))
    
    def divide(self, num1: float, num2: float) -> float:
        """Divide two numbers."""
        return asyncio.run(self._client.divide(num1, num2))
    
    def power(self, base: float, exponent: float) -> float:
        """Raise base to the power of exponent."""
        return asyncio.run(self._client.power(base, exponent))
    
    def square_root(self, number: float) -> float:
        """Calculate square root."""
        return asyncio.run(self._client.square_root(number))
    
    def factorial(self, number: int) -> int:
        """Calculate factorial."""
        return asyncio.run(self._client.factorial(number))


def main():
    """Example usage of the simple client."""
    print("=== Simple MCP Math Client ===")
    
    # Create client
    client = SimpleMathClient()
    
    try:
        # Perform calculations
        print("Performing calculations...")
        
        result1 = client.add(10, 5)
        print(f"10 + 5 = {result1}")
        
        result2 = client.multiply(result1, 3)
        print(f"{result1} × 3 = {result2}")
        
        result3 = client.divide(result2, 9)
        print(f"{result2} ÷ 9 = {result3}")
        
        result4 = client.power(2, 4)
        print(f"2^4 = {result4}")
        
        result5 = client.square_root(16)
        print(f"√16 = {result5}")
        
        result6 = client.factorial(4)
        print(f"4! = {result6}")
        
        print("\nAll calculations completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
