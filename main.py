
# main.py
import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv(override=True)

async def log_tools(log: str)  -> None:
    """
        This function print logs to the console
    """
    print(f"===========> {log}")
    
    
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY")
)

# AutoGen agents setup
async def main() -> None:
    
    assistant_agent = AssistantAgent(
        name="personal_assistant",
        model_client= model_client,
        system_message="You are an polite helpful assistant"
    )
    
    log_agent = AssistantAgent(
        name="log_agent",
        model_client=model_client,
        tools=[log_tools],
        reflect_on_tool_use=True,
        system_message="You are an assistant to log data to the console"
    )
    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=2)
    termination = text_mention_termination | max_messages_termination
    selector_prompt = """Select an agent to perform task.

        {roles}

        Current conversation context:
        {history}

        Read the above conversation, then select an agent from {participants} to perform the next task.
        Make sure the planner agent has assigned tasks before other agents start working.
        Only select one agent.
    """
    team = SelectorGroupChat(
        [log_agent, assistant_agent],
        model_client=model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=True,  # Allow an agent to speak multiple turns in a row.
    )
    
    # await Console(team.run_stream(task="What is RAG"))
    
    await Console(team.run_stream(task = "print -> Hello World!"))
        
    
    


if __name__ == "__main__":
    asyncio.run(main())