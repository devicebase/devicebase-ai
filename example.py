"""Simple example of using the ReAct agent.

⚠️ IMPORTANT: This agent requires a vision/multimodal LLM to function properly.
The agent captures screenshots at every step and sends them to the LLM for visual context.

Supported vision models: gpt-4o, gpt-4o-mini, claude-3-5-sonnet, llama3.2-vision
Unsupported (text-only): gpt-3.5-turbo, text-davinci-003, base llama models
"""

import os
from devicebase_ai.agent import Agent


def main():
    """Run a simple example."""
    # Show environment configuration
    print("Environment Configuration:")
    print(f"  OPENAI_API_KEY: {'***' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print(f"  OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')}")
    model_name = os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini')
    print(f"  OPENAI_MODEL_NAME: {model_name}")
    print(f"  DEVICEBASE_BASE_URL: {os.getenv('DEVICEBASE_BASE_URL', 'Not set (using default)')}")
    print(f"  DEVICEBASE_API_KEY: {'***' if os.getenv('DEVICEBASE_API_KEY') else 'Not set'}")
    print()

    # Warn about vision model requirement
    print("⚠️  IMPORTANT: This agent requires a vision/multimodal model!")
    print(f"   Current model: {model_name}")
    print("   Supported models: gpt-4o, gpt-4o-mini, claude-3-5-sonnet, llama3.2-vision")
    print("   Text-only models (gpt-3.5-turbo, etc.) will NOT work properly!")
    print()

    # Ensure API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is required")
        print("\nExample configuration:")
        print("  export OPENAI_API_KEY='your-api-key'")
        print("  export OPENAI_BASE_URL='https://api.openai.com/v1'  # Optional")
        print("  export OPENAI_MODEL_NAME='gpt-4o-mini'  # Optional (must be vision model!)")
        print("  export DEVICEBASE_BASE_URL='http://localhost:8080'  # Optional")
        print("  export DEVICEBASE_API_KEY='your-devicebase-key'  # Optional")
        return

    # Initialize the agent
    print("Initializing ReAct Agent...")
    try:
        agent = Agent()
    except Exception as e:
        print(f"Error initializing agent: {e}")
        return

    # Run a task
    task = "打开微信给xx发送消息"
    print(f"\nTask: {task}\n")

    try:
        result = agent.run(task, stream=True)
        print(f"\nFinal result: {result}")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
