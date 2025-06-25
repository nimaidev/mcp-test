
# main.py
import asyncio
import os
from time import timezone
import time
from typing import Any

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import httpx

load_dotenv(override=True)

async def log_tools(log: str)  -> None:
    """
        This function print logs to the console
    """
    print(f"===========> {log}")
    
async def get_iqnext_cloud_version() -> Any | None:
    """
        This method will call a api to get the IQNext Cloud Version
    """
    response =  httpx.get("https://faraday.iqnext.io/api/iqnext/v1/nc/about")    
    res = response.json()
    if res:
        return res.get("success").get("data")
    

async def get_energy_consumption(start_date : str, end_date: str, week_days : str, view_by: int):
    f"""
        Get the energy consumption/ Cost as per user requirement
        Args:
            start_date:
                type: string
                description: A Date in 'YYYY-MM-DD' format, need to be calculated dynamically, 
                assuming today as {time.time} 
                    Example-1:  
                        If User asks last 7 days then start_date should be today - 7 Days
                    Example-2:
                        if User ask for January data then start_date is [{time.time} in YYYY]:01:01
            end_date:
                type: string
                description: A Date in 'YYYY-MM-DD' format, need to be calculated dynamically, 
                assuming today as {time.time} 
                    Example-1:  
                        If User asks last 7 days then end_date should be today 
                    Example-2:
                        if User ask for January data then end_date is [{time.time} in YYYY]:01:31
            week_days:
                type: string
                description: A coma separated string with day in number notation starts from sunday as 0
                    Example-1:
                        If user asks for workings days the value should be Monday to Friday i.e. 1,2,3,4,5
                    Example-2:
                        If user asks for non working days then weekdays should be 6,0 where 6 is saturday and 0 is sunday
                default: 0,1,2,3,4,5,6
            view_by:
                type: int,
                description: always will be 0 or 1 , where 0 denotes consumption and 1 denotes cost
                    Example-1:
                        If user asks for energy consumption then view_by = 0, if user asks for energy cost then 1
                default: 0
    """
    payload = {
        "startDate" : start_date,
        "startTime" : "00:00",
        "endDate"   : end_date,
        "endTime"   : "23:59",
        "floorIds"  : "7,1,18,5,19,13,6",
        "selectedWeeekDays" : week_days,
        "viewBY"    : view_by
    }
    
    print(payload)
    url =  os.getenv("ENERGY_URL")
    token = os.getenv("CP_TOKEN")
    response = httpx.post(
        url=url,
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    response = response.json()
    if response:
        print(response)
        return response.get("success").get("data")
    
    
    
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY")
)

# AutoGen agents setup
async def main() -> None:
    
    energy_agent = AssistantAgent(
        name="energy_agent",
        model_client= model_client,
        tools = [get_energy_consumption],
        reflect_on_tool_use=True,
        system_message="You are an polite helpful assistant who is capable of processing user query related to energy data like consumption, load, cost etc."
    )
    
    log_agent = AssistantAgent(
        name="log_agent",
        model_client=model_client,
        tools=[log_tools , get_iqnext_cloud_version],
        reflect_on_tool_use=True,
        system_message="You are an assistant to log data to the console or get cloud version"
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
        [log_agent, energy_agent],
        model_client=model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=True,  # Allow an agent to speak multiple turns in a row.
    )
    
    # await Console(team.run_stream(task="What is RAG"))
    
    await Console(team.run_stream(task = "what is my current month energy usage"))
        
    # await Console(assistant_agent.run(task="what is my current month energy usage"))
    


if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(get_iqnext_cloud_version())