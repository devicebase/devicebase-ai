# devicebase-ai

AI agent framework built on top of devicebase, featuring ReAct-style reasoning for mobile automation.

## Features

- **BaseAgent**: Base class with OpenAI-compatible LLM integration, function calling, and streaming support
- **Agent**: Mobile automation agent using devicebase with reasoning capabilities
- **Visual Context**: Automatic screenshot capture at every step for vision-capable LLMs
- **Tool System**: Extensible tool framework for custom actions
- **Streaming**: Real-time output streaming for better user experience
- **Multi-provider Support**: Compatible with OpenAI, Azure, Anthropic, and other OpenAI-compatible APIs

## ⚠️ Important: Vision/Multimodal Model Required

**This agent requires a vision-capable or multimodal LLM to function properly.**

The agent captures screenshots at every step to provide visual context to the LLM. This is essential for:
- Understanding the current UI state
- Making accurate decisions about which elements to interact with
- Detecting and recovering from errors
- Providing robust automation with visual feedback

**Using a text-only model will result in poor performance and failed automation tasks.**

## Installation

```bash
# Install with uv
uv sync --extra dev

# Or with pip
pip install -e .
```

## Configuration

### Environment Variables

The agent supports multiple configuration options via environment variables:

**LLM Configuration (Required):**
```bash
export OPENAI_API_KEY="your-api-key"  # Required
export OPENAI_BASE_URL="https://api.openai.com/v1"  # Optional, default: OpenAI
export OPENAI_MODEL_NAME="gpt-4o-mini"  # Optional, default: gpt-4o-mini
                                    # ⚠️ Must be a vision/multimodal model!
```

**Devicebase Configuration (Optional):**
```bash
export DEVICEBASE_BASE_URL="http://localhost:8080"  # Optional
export DEVICEBASE_API_KEY="your-devicebase-key"  # Optional
export DEVICEBASE_DEVICE_SERIAL="your-devicebase-device-serial"  # Optional
```

### Compatible LLM Providers

**⚠️ Important: All models below MUST be vision/multimodal models.**

The agent works with any OpenAI-compatible API that supports vision:

**OpenAI (Recommended):**
```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_MODEL_NAME="gpt-4o"  # Vision model - BEST performance
# or
export OPENAI_MODEL_NAME="gpt-4o-mini"  # Vision model - Good balance
```

**Azure OpenAI:**
```bash
export OPENAI_API_KEY="your-azure-key"
export OPENAI_BASE_URL="https://your-resource.openai.azure.com/openai/deployments/your-deployment"
export OPENAI_MODEL_NAME="gpt-4o"  # Must use vision model deployment
```

**Anthropic Claude (via compatible proxy):**
```bash
export OPENAI_API_KEY="your-anthropic-key"
export OPENAI_BASE_URL="https://api.anthropic.com/v1"
export OPENAI_MODEL_NAME="claude-3-5-sonnet-20241022"  # Vision model
# or
export OPENAI_MODEL_NAME="claude-3-5-sonnet-20250619"  # Latest vision model
```

**Other Providers (Ollama, vLLM, etc.):**
```bash
export OPENAI_API_KEY="any-key"  # Some local servers require this
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_MODEL_NAME="llama3.2-vision"  # ⚠️ Must use vision variant!
```

## Usage

### Basic ReAct Agent

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key"

# Run the example
python example.py

# Or use main.py
python main.py "打开微信给xx发送消息"
```

### With Custom Options

```bash
# Specify model and device
python main.py "Open WeChat and send message to xx" \
  --model gpt-4o \
  --device <serial>

# Disable streaming
python main.py "Task description" --no-stream

# Override LLM configuration
python main.py "Task" \
  --llm-base-url "https://your-api.example.com/v1" \
  --llm-api-key "your-key" \
  --model "custom-model"

# Override devicebase configuration
# visit https://devicebase.cn/ for more information
python main.py "Task" \
  --devicebase-base-url "http://localhost:8080" \
  --devicebase-api-key "devicebase-key"
```

### Programmatic Usage

```python
import os
from agents.agent import Agent

# Using environment variables
agent = Agent()

# Or with explicit configuration
agent = Agent(
    api_key="your-llm-key",
    base_url="https://api.openai.com/v1",
    model="gpt-4o-mini",
    device_serial=None,  # Auto-detect
    devicebase_base_url="http://localhost:8080",
    devicebase_api_key="devicebase-key"
)

# Run task
agent.run("打开微信给xx发送消息", stream=True)
```

## Configuration

For detailed configuration options and examples, see [CONFIGURATION.md](CONFIGURATION.md).

### Quick Configuration

```bash
# Copy and edit environment file
cp .env.example .env
nano .env

# Source the file
source .env

# Run the agent
python main.py "Your task here"
```

### Supported LLM Providers

**⚠️ All models MUST support vision/multimodal capabilities.**

- **OpenAI**: GPT-4o, GPT-4o-mini (both have excellent vision support)
- **Azure OpenAI**: GPT-4o deployments with vision enabled
- **Anthropic Claude**: Claude 3.5 Sonnet (excellent vision capabilities)
- **Ollama**: Use vision model variants (e.g., llama3.2-vision, llava)
- **vLLM**: Deploy vision-enabled models only
- **Any OpenAI-compatible API**: Must support image_url content type

**Text-only models (e.g., GPT-3.5, text-only Llama variants) will NOT work properly.**

See [CONFIGURATION.md](CONFIGURATION.md) for provider-specific examples.

## Visual Context with Screenshots

**⚠️ This feature requires a vision/multimodal model - see configuration requirements above.**

The agent automatically captures screenshots at every step, providing visual context to the LLM:

- **Initial screenshot** captured before starting the task
- **Post-action screenshots** captured after each tool execution
- **Multimodal messages** send screenshots to vision-capable models (GPT-4o, Claude, etc.)

This enables:
- Better decision-making by seeing actual UI
- Improved error detection and recovery
- More robust automation with visual feedback

**Recommended models** (with vision support):
- **GPT-4o** - Best performance, excellent vision understanding
- **GPT-4o-mini** - Good balance of speed and accuracy
- **Claude 3.5 Sonnet** - Excellent vision capabilities, strong reasoning

**❌ Do NOT use:**
- GPT-3.5 or GPT-4 (text-only models)
- Text-only Llama variants
- Any model without vision/multimodal support

See [docs/SCREENSHOT_CONTEXT.md](docs/SCREENSHOT_CONTEXT.md) for details.

## Architecture

```
src/agents/
├── base.py      # Base agent class with OpenAI integration
├── agent.py     # ReAct-style mobile automation agent with screenshot context
└── __init__.py  # Package exports
```

## Development Setup

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
pytest

# Lint and format
ruff check .
ruff check --fix .

# Type check
mypy src/

# Run pre-commit hooks
pre-commit run --all-files
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_base_agent.py
```

## License

MIT
