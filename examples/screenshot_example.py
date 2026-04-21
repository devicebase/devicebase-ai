"""Example demonstrating screenshot context feature."""

import os
from agents.agent import Agent


def main():
    """Demonstrate agent with automatic screenshot capture."""

    # Check environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
        print("\nFor best results, use a vision-capable model:")
        print("  export OPENAI_MODEL_NAME='gpt-4o'  # or 'gpt-4o-mini'")
        return

    # Show current configuration
    print("="*60)
    print("Screenshot Context Example")
    print("="*60)
    print(f"Model: {os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini')}")
    print(f"Device: Auto-detect")
    print(f"\nNote: This example will:")
    print("  1. Capture initial screenshot")
    print("  2. Execute actions with visual context")
    print("  3. Capture screenshot after each action")
    print("  4. LLM will see screenshots to make decisions")
    print("="*60)
    print()

    # Initialize agent
    print("Initializing agent...")
    agent = Agent()

    # Run a simple task
    task = "Launch the settings app"
    print(f"\nTask: {task}\n")

    result = agent.run(task, stream=True)

    print(f"\n{'='*60}")
    print("Example completed!")
    print(f"{'='*60}")
    print(f"\nResult: {result}")
    print("\nKey observations:")
    print("  - Screenshots were captured at each step")
    print("  - LLM used visual context to navigate")
    print("  - Check console output for [Screenshot captured] messages")


def example_with_comparison():
    """Compare with and without visual context."""

    print("\n" + "="*60)
    print("Comparison: Vision vs Text-Only")
    print("="*60)

    print("\nVision-capable models (Recommended):")
    print("  - GPT-4o: Best visual understanding")
    print("  - GPT-4o-mini: Good balance of speed and vision")
    print("  - Claude 3.5 Sonnet: Excellent visual reasoning")
    print("\n  These models can:")
    print("  ✓ See actual UI elements")
    print("  ✓ Identify icons by appearance")
    print("  ✓ Read text from screenshots")
    print("  ✓ Handle complex layouts")

    print("\nText-only models (Limited):")
    print("  - GPT-4, GPT-3.5")
    print("\n  These models:")
    print("  ✗ Cannot see screenshots")
    print("  ✗ Rely only on screen hierarchy")
    print("  ✗ May struggle with visual elements")

    print("\nRecommendation: Use GPT-4o-mini for best balance")
    print("="*60)


if __name__ == "__main__":
    main()

    # Show comparison
    example_with_comparison()

    print("\nFor more details, see: docs/SCREENSHOT_CONTEXT.md")
