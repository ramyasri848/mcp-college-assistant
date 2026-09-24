import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


BASE_DIR = Path(__file__).resolve().parent.parent
SERVER_FILE = BASE_DIR / "server" / "server.py"

load_dotenv(BASE_DIR / ".env")


SYSTEM_PROMPT = """
You are a college assistant.

You can answer questions using college information
provided through MCP resources.

You can also manage tasks using MCP tools.

When a user asks for information about the college,
use the information available from the MCP resources.

When the user asks you to create, complete, list,
or delete a task, use the appropriate MCP tool.

Do not invent college information.
"""


async def run_assistant(user_request):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("OPENAI_API_KEY is missing.")
        print("Create a .env file and add your API key.")
        return

    openai_client = OpenAI(api_key=api_key)

    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_FILE)]
    )

    async with stdio_client(server_parameters) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            print("\n[MCP] Connected to College MCP Server")

            resources_result = await session.list_resources()

            print(
                f"[MCP] Resources discovered: "
                f"{len(resources_result.resources)}"
            )

            tools_result = await session.list_tools()

            print(
                f"[MCP] Tools discovered: "
                f"{len(tools_result.tools)}"
            )

            department_result = await session.read_resource(
                "college://departments/CSE"
            )

            cse_information = department_result.contents[0].text

            print("\n[MCP RESOURCE] CSE Department data loaded")

            mcp_tools = []

            for tool in tools_result.tools:
                mcp_tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description or "",
                            "parameters": tool.inputSchema
                        }
                    }
                )

            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": (
                        f"College resource data:\n"
                        f"{cse_information}\n\n"
                        f"User request:\n"
                        f"{user_request}"
                    )
                }
            ]

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=mcp_tools,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message

            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments
                            }
                        }
                        for call in (assistant_message.tool_calls or [])
                    ]
                }
            )

            if assistant_message.tool_calls:

                for tool_call in assistant_message.tool_calls:

                    tool_name = tool_call.function.name

                    arguments = json.loads(
                        tool_call.function.arguments
                    )

                    print(
                        f"\n[MCP TOOL] Executing: "
                        f"{tool_name}"
                    )

                    print(
                        f"[MCP TOOL] Arguments: "
                        f"{arguments}"
                    )

                    tool_result = await session.call_tool(
                        tool_name,
                        arguments
                    )

                    result_text = str(tool_result.content)

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_text
                        }
                    )

            final_response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )

            answer = final_response.choices[0].message.content

            print("\n==============================")
            print("FINAL AI RESPONSE")
            print("==============================")
            print(answer)


if __name__ == "__main__":
    request = input(
        "\nEnter your request: "
    )

    asyncio.run(
        run_assistant(request)
    )