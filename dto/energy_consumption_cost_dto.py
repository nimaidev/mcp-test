from typing import Optional
from pydantic import BaseModel, Field

# To be used for generating payload using llm 
class EnergyConsumptionCostInputDTO(BaseModel):
    id: Optional[int]
    startDate: str = Field(
        examples=["2024-06-01"],
        json_schema_extra={"meta": "date field in YYYY-MM-DD format"}
    )
    endDate: str = Field(
        examples=["2024-06-30"],
        json_schema_extra={"meta": "date field in YYYY-MM-DD format"}
    )
    startTime: str = Field(
        default="00:00",
        examples=["23:59"],
        json_schema_extra={"meta": "time field with 00:00-23:59 in string format"}
    )
    endTime: str = Field(
        default="23:59",
        examples=["23:59"],
        json_schema_extra={"meta": "time field with 00:00-23:59 in string format"}
    )
    viewBy: int = Field(
        default=0,
        examples=[0, 1],
        json_schema_extra={"meta": "0 energy consumption, 1 for energy cost"},
        ge=0,
        le=1
    )
    floorIds: str = Field(
        ...,
        examples=["1,2,3,4,5"],
        json_schema_extra={"meta": "comma-separated floor IDs"}
    )
    selectedWeeekDays: str = Field(
        ...,
        examples=["Mon,Tue,Wed"],
        json_schema_extra={"meta": "comma-separated weekdays"}
    )