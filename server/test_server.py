from datetime import datetime
from typing import Annotated
from pydantic import Field
from mcp.server import FastMCP


mcp = FastMCP()

today = datetime.today().strftime("%Y-%m-%d")


@mcp.tool(name="get_energy_consumption_or_cost_data")
async def get_energy_consumption_or_cost_data(
    startDate: Annotated[
        str,
        Field(
            description="date from where energy calculation will starts. Always in the format if YYYY-MM-DD"
        ),
    ],
    endDate: Annotated[
        str,
        Field(
            description=" date from where energy calculation will starts. Always in the format if YYYY-MM-DD"
        ),
    ] = today,
    viewBy: Annotated[
        int,
        Field(
            description=" 0 for energy consumption, 1 for energy cost",
            ge=0, le=1
        ),
    ] = 0,
) -> dict[str,str]:
    """
    Get the energy consumption/cost data as per user requirement
    Args:
        startDate :
    """
    if viewBy == 0:
        return {"result": f"Energy consumption from {startDate} to {endDate} is 200kWh"}
    if viewBy == 1:
        return {"result": f"Energy cost from {startDate} to {endDate} is 200 rupees"}
        
  
