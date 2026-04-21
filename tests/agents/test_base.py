"""Tests for BaseAgent."""

import pytest
from unittest.mock import Mock, patch
from devicebase_ai.base import BaseAgent


# Concrete implementation for testing
class TestableAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    def run(self, prompt: str) -> str:
        """Simple implementation for testing."""
        return f"Processed: {prompt}"


class TestBaseAgent:
    """Test BaseAgent functionality."""

    def test_register_tool(self):
        """Test tool registration."""
        agent = TestableAgent(api_key="test-key")

        def dummy_tool(x: int) -> int:
            return x * 2

        agent.register_tool(
            name="multiply",
            description="Multiply by 2",
            parameters={
                "type": "object",
                "properties": {"x": {"type": "integer"}},
                "required": ["x"],
            },
            func=dummy_tool,
        )

        assert len(agent.tools) == 1
        assert agent.tools[0]["function"]["name"] == "multiply"
        assert "multiply" in agent.tool_map

    def test_execute_tool_success(self):
        """Test successful tool execution."""
        agent = TestableAgent(api_key="test-key")

        def dummy_tool(x: int) -> int:
            return x * 2

        agent.register_tool(
            name="multiply",
            description="Multiply by 2",
            parameters={
                "type": "object",
                "properties": {"x": {"type": "integer"}},
                "required": ["x"],
            },
            func=dummy_tool,
        )

        result = agent._execute_tool("multiply", {"x": 5})
        assert result == "10"

    def test_execute_tool_unknown(self):
        """Test executing unknown tool."""
        agent = TestableAgent(api_key="test-key")

        result = agent._execute_tool("unknown", {})
        assert "Error: Unknown tool" in result

    def test_execute_tool_error(self):
        """Test tool execution with error."""
        agent = TestableAgent(api_key="test-key")

        def failing_tool() -> None:
            raise ValueError("Tool error")

        agent.register_tool(
            name="failing",
            description="Failing tool",
            parameters={"type": "object", "properties": {}},
            func=failing_tool,
        )

        result = agent._execute_tool("failing", {})
        assert "Error executing failing" in result

    @patch("devicebase_ai_agent.base_agent.OpenAI")
    def test_chat_without_tools(self, mock_openai):
        """Test chat without tools."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_response = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        agent = TestableAgent(api_key="test-key")
        messages = [{"role": "user", "content": "Hello"}]

        response = agent.chat(messages=messages, stream=False)

        mock_client.chat.completions.create.assert_called_once()
        assert response == mock_response

    def test_process_stream(self):
        """Test stream processing."""
        agent = TestableAgent(api_key="test-key")

        # Mock stream chunks
        mock_chunks = []
        for word in ["Hello", " world", "!"]:
            chunk = Mock()
            chunk.choices = [Mock()]
            chunk.choices[0].delta.content = word
            mock_chunks.append(chunk)

        mock_stream = iter(mock_chunks)

        # Capture output
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            result = agent.process_stream(iter(mock_stream))

        assert result == "Hello world!"
