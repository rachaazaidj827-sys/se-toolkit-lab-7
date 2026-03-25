"""LLM service for intent-based routing with tool calling."""

import httpx
import json
from typing import Optional, Any


class LlmService:
    """Service for making LLM API calls with tool support."""

    def __init__(self, api_key: str, base_url: str, model: str):
        """Initialize the LLM client.

        Args:
            api_key: API key for authentication.
            base_url: Base URL of the LLM API.
            model: Model name to use.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60.0,
        )

    def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        max_iterations: int = 5,
    ) -> str:
        """Chat with the LLM, allowing it to call tools.

        Args:
            messages: Conversation history with user message.
            tools: List of tool schemas available to the LLM.
            max_iterations: Maximum tool call iterations.

        Returns:
            Final response from the LLM.
        """
        for iteration in range(max_iterations):
            # Call the LLM
            response = self._client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": "auto",
                },
            )
            response.raise_for_status()
            data = response.json()
            choice = data["choices"][0]["message"]

            # Check if LLM wants to call tools
            if "tool_calls" in choice and choice["tool_calls"]:
                tool_calls = choice["tool_calls"]
                messages.append(
                    {
                        "role": "assistant",
                        "content": choice.get("content"),
                        "tool_calls": tool_calls,
                    }
                )

                # Execute each tool call
                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    tool_args = json.loads(tool_call["function"]["arguments"])
                    tool_id = tool_call["id"]

                    # Execute the tool
                    result = self._execute_tool(tool_name, tool_args)

                    # Add tool result to messages
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "content": json.dumps(result, default=str),
                        }
                    )
            else:
                # LLM returned final answer
                return choice.get("content", "I don't have enough information to answer.")

        # Max iterations reached
        return "I'm having trouble getting a complete answer. Please try rephrasing your question."

    def _execute_tool(self, name: str, arguments: dict) -> Any:
        """Execute a tool by name.

        Args:
            name: Tool name.
            arguments: Tool arguments.

        Returns:
            Tool execution result.
        """
        # Import here to avoid circular imports
        from bot.services.lms_api import LmsApiService
        from bot.config import config

        api = LmsApiService(config.lms_api_base_url, config.lms_api_key)

        if name == "get_items":
            return api.get_items()
        elif name == "get_learners":
            return api.get_learners()
        elif name == "get_scores":
            return api.get_scores(arguments.get("lab", ""))
        elif name == "get_pass_rates":
            return api.get_pass_rates(arguments.get("lab", ""))
        elif name == "get_timeline":
            return api.get_timeline(arguments.get("lab", ""))
        elif name == "get_groups":
            return api.get_groups(arguments.get("lab", ""))
        elif name == "get_top_learners":
            return api.get_top_learners(
                arguments.get("lab", ""), arguments.get("limit", 5)
            )
        elif name == "get_completion_rate":
            return api.get_completion_rate(arguments.get("lab", ""))
        elif name == "trigger_sync":
            return api.trigger_sync()
        else:
            return {"error": f"Unknown tool: {name}"}


class LlmError(Exception):
    """Custom exception for LLM errors."""

    pass
