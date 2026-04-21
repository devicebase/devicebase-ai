"""Configuration examples for different LLM providers."""

import os
from agents.agent import Agent


def example_openai():
    """Example using OpenAI."""
    print("=== OpenAI Example ===")

    agent = Agent(
        api_key="sk-...",
        base_url="https://api.openai.com/v1",
        model="gpt-4o-mini",
    )

    # Or use environment variables:
    # export OPENAI_API_KEY="sk-..."
    # export OPENAI_BASE_URL="https://api.openai.com/v1"
    # export OPENAI_MODEL_NAME="gpt-4o-mini"
    # agent = Agent()


def example_azure():
    """Example using Azure OpenAI."""
    print("=== Azure OpenAI Example ===")

    agent = Agent(
        api_key="your-azure-key",
        base_url="https://your-resource.openai.azure.com/openai/deployments/your-deployment",
        model="gpt-4o",
    )


def example_anthropic():
    """Example using Anthropic Claude (via compatible proxy)."""
    print("=== Anthropic Example ===")

    agent = Agent(
        api_key="sk-ant-...",
        base_url="https://api.anthropic.com/v1",
        model="claude-3-5-sonnet-20241022",
    )


def example_ollama():
    """Example using Ollama for local models."""
    print("=== Ollama Example ===")

    agent = Agent(
        api_key="any-key",  # Ollama doesn't require a real key
        base_url="http://localhost:11434/v1",
        model="llama3.2",
    )


def example_custom_provider():
    """Example using a custom OpenAI-compatible provider."""
    print("=== Custom Provider Example ===")

    agent = Agent(
        api_key="custom-key",
        base_url="https://your-custom-provider.com/v1",
        model="custom-model-name",
    )


def example_with_devicebase():
    """Example with custom devicebase configuration."""
    print("=== Devicebase Configuration Example ===")

    agent = Agent(
        # LLM configuration (using env vars)
        # api_key, base_url, model will be read from:
        # OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL_NAME
        #
        # Devicebase configuration
        devicebase_base_url="http://localhost:8080",
        devicebase_api_key="devicebase-key",
        device_serial=None,  # Auto-detect
    )

    # Or use environment variables:
    # export DEVICEBASE_BASE_URL="http://localhost:8080"
    # export DEVICEBASE_API_KEY="devicebase-key"
    # agent = Agent()


def example_all_env_vars():
    """Example using all environment variables."""
    print("=== All Environment Variables Example ===")

    # Set up environment variables
    os.environ["OPENAI_API_KEY"] = "your-api-key"
    os.environ["OPENAI_BASE_URL"] = "https://api.openai.com/v1"
    os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"
    os.environ["DEVICEBASE_BASE_URL"] = "http://localhost:8080"
    os.environ["DEVICEBASE_API_KEY"] = "devicebase-key"

    # Initialize with all config from environment
    agent = Agent()

    # Run a task
    agent.run("Launch the calculator app")


if __name__ == "__main__":
    print("Configuration Examples\n")
    print("Choose an example:")
    print("1. OpenAI")
    print("2. Azure OpenAI")
    print("3. Anthropic")
    print("4. Ollama (local)")
    print("5. Custom provider")
    print("6. With devicebase config")
    print("7. All environment variables")

    # Uncomment the example you want to run:
    # example_openai()
    # example_azure()
    # example_anthropic()
    # example_ollama()
    # example_custom_provider()
    # example_with_devicebase()
    # example_all_env_vars()
