"""Main entry point for the ReAct agent.

⚠️ IMPORTANT: This agent requires a vision/multimodal LLM to function properly.
The agent captures screenshots at every step and sends them to the LLM for visual context.

Supported vision models: gpt-4o, gpt-4o-mini, claude-3-5-sonnet, llama3.2-vision
Unsupported (text-only): gpt-3.5-turbo, text-davinci-003, base llama models
"""

import sys
import argparse
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from project root
_dotenv_path = Path(__file__).parent / ".env"
if _dotenv_path.exists():
    load_dotenv(_dotenv_path)

from devicebase_ai.agent import Agent


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ReAct AI Agent for mobile automation (requires vision/multimodal model)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
⚠️ IMPORTANT: This agent requires a vision/multimodal model to function properly.
The agent captures screenshots at every step for visual context.

Environment Variables:
  LLM Configuration:
    OPENAI_API_KEY          API key for the LLM provider (required)
    OPENAI_BASE_URL         Base URL for the LLM API (default: https://api.openai.com/v1)
    OPENAI_MODEL_NAME       Model name to use (default: gpt-4o-mini)
                            ⚠️ Must be a vision/multimodal model!

  Devicebase Configuration:
    DEVICEBASE_BASE_URL     Base URL for devicebase (optional)
    DEVICEBASE_API_KEY      API key for devicebase (optional)

Examples:
  # Use environment variables
  export OPENAI_API_KEY="your-key"
  python main.py "Open WeChat"

  # Override model (use vision model)
  python main.py "Open WeChat" --model gpt-4o

  # Use custom LLM provider
  python main.py "Task" --llm-base-url "https://api.custom.com/v1"

  # Use with devicebase configuration
  python main.py "Task" --devicebase-base-url "http://localhost:8080"

Recommended Models (with vision support):
  - gpt-4o (best performance)
  - gpt-4o-mini (good balance)
  - claude-3-5-sonnet (excellent vision)

❌ Do NOT use text-only models (gpt-3.5-turbo, text-only llama variants)
        """,
    )
    parser.add_argument("task", nargs="?", help="Task description (e.g., '打开微信给xx发送消息')")
    parser.add_argument("--model", help="Model to use (overrides OPENAI_MODEL_NAME env var)")
    parser.add_argument("--device", help="Device serial number (auto-detect if not specified)")
    parser.add_argument("--llm-base-url", help="LLM API base URL (overrides OPENAI_BASE_URL env var)")
    parser.add_argument("--llm-api-key", help="LLM API key (overrides OPENAI_API_KEY env var)")
    parser.add_argument(
        "--devicebase-base-url", help="Devicebase API base URL (overrides DEVICEBASE_BASE_URL env var)"
    )
    parser.add_argument(
        "--devicebase-api-key", help="Devicebase API key (overrides DEVICEBASE_API_KEY env var)"
    )
    parser.add_argument("--no-stream", action="store_true", help="Disable streaming output")

    args = parser.parse_args()

    # Get task from argument or prompt
    task = args.task
    if not task:
        task = input("Enter task: ")

    try:
        # Initialize agent with all configurations
        agent = Agent(
            api_key=args.llm_api_key,
            base_url=args.llm_base_url,
            model=args.model,
            device_serial=args.device,
            devicebase_base_url=args.devicebase_base_url,
            devicebase_api_key=args.devicebase_api_key,
        )

        # Run the agent
        agent.run(task, stream=not args.no_stream)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
