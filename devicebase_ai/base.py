"""Base Agent implementation with OpenAI, function calling, and streaming support."""

from abc import ABC, abstractmethod
from collections.abc import Callable

from openai import OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_message_function_tool_call import Function


class BaseAgent(ABC):
    """Base agent class supporting function calling and streaming output."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
    ):
        """Initialize the base agent.

        ⚠️ Note: If using this base class for vision-enabled agents (like Agent),
        the 'model' parameter must be a vision/multimodal model that supports
        image_url content type (e.g., gpt-4o, gpt-4o-mini, claude-3-5-sonnet).

        Args:
            api_key: LLM API key (defaults to OPENAI_API_KEY env var)
            base_url: LLM API base URL (defaults to OPENAI_BASE_URL env var)
            model: Model name to use (defaults to OPENAI_MODEL_NAME env var)
            temperature: Temperature for generation
        """
        import os

        # Use environment variables if not provided
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model = model or os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

        if not api_key:
            raise ValueError(
                "LLM API key must be provided or set in OPENAI_API_KEY environment variable"
            )

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature
        self.tools: list[dict] = []
        self.tool_map: dict[str, Callable] = {}

    def register_tool(self, name: str, description: str, parameters: dict, func: Callable):
        """Register a tool for function calling.

        Args:
            name: Tool name
            description: Tool description
            parameters: JSON schema for parameters
            func: Function to execute
        """
        tool_schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        }
        self.tools.append(tool_schema)
        self.tool_map[name] = func

    def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool function.

        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool

        Returns:
            Result of the tool execution
        """
        if tool_name not in self.tool_map:
            return f"Error: Unknown tool '{tool_name}'"

        try:
            result = self.tool_map[tool_name](**arguments)
            return str(result)
        except Exception as e:
            return f"Error executing {tool_name}: {e}"

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        stream: bool = False,
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        """Send a chat completion request.

        Args:
            messages: Conversation messages
            tools: Optional tools for function calling
            stream: Whether to stream the response

        Returns:
            Chat completion or stream
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }

        if tools:
            kwargs["tools"] = tools

        response = self.client.chat.completions.create(**kwargs, stream=stream)
        return response

    def process_stream(self, stream: Stream[ChatCompletionChunk]) -> str:
        """Process a streaming response.

        Args:
            stream: Stream to process

        Returns:
            Complete response text
        """
        full_content = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                print(content, end="", flush=True)
        print()  # New line after streaming
        return full_content

    def process_stream_with_tools(
        self, stream: Stream[ChatCompletionChunk]
    ) -> tuple[str, list, str]:
        """Process a streaming response with tool calls.

        Accumulates content and tool calls from a stream.

        Args:
            stream: Stream to process

        Returns:
            Tuple of (complete response text, list of tool calls)
        """
        from openai.types.chat import ChatCompletionMessageToolCall
        from dataclasses import dataclass

        @dataclass
        class AccumulatedToolCall:
            id: str = ""
            name: str = ""
            arguments: str = ""

        full_content = ""
        full_thinking = ""
        accumulated_calls: list[AccumulatedToolCall] = []
        current_index = -1

        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            # Accumulate thinking
            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                print(delta.reasoning_content, end="", flush=True)
                full_thinking += delta.reasoning_content

            if hasattr(delta, "reasoning") and delta.reasoning:
                print(delta.reasoning, end="", flush=True)
                full_thinking += delta.reasoning

            # Accumulate content
            if delta.content:
                full_content += delta.content
                print(delta.content, end="", flush=True)

            # Accumulate tool calls
            if delta.tool_calls:
                for tool_delta in delta.tool_calls:
                    idx = tool_delta.index if tool_delta.index is not None else 0

                    if idx > current_index:
                        # New tool call
                        accumulated_calls.append(AccumulatedToolCall())
                        current_index = idx

                    tc = accumulated_calls[current_index]
                    if tool_delta.id:
                        tc.id += tool_delta.id
                    if tool_delta.function:
                        if tool_delta.function.name:
                            tc.name += tool_delta.function.name
                        if tool_delta.function.arguments:
                            tc.arguments += tool_delta.function.arguments

        # Convert to tool call objects
        tool_calls: list = []
        for tc in accumulated_calls:
            if tc.name:
                tool_calls.append(
                    ChatCompletionMessageToolCall(
                        id=tc.id,
                        type="function",
                        function=Function(name=tc.name, arguments=tc.arguments),
                    )
                )

        return full_content, tool_calls, full_thinking

    @abstractmethod
    def run(self, prompt: str) -> str:
        """Run the agent with a prompt.

        Args:
            prompt: User prompt

        Returns:
            Agent response
        """
        pass