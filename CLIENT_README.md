# MCP Math Server & Clients with LLM Integration

This project provides a complete MCP (Model Context Protocol) math server with multiple client interfaces, including AI-powered natural language processing.

## Components

### 1. MCP Math Server (`maths.py`)
A FastMCP server that provides mathematical operations:
- `add_numbers` - Add two numbers
- `subtract_numbers` - Subtract two numbers  
- `multiply_numbers` - Multiply two numbers
- `divide_numbers` - Divide two numbers
- `power` - Raise base to exponent
- `square_root` - Calculate square root
- `factorial` - Calculate factorial

### 2. Client Options

#### A. 🧠 LLM-Powered Clients (NEW!)

##### LLM Terminal Client (`llm_client.py`)
AI-powered client that understands natural language:

```bash
# Run interactive LLM mode
uv run llm_client.py

# Run LLM demo mode  
uv run llm_client.py demo
```

Example natural language queries:
- "What's 15 plus 25?"
- "Calculate the square root of 144"
- "What's 5 factorial?"
- "Raise 2 to the power of 8"
- "What's (10 + 5) times 3?"
- "Solve 100 divided by 4"

##### LLM Web Chat Interface (`llm_web.py`)
Beautiful chat interface for natural language math queries:

```bash
uv run llm_web.py
```

Then open http://localhost:5001 for an AI chat interface!

#### B. Traditional Clients

##### Interactive Terminal Client (`mcp_client.py`)
Full-featured async client with interactive mode:

```bash
# Run interactive mode
uv run mcp_client.py

# Run demo mode
uv run mcp_client.py demo
```

##### Simple Synchronous Client (`simple_client.py`)
Easy-to-use synchronous wrapper:

```bash
uv run simple_client.py
```

##### Web-based Calculator (`web_client.py`)
Traditional calculator interface:

```bash
uv run web_client.py
```

Then open http://localhost:5000

#### C. Integration Clients

##### VS Code MCP Integration
Configure in `.vscode/mcp.json` for direct tool access in VS Code

##### AutoGen Agent Integration (`main.py`)
Use with AutoGen agents for AI-powered math assistance

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set up OpenAI API Key (for LLM features):**
   ```bash
   echo "OPENAI_API_KEY=your_key_here" >> .env
   ```

3. **Try the LLM chat interface:**
   ```bash
   uv run llm_web.py
   ```

4. **Or try the LLM terminal client:**
   ```bash
   uv run llm_client.py
   ```

## ✨ New LLM Features

### 🤖 Natural Language Processing
- Ask questions in plain English
- Automatic tool selection and execution
- Step-by-step explanations
- Context-aware responses

### 🧠 Smart Calculation Chains
The LLM can handle complex multi-step calculations:
- "Calculate (15 + 25) times 2, then find the square root"
- "What's 5 factorial divided by 10?"
- "Raise 2 to the power of 8, then subtract 100"

### 💬 Conversational Interface
- Web chat interface with modern UI
- Real-time responses
- Error handling and explanations
- Example queries to get started

## 🛠️ Development

### Adding New Math Operations

1. **Add to MCP server** (`maths.py`):
```python
@math_mcp.tool
def new_operation(param: float) -> float:
    """Description of the operation"""
    return result
```

2. **Add to LLM schema** (`llm_client.py`):
```python
"new_operation": {
    "name": "new_operation",
    "description": "Description for LLM",
    "parameters": {
        "type": "object",
        "properties": {
            "param": {"type": "number", "description": "Parameter description"}
        },
        "required": ["param"]
    }
}
```

### Example LLM Usage in Code

```python
from llm_client import LLMMathClient

async def main():
    client = LLMMathClient()
    
    # Process natural language
    response = await client.process_natural_language(
        "What's the square root of 144 plus 5 factorial?"
    )
    print(response)

asyncio.run(main())
```

## 🎯 Use Cases

### Educational
- Math tutoring with natural language
- Step-by-step problem solving
- Interactive learning assistance

### Development  
- API testing with natural language
- Rapid calculation prototyping
- Integration into larger systems

### Business
- Natural language calculation interface
- Customer service math assistance
- Automated calculation workflows

## 🔧 Troubleshooting

### LLM Features
- **"API key not found"**: Set `OPENAI_API_KEY` in your `.env` file
- **Slow responses**: Check your internet connection and OpenAI API status
- **Wrong calculations**: The LLM chooses tools automatically - verify your query is clear

### Traditional Features
- **Server won't start**: Run `uv sync` to install dependencies
- **Connection errors**: Ensure the MCP server is accessible
- **Web interface issues**: Check that the port (5000/5001) is available

## 📊 Feature Comparison

| Client Type | Natural Language | GUI | API Integration | Complexity |
|-------------|------------------|-----|-----------------|------------|
| LLM Web Chat | ✅ | ✅ | ✅ | Low |
| LLM Terminal | ✅ | ❌ | ✅ | Low |
| Web Calculator | ❌ | ✅ | ❌ | Low |
| Terminal Client | ❌ | ❌ | ✅ | Medium |
| AutoGen Agent | ✅ | ❌ | ✅ | High |
| VS Code Tools | ❌ | ✅ | ✅ | Low |

## 🏆 Best Practices

1. **For learning/tutoring**: Use LLM web chat interface
2. **For development**: Use LLM terminal client or simple client
3. **For integration**: Use AutoGen agent or direct MCP tools
4. **For quick calculations**: Use any web interface
5. **For automation**: Use simple client in scripts
