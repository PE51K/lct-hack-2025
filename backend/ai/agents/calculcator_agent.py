"""
Calculator Agent Module.

This module defines the calculator agent, including its prompt template,
tools for mathematical operations, and input models.
"""

from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain_core.tools.structured import StructuredTool
from pydantic import BaseModel, Field

# Chat prompt template for the calculator agent
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
    """
    Input model for the sum_numbers tool.

    Attributes:
        numbers (list[float]): A list of numbers to sum.
    """

    numbers: list[float] = Field(..., description="A list of numbers to sum")


async def sum_numbers(numbers: list[float]) -> float:
    """
    Sum a list of numbers.

    Args:
        numbers (list[float]): The list of numbers to sum.

    Returns:
        float: The sum of the numbers.
    """
    return sum(numbers)


# List of tools available to the calculator agent
calculator_agent_tools = [
    StructuredTool.from_function(
        name="sum_numbers",
        description="Sum a list of numbers",
        coroutine=sum_numbers,
        input_model=SummationInput,
    ),
]
