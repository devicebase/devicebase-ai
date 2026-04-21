# Screenshot Context Feature

## Overview

The ReAct Agent now automatically captures and includes screenshots at every step of execution. This provides visual context to the LLM, enabling it to make better decisions when controlling mobile devices.

## How It Works

### Automatic Screenshot Capture

1. **Initial Context**: Before starting the task, the agent captures the initial screen state
2. **After Each Action**: After executing any tool, a new screenshot is captured
3. **Visual Feedback**: Screenshots are attached to messages for vision-capable LLMs (GPT-4o, GPT-4o-mini, Claude, etc.)

### Message Format

The agent uses OpenAI's multimodal message format:

```python
{
    "role": "user",
    "content": [
        {"type": "text", "text": "Open WeChat"},
        {
            "type": "image_url",
            "image_url": {
                "url": "data:image/png;base64,<base64_data>"
            }
        }
    ]
}
```

## Benefits

### 1. Better Decision Making
The LLM can see the actual screen state, not just text hierarchy:
- Accurate element identification
- Better understanding of UI layouts
- Improved error detection and recovery

### 2. Enhanced Error Handling
When something goes wrong, the LLM can:
- See error messages visually
- Identify unexpected dialogs
- Detect loading states
- Verify actions succeeded

### 3. More Robust Automation
Visual context helps with:
- Dynamic content handling
- Animated transitions
- Complex UI interactions
- Cross-device compatibility

## Example Flow

```python
from agents.agent import Agent

agent = Agent()

# 1. Initial screenshot captured
agent.run("Open WeChat and send message to John")

# 2. After tap → screenshot captured
# 3. After swipe → screenshot captured
# 4. After type_text → screenshot captured
# Each step includes visual context for the LLM
```

## Console Output

```
============================================================
Task: Open WeChat
============================================================

[Iteration 1/30]
Thinking: I need to find the WeChat icon on the home screen...

[Tool Call] tap({'value': '500,800'})
[Result] Tapped at (500, 800)
[Screenshot captured and attached to context]

[Iteration 2/30]
Thinking: WeChat is now open. I can see the chat list...

[Tool Call] type_text({'text': 'John'})
[Result] Typed: John
[Screenshot captured and attached to context]
```

## Model Compatibility

### Vision-Capable Models (Recommended)
These models can see screenshots:
- **GPT-4o** ✅ Best performance
- **GPT-4o-mini** ✅ Good balance
- **Claude 3.5 Sonnet** ✅ Excellent vision
- **Claude 3 Opus** ✅ High quality

### Text-Only Models
These models work but won't see screenshots:
- **GPT-4** ⚠️ Limited functionality
- **GPT-3.5 Turbo** ⚠️ Not recommended

## Configuration

No additional configuration needed. Screenshots are captured automatically if:
1. Your LLM supports vision (multimodal)
2. Devicebase can capture screenshots (default: enabled)

### Disable Screenshots

If you want to disable screenshot capture:

```python
from agents.agent import Agent

agent = Agent()
# Modify the agent to skip screenshots
agent._get_screenshot_base64 = lambda: None
```

## Performance Considerations

### Screenshot Impact
- **Size**: ~50-200KB per screenshot (PNG)
- **Capture Time**: 100-500ms per screenshot
- **Network**: Adds to API request size

### Optimization Tips

1. **Use efficient models**: GPT-4o-mini balances speed and vision
2. **Limit iterations**: The agent has MAX_ITERATIONS = 30 by default
3. **Monitor tokens**: Vision models consume more tokens per image

```bash
# Monitor token usage with environment variable
export OPENAI_MODEL_NAME="gpt-4o-mini"  # More efficient
```

## Troubleshooting

### Screenshots Not Capturing

**Problem**: `[Screenshot capture failed: ...]` in console

**Solutions**:
1. Check device connection: `adb devices`
2. Verify devicebase server is running
3. Ensure device screen is on
4. Check permissions: ADB screen capture permission

### Large Context Size

**Problem**: API requests too large with many screenshots

**Solutions**:
1. Reduce MAX_ITERATIONS
2. Use model with larger context window
3. Implement screenshot compression

```python
agent = Agent()
agent.MAX_ITERATIONS = 15  # Reduce iterations
```

### Slow Performance

**Problem**: Each iteration takes too long

**Solutions**:
1. Use faster model: GPT-4o-mini instead of GPT-4o
2. Optimize screenshot quality
3. Reduce screenshot frequency

## Advanced Usage

### Custom Screenshot Handler

```python
class CustomAgent(Agent):
    def _get_screenshot_base64(self) -> bytes | None:
        # Add custom logic
        screenshot = super()._get_screenshot_base64()

        # Compress or modify screenshot
        if screenshot:
            # Your custom processing
            pass

        return screenshot
```

### Screenshot Callbacks

```python
class LoggingAgent(Agent):
    def run(self, prompt: str, stream: bool = True) -> str:
        # Add logging for each screenshot
        print(f"Starting task: {prompt}")

        result = super().run(prompt, stream)

        print(f"Task completed with {self.MAX_ITERATIONS} max iterations")
        return result
```

## Best Practices

1. **Use vision-capable models** for best results
2. **Monitor token usage** when running long tasks
3. **Check screenshot quality** if LLM makes visual errors
4. **Adjust iterations** based on task complexity
5. **Test with different models** to find optimal balance

## Examples

See [examples/](examples/) directory for complete examples:
- Basic task with screenshots
- Multi-step workflows
- Error recovery scenarios
