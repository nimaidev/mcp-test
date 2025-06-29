

import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow, RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.anthropic import AnthropicChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
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
        args=["run", "-m", "server"]
    )
    
    async with McpWorkbench(server_params=params) as workbench:
        tools = await workbench.list_tools()
        print(type(tools))

        assistant_agent = AssistantAgent(
            name="assistant_agent",
            model_client=model_client,
            system_message="""
                You are a helpful assistant that uses MCP tools to answer questions. 
                Always end with 'TERMINATE' when done.
            """,
            workbench=workbench
            # tools = tools
        )
        
        formatting_agent = AssistantAgent(
            name = "formatting_agent",
            model_client= model_client,
            system_message="Your job is to format the incoming  data to nice human readable natural language"
        )
        
        builder = DiGraphBuilder()
        builder.add_node(assistant_agent).add_node(formatting_agent)
        builder.add_edge(assistant_agent, formatting_agent)
        
        graph = builder.build()
        
        flow = GraphFlow([assistant_agent, formatting_agent], graph=graph)
        # await Console(flow.run_stream(task="what are my cloud version"))
        
        # result = await workbench.call_tool(tools[0]["name"])
        stream = flow.run_stream(task="what are my cloud version")
        async for event in stream:  # type: ignore
            print(event)
        # print(result)
        
asyncio.run(main())