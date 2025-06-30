

import asyncio
from datetime import datetime
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console
from autogen_ext.models.anthropic import AnthropicChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench, SseServerParams, StdioServerParams, StreamableHttpServerParams
from dotenv import load_dotenv
import os

load_dotenv()

model_client = AnthropicChatCompletionClient(
   model = "claude-3-haiku-20240307",
   api_key= os.getenv("ANTHROPIC_API_KEY")
)
async def main() -> None:
    params = StdioServerParams(
        command="uv",
        args=["run", "-m", "server","test_serve"]
    )
    
    params = StreamableHttpServerParams(
        url="http://127.0.0.1:8000/mcp",
        headers = {
            'Authorization' : 'Bearer hello'
        },
        timeout=10
    )

    async with McpWorkbench(server_params=params) as workbench:
        tools = await workbench.list_tools()
        print(type(tools))

        assistant_agent = AssistantAgent(
            name="assistant_agent",
            model_client=model_client,
            system_message=f"""
                You are a helpful assistant that uses MCP tools to answer questions.
                - Generate payload as per the tool signature 
                - Consider today as {datetime.today().strftime("%Y-%m-%d")  }
                - Always end with 'TERMINATE' when done.
            """,
            workbench=workbench
            # tools = tools
        )
        
        formatting_agent = AssistantAgent(
            name = "formatting_agent",
            model_client= model_client,
            system_message="""Your job is to format energy cost data into clear, human-readable language.

            When you receive energy consumption data:
            - Calculate the total cost (consumption × INR 10 per kWh)
            - Show daily breakdown if possible
            - Use currency formatting (INR XX.XX)
            - Highlight key spending insights
            - Make it conversational and easy to understand"""
        )
        
        builder = DiGraphBuilder()
        builder.add_node(assistant_agent).add_node(formatting_agent)
        builder.add_edge(assistant_agent, formatting_agent)
        
        graph = builder.build()
        
        flow = GraphFlow([assistant_agent, formatting_agent], graph=graph)
                
        await Console(flow.run_stream(task="what 2 + 22"))
        # print(result)
        
asyncio.run(main())