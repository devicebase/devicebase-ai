"""ReAct Agent implementation using devicebase.

⚠️ IMPORTANT: This agent requires a vision/multimodal LLM to function properly.
The agent captures screenshots at every step and sends them to the LLM for visual context.
Using a text-only model will result in poor performance and failed automation tasks.

Supported vision models: gpt-4o, gpt-4o-mini, claude-3-5-sonnet, llama3.2-vision
Unsupported (text-only): gpt-3.5-turbo, text-davinci-003, base llama models
"""

import base64
import os
import io
from PIL import Image

from devicebase import DeviceBaseClient

from devicebase_ai.base import BaseAgent
from devicebase_ai.prompt import SYSTEM_PROMPT

class Agent(BaseAgent):
    """ReAct-style agent that uses devicebase for mobile automation.

    This agent automatically captures screenshots at each step to provide visual
    context to the LLM. This requires a vision/multimodal model that supports
    image_url content type.
    """

    MAX_ITERATIONS = 30

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
        device_serial: str | None = None,
        devicebase_base_url: str | None = None,
        devicebase_api_key: str | None = None,
    ):
        """Initialize the ReAct agent.

        ⚠️ IMPORTANT: The 'model' parameter MUST be a vision/multimodal model.
        See module-level documentation for supported models.

        Args:
            api_key: LLM API key (defaults to OPENAI_API_KEY env var)
            base_url: LLM API base URL (defaults to OPENAI_BASE_URL env var)
            model: Model name to use (defaults to OPENAI_MODEL_NAME env var)
                  ⚠️ Must be a vision/multimodal model!
            device_serial: Device serial number (auto-detect if None)
            devicebase_base_url: Devicebase API base URL (defaults to DEVICEBASE_BASE_URL env var)
            devicebase_api_key: Devicebase API key (defaults to DEVICEBASE_API_KEY env var)
        """
        # Get devicebase configuration from environment if not provided
        devicebase_base_url = devicebase_base_url or os.getenv("DEVICEBASE_BASE_URL")
        devicebase_api_key = devicebase_api_key or os.getenv("DEVICEBASE_API_KEY")
        device_serial = device_serial or os.getenv("DEVICEBASE_DEVICE_SERIAL")

        # Initialize base agent (will use env vars for LLM config)
        super().__init__(api_key=api_key, base_url=base_url, model=model)

        # Initialize devicebase client with configuration
        device_kwargs = {}
        if device_serial:
            device_kwargs["serial"] = device_serial
        if devicebase_base_url:
            device_kwargs["base_url"] = devicebase_base_url
        if devicebase_api_key:
            device_kwargs["api_key"] = devicebase_api_key

        self.device = DeviceBaseClient(**device_kwargs)
        device_info = self.device.get_device_info()
        self.device_serial = device_info.serial
        self._screen = [1080, 2400]
        print(f"Connected to device: {self.device_serial}")

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register all available tools."""

        # Tap
        self.register_tool(
            name="tap",
            description="Tap at a point on the screen. Coordinates are relative (0-1000 scale).",
            parameters={
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "X,Y coordinate (0-1000) (e.g., 123,234)",
                    },
                },
                "required": ["value"],
            },
            func=self._tap,
        )

        # Double tap
        self.register_tool(
            name="double_tap",
            description="Double tap at a point on the screen.",
            parameters={
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "X,Y coordinate (0-1000) (e.g., 123,234)",
                    },
                },
                "required": ["value"],
            },
            func=self._double_tap,
        )

        # Long press
        self.register_tool(
            name="long_press",
            description="Long press at a point on the screen.",
            parameters={
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "X,Y coordinate (0-1000) (e.g., 123,234)",
                    },
                },
                "required": ["value"],
            },
            func=self._long_press,
        )

        # Swipe
        self.register_tool(
            name="swipe",
            description="Swipe from one point to another.",
            parameters={
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "start_x,start_y,end_x,end_y coordinate (0-1000) (e.g., 123,234,566,456)",
                    },
                },
                "required": ["value"],
            },
            func=self._swipe,
        )

        # Type text
        self.register_tool(
            name="type_text",
            description="Type text into the currently focused input field.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to type"},
                },
                "required": ["text"],
            },
            func=self._type_text,
        )

        # Launch app
        self.register_tool(
            name="launch_app",
            description="Launch an app by name.",
            parameters={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "App name"},
                },
                "required": ["app_name"],
            },
            func=self._launch_app,
        )

        # Back
        self.register_tool(
            name="back",
            description="Press the Back button.",
            parameters={"type": "object", "properties": {}},
            func=self._back,
        )

        # Home
        self.register_tool(
            name="home",
            description="Press the Home button.",
            parameters={"type": "object", "properties": {}},
            func=self._home,
        )

        # Wait
        self.register_tool(
            name="wait",
            description="Wait for a duration before next action.",
            parameters={
                "type": "object",
                "properties": {
                    "duration": {"type": "string", "description": "e.g. '2 seconds'"},
                },
                "required": ["duration"],
            },
            func=self._wait,
        )

        # Get screen info
        # self.register_tool(
        #    name="get_screen_info",
        #    description="Get current screen information including hierarchy and text.",
        #    parameters={"type": "object", "properties": {}},
        #    func=self._get_screen_info,
        # )

        # Finish
        self.register_tool(
            name="finish",
            description="Task completed. Call when the user's goal is achieved.",
            parameters={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Summary of result"},
                },
                "required": ["message"],
            },
            func=self._finish,
        )

    # Tool implementations
    def _tap(self, value: str) -> str:
        x, y = self._parse_coords(value)
        x = int(x) / 1000 * self._screen[0]
        y = int(y) / 1000 * self._screen[1]
        self.device.tap(x=int(x), y=int(y))
        return f"Tapped at ({int(x)}, {int(y)})"

    def _double_tap(self, value: str) -> str:
        x, y = self._parse_coords(value)
        x = int(x) / 1000 * self._screen[0]
        y = int(y) / 1000 * self._screen[1]
        self.device.double_tap(x=int(x), y=int(y))
        return f"Double tapped at ({int(x)}, {int(y)})"

    def _long_press(self, value: str) -> str:
        x, y = self._parse_coords(value)
        x = int(x) / 1000 * self._screen[0]
        y = int(y) / 1000 * self._screen[1]
        self.device.long_press(x=int(x), y=int(y))
        return f"Long pressed at ({int(x)}, {int(y)})"

    def _swipe(self, value: str) -> str:
        parts = self._parse_coords(value, require_many=True)
        if len(parts) < 4:
            return f"Error: swipe requires 4 coordinates, got {parts}"
        start_x, start_y, end_x, end_y = parts[:4]
        start_x = int(start_x) / 1000 * self._screen[0]
        start_y = int(start_y) / 1000 * self._screen[1]
        end_x = int(end_x) / 1000 * self._screen[0]
        end_y = int(end_y) / 1000 * self._screen[1]
        self.device.swipe(
            x1=int(start_x),
            y1=int(start_y),
            x2=int(end_x),
            y2=int(end_y),
        )
        return f"Swiped from ({int(start_x)}, {int(start_y)}) to ({int(end_x)}, {int(end_y)})"

    def _parse_coords(self, value: str, require_many: bool = False) -> list[str]:
        """Parse coordinate string from tool arguments.

        Handles multiple formats:
        - "380,767" -> ["380", "767"]
        - "[380, 767]" -> ["380", "767"]
        - "{'value': '380,767'}" -> ["380", "767"]
        - "{'value': [380, 767]}" -> ["380", "767"]
        """
        import ast

        # Try parsing as Python literal first
        try:
            parsed = ast.literal_eval(str(value))
            if isinstance(parsed, dict):
                # Extract from dict (e.g., {"value": "380,767"} or {"value": [380, 767]})
                for v in parsed.values():
                    if isinstance(v, str):
                        return self._parse_coords(v, require_many)
                    elif isinstance(v, (list, tuple)):
                        return [str(i) for i in v]
                # Try flattening if it's the raw dict
                parts = []
                for v in parsed.values():
                    if isinstance(v, str) and "," in v:
                        parts.extend(v.split(","))
                    elif isinstance(v, (int, float)):
                        parts.append(str(v))
                if parts:
                    return parts
            elif isinstance(parsed, (list, tuple)):
                return [str(i) for i in parsed]
            elif isinstance(parsed, str):
                # If it's a comma-separated string, parse it
                if "," in parsed:
                    return [p.strip() for p in parsed.split(",")]
                return [parsed]
        except (ValueError, SyntaxError):
            pass

        # Fallback: split by comma
        if "," in value:
            return [p.strip() for p in value.split(",")]
        return [value]

    def _type_text(self, text: str) -> str:
        self.device.input_text(text=text)
        return f"Typed: {text}"

    def _launch_app(self, app_name: str) -> str:
        self.device.launch_app(app_name=app_name)
        return f"Launched app: {app_name}"

    def _back(self) -> str:
        self.device.back()
        return "Pressed Back button"

    def _home(self) -> str:
        self.device.home()
        return "Pressed Home button"

    def _wait(self, duration: str) -> str:
        import time
        parts = duration.split()
        seconds = int(parts[0])
        time.sleep(seconds)
        return f"Waited {duration}"

    def _get_screen_info(self) -> str:
        """Get current screen information."""
        hierarchy = self.device.dump_hierarchy()
        return f"Current screen hierarchy:\n{hierarchy}"
    
    def _current_app(self):
        """Get current app name."""
        try:
            app_info = self.device.get_current_app()
            return app_info.data["data"] if "data" in app_info.data else ""
        except Exception:
            return None

    def _get_screenshot_base64(self) -> bytes | None:
        """Get screenshot as base64 bytes."""
        try:
            img_bytes = self.device.get_screenshot()
            # read img_bytes as image
            img = Image.open(io.BytesIO(img_bytes))
            self._screen = [img.width, img.height]
            print(f"Screen size: {self._screen}")
            return img_bytes
        except Exception:
            return None

    def _finish(self, message: str) -> str:
        """Mark task as complete."""
        return f"[TASK COMPLETE] {message}"

    def run(self, prompt: str, stream: bool = True) -> str:
        """Run the ReAct agent with a prompt.

        ⚠️ This method requires a vision/multimodal model to process screenshots.
        Screenshots are captured at each step and sent to the LLM as image_url content.

        Args:
            prompt: User prompt
            stream: Whether to stream the response

        Returns:
            Final response
        """
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        print(f"\n{'='*60}")
        print(f"Task: {prompt}")
        print(f"{'='*60}\n")

        for iteration in range(self.MAX_ITERATIONS):
            print(f"\n[Iteration {iteration + 1}/{self.MAX_ITERATIONS}]")
            if iteration > 0:
                prompt = f"Current App: {self._current_app()}"
                print(prompt)
            # Capture screenshot after tool execution
            post_screenshot = self._get_screenshot_base64()
            # Add screenshot if available
            if post_screenshot:
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(post_screenshot).decode()}"},
                        }
                    ],
                })
                print("[Screenshot captured and attached to context]")

            # Get response from LLM
            response = self.chat(messages=messages, tools=self.tools, stream=stream)

            if stream:
                content, tool_calls, thinking_content = self.process_stream_with_tools(response)
                # (content)
            else:
                content = response.choices[0].message.content or ""
                tool_calls = response.choices[0].message.tool_calls or []
                thinking_content = ""
                print(content)

            # Handle function calls
            if not tool_calls:
                print("\n[No more tool calls]")
                break

            if thinking_content or content:
                messages.append({
                    "role": "assistant",
                    "content": f"thinking: {thinking_content}\nanswer: {content}",
                })

            # Process tool calls
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = eval(tool_call.function.arguments)

                print(f"\n[Tool Call] {function_name}({function_args})")

                # Execute tool
                result = self._execute_tool(function_name, function_args)
                print(f"[Result] {result}")

                # Add assistant message and tool result to conversation
                messages.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call],
                    }
                )

                # Build tool response message with screenshot
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": [
                        {"type": "text", "text": result},
                    ],
                }

                messages.append(tool_message)

                # Check if task is finished
                if function_name == "finish":
                    print(f"\n{'='*60}")
                    print("Task completed successfully!")
                    print(f"{'='*60}\n")
                    return result
                
            # Remove all historical image_url entries to keep only the latest screenshot
            # This is required because LLMs typically only support one image per request
            for msg in messages:
                if isinstance(msg.get("content"), list):
                    msg["content"] = [
                        item for item in msg["content"]
                        if item.get("type") != "image_url"
                    ]


        return "Agent execution completed"
