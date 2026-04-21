"""Tests for Agent."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from devicebase_ai.agent import Agent


@pytest.fixture
def mock_device():
    """Mock devicebase DeviceBaseClient."""
    with patch("devicebase_ai_agent.base_agent.OpenAI"), patch(
        "devicebase_ai_agent.react_agent.DeviceBaseClient"
    ) as mock:
        device_instance = Mock()
        device_info = Mock()
        device_info.serial = "test-device-123"
        device_instance.get_device_info.return_value = device_info
        mock.return_value = device_instance
        yield device_instance


class TestAgent:
    """Test Agent functionality."""

    def test_init_without_api_key(self, mock_device):
        """Test initialization fails without API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key"):
                Agent()

    def test_init_with_api_key(self, mock_device):
        """Test successful initialization."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            agent = Agent()
            assert agent.device_serial == "test-device-123"
            assert len(agent.tools) == 11  # All registered tools

    def test_register_tools(self, mock_device):
        """Test all tools are registered."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            agent = Agent()

            tool_names = {tool["function"]["name"] for tool in agent.tools}
            expected_tools = {
                "tap",
                "double_tap",
                "long_press",
                "swipe",
                "type_text",
                "launch_app",
                "back",
                "home",
                "wait",
                "get_screen_info",
                "finish",
            }

            assert tool_names == expected_tools

    def test_tap_tool(self, mock_device):
        """Test tap tool execution."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            agent = Agent()
            result = agent._tap("100,200")
            assert "Tapped at" in result
            mock_device.tap.assert_called_once_with(x=100, y=200)

    def test_swipe_tool(self, mock_device):
        """Test swipe tool execution."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            agent = Agent()
            result = agent._swipe("100,200,300,400")
            assert "Swiped from" in result
            mock_device.swipe.assert_called_once_with(
                start_x=100, start_y=200, end_x=300, end_y=400
            )

    def test_type_text_tool(self, mock_device):
        """Test type_text tool execution."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            agent = Agent()
            result = agent._type_text("Hello World")
            assert "Typed: Hello World" in result
            mock_device.input_text.assert_called_once_with(text="Hello World")

    def test_launch_app_tool(self, mock_device):
        """Test launch_app tool execution."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            agent = Agent()
            result = agent._launch_app("WeChat")
            assert "Launched app: WeChat" in result
            mock_device.launch_app.assert_called_once_with(package_name="WeChat")

    def test_back_tool(self, mock_device):
        """Test back tool execution."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            agent = Agent()
            result = agent._back()
            assert "Back button" in result
            mock_device.back.assert_called_once()

    def test_home_tool(self, mock_device):
        """Test home tool execution."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            agent = Agent()
            result = agent._home()
            assert "Home button" in result
            mock_device.home.assert_called_once()

    def test_wait_tool(self, mock_device):
        """Test wait tool execution."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            agent = Agent()
            with patch("time.sleep") as mock_sleep:
                result = agent._wait("2 seconds")
                assert "Waited 2 seconds" in result
                mock_sleep.assert_called_once_with(2)

    def test_get_screen_info_tool(self, mock_device):
        """Test get_screen_info tool execution."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            agent = Agent()
            mock_device.dump_hierarchy.return_value = "Screen content here"
            result = agent._get_screen_info()
            assert "Current screen hierarchy" in result
            mock_device.dump_hierarchy.assert_called_once()

    def test_finish_tool(self, mock_device):
        """Test finish tool execution."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            agent = Agent()
            result = agent._finish("Task completed")
            assert "TASK COMPLETE" in result
            assert "Task completed" in result
