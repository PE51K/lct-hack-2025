from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.tools.structured import StructuredTool
from pydantic import BaseModel, Field


calculator_agent_system_prompt_template = SystemMessagePromptTemplate.from_template(
    """You are a calculator agent. You can perform mathematical calculations and provide accurate results."""
)


class SummationInput(BaseModel):
    numbers: list[float] = Field(..., description="A list of numbers to sum")


async def sum_numbers(numbers: list[float]) -> float:
    return sum(numbers)


calculator_agent_tools = [
    StructuredTool.from_function(
        name="sum_numbers",
        description="Sum a list of numbers",
        coroutine=sum_numbers,
        input_model=SummationInput,
    ),
]
