import random
import os

from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

# Initialize OpenTelemetry
# Set service name from environment variable for OpenTelemetry
os.environ.setdefault("OTEL_SERVICE_NAME", "echoagent")

from google.adk.telemetry.setup import maybe_set_otel_providers

maybe_set_otel_providers()


def roll_die(sides: int, tool_context: ToolContext) -> int:
    """Roll a die and record the outcome for later reference."""
    result = random.randint(1, sides)
    if "rolls" not in tool_context.state:
        tool_context.state["rolls"] = []

    tool_context.state["rolls"] = tool_context.state["rolls"] + [result]
    return result


async def check_prime(nums: list[int]) -> str:
    """Check whether the provided numbers are prime."""
    primes = set()
    for number in nums:
        number = int(number)
        if number <= 1:
            continue
        is_prime = True
        for i in range(2, int(number**0.5) + 1):
            if number % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.add(number)
    return (
        "No prime numbers found."
        if not primes
        else f"{', '.join(str(num) for num in primes)} are prime numbers."
    )


def create_model():
    """Use a Gemini model."""
    return "gemini-2.0-flash"


root_agent = Agent(
    model=create_model(),
    name="echoagent_agent",
    description="echoagent agent.",
    instruction="""
Concisely answer the questions asked.
    """,
    tools=[
        roll_die,
        check_prime,
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="http://34.61.30.91/mcp",
            ),
        ),
    ],
)
