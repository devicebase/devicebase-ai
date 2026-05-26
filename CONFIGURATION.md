# Configuration Guide

This guide explains how to configure the ReAct AI Agent with different LLM providers and devicebase settings.

## Quick Start

```bash
# Copy example environment file
cp .env.example .env

# Edit with your configuration
nano .env

# Run the agent
python main.py "Open WeChat"
```

## Environment Variables

### LLM Configuration (Required)

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENAI_API_KEY` | API key for your LLM provider | Required | `sk-...` |
| `OPENAI_BASE_URL` | Base URL for the LLM API | `https://api.openai.com/v1` | `https://api.openai.com/v1` |
| `OPENAI_MODEL_NAME` | Model name to use | `gpt-4o-mini` | `gpt-4o-mini` |

### Devicebase Configuration (Optional)

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DEVICEBASE_BASE_URL` | Base URL for devicebase server | None | `https://api.devicebase.cn` |
| `DEVICEBASE_API_KEY` | API key for devicebase | None | `your-devicebase-api-key` |

## LLM Provider Examples

### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_MODEL_NAME="gpt-4o-mini"
```

### Azure OpenAI

```bash
export OPENAI_API_KEY="your-azure-key"
export OPENAI_BASE_URL="https://your-resource.openai.azure.com/openai/deployments/your-deployment"
export OPENAI_MODEL_NAME="gpt-4o"
```

### Anthropic Claude (via compatible proxy)

```bash
export OPENAI_API_KEY="sk-ant-..."
export OPENAI_BASE_URL="https://api.anthropic.com/v1"
export OPENAI_MODEL_NAME="claude-3-5-sonnet-20241022"
```

### Ollama (Local Models)

```bash
export OPENAI_API_KEY="any-key"
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_MODEL_NAME="llama3.2"
```

### vLLM (Local Models)

```bash
export OPENAI_API_KEY="any-key"
export OPENAI_BASE_URL="http://localhost:8000/v1"
export OPENAI_MODEL_NAME="meta-llama/Llama-3.2-3B-Instruct"
```

### Custom Provider

Any OpenAI-compatible API:

```bash
export OPENAI_API_KEY="your-custom-key"
export OPENAI_BASE_URL="https://your-custom-provider.com/v1"
export OPENAI_MODEL_NAME="custom-model-name"
```

## Command-Line Usage

### Basic Usage

```bash
# Using environment variables
python main.py "Open WeChat and send message"

# Specify model explicitly
python main.py "Task" --model gpt-4o

# Specify device
python main.py "Task" --device emulator-5554
```

### Override Configuration

```bash
# Override LLM configuration
python main.py "Task" \
  --llm-base-url "https://custom.api.com/v1" \
  --llm-api-key "custom-key" \
  --model "custom-model"

# Override devicebase configuration
python main.py "Task" \
  --devicebase-base-url "https://api.devicebase.cn" \
  --devicebase-api-key "devicebase-api-key"
```

### Disable Streaming

```bash
python main.py "Task" --no-stream
```

## Programmatic Usage

### Using Environment Variables

```python
from agents.agent import Agent

# All configuration from environment variables
agent = Agent()
agent.run("Open WeChat")
```

### Explicit Configuration

```python
from agents.agent import Agent

agent = Agent(
    api_key="your-llm-key",
    base_url="https://api.openai.com/v1",
    model="gpt-4o-mini",
    device_serial=None,  # Auto-detect
    devicebase_base_url="https://api.devicebase.cn",
    devicebase_api_key="devicebase-api-key"
)

agent.run("Open WeChat")
```

### Mixed Configuration

```python
import os
from agents.agent import Agent

# LLM from environment, devicebase explicit
agent = Agent(
    devicebase_base_url="https://api.devicebase.cn",
    devicebase_api_key="devicebase-api-key"
)

# LLM explicit, devicebase from environment
agent = Agent(
    api_key="your-llm-key",
    model="gpt-4o"
)
```

## Troubleshooting

### LLM Connection Issues

1. **Check API key**: Ensure `OPENAI_API_KEY` is set correctly
2. **Check base URL**: Verify `OPENAI_BASE_URL` is accessible
3. **Check model name**: Ensure `OPENAI_MODEL_NAME` is supported by your provider

```bash
# Test configuration
python -c "import os; print(f'API Key: {os.getenv(\"OPENAI_API_KEY\", \"Not set\")}')"
python -c "import os; print(f'Base URL: {os.getenv(\"OPENAI_BASE_URL\", \"Not set\")}')"
python -c "import os; print(f'Model: {os.getenv(\"OPENAI_MODEL_NAME\", \"Not set\")}')"
```

### Devicebase Connection Issues

1. **Check devicebase server**: Ensure devicebase server is running
2. **Check device connection**: Verify device is connected via ADB
3. **Check API key**: If authentication is enabled, set `DEVICEBASE_API_KEY`

```bash
# Test devicebase connection
curl https://api.devicebase.cn/v1/devices
```

### Model-Specific Issues

Different models may require different formats. If you encounter issues:

1. **OpenAI models**: Use `gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo`
2. **Azure models**: Use your deployment name as the model
3. **Anthropic models**: Ensure you're using a compatible proxy
4. **Local models**: Check that the model is downloaded and running

## Examples

See [examples/config_examples.py](examples/config_examples.py) for complete examples of different configurations.
