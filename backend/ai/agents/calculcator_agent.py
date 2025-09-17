from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder
from langchain_core.tools.structured import StructuredTool
from pydantic import BaseModel, Field


calculator_agent_chat_prompt_template = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
"""
You are a calculator agent. You can perform mathematical calculations and provide accurate results.
"""
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
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
