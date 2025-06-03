"""
Test script to compare different streaming speeds.

This script helps you find the optimal streaming speed for your preference.
"""

import asyncio
import time
from streaming_config import SPEED_PRESETS


async def compare_streaming_speeds():
    """Compare different streaming speeds side by side."""
    print("🚀 Streaming Speed Comparison")
    print("=" * 60)

    sample_text = (
        "SOUP documentation is essential for medical device cybersecurity compliance."
    )

    for preset_name, delay in SPEED_PRESETS.items():
        print(f"\n🔧 Testing '{preset_name}' speed (delay: {delay}s)")
        print("-" * 40)

        start_time = time.time()

        for char in sample_text:
            print(char, end="", flush=True)
            if delay > 0:
                await asyncio.sleep(delay)

        end_time = time.time()
        total_time = end_time - start_time
        chars_per_sec = (
            len(sample_text) / total_time if total_time > 0 else float("inf")
        )

        print(f"\n   ⏱️  Time: {total_time:.2f}s | Speed: {chars_per_sec:.1f} chars/sec")

        # Pause between tests
        await asyncio.sleep(1)


async def test_recommended_speeds():
    """Test the most commonly used speeds."""
    print("\n🎯 Recommended Speed Tests")
    print("=" * 60)

    recommended = {
        "very_fast": 0.001,  # Very responsive
        "fast": 0.005,  # Current setting
        "normal": 0.01,  # Original setting
    }

    sample = "What are the cybersecurity requirements for Class II medical devices?"

    for name, delay in recommended.items():
        print(f"\n✨ {name.upper()} ({delay}s delay):")
        print("   ", end="")

        start_time = time.time()

        for char in sample:
            print(char, end="", flush=True)
            if delay > 0:
                await asyncio.sleep(delay)

        end_time = time.time()
        total_time = end_time - start_time

        print(f"\n   📊 Completed in {total_time:.1f}s")
        await asyncio.sleep(0.5)


def print_speed_recommendations():
    """Print speed recommendations for different use cases."""
    print("\n💡 Speed Recommendations")
    print("=" * 60)

    recommendations = [
        ("instant", "0.0s", "Demo/testing - no streaming effect"),
        ("very_fast", "0.001s", "Impatient users - very responsive"),
        ("fast", "0.005s", "Most users - good balance (CURRENT)"),
        ("normal", "0.01s", "Careful readers - original setting"),
        ("slow", "0.02s", "Detailed reading - very deliberate"),
    ]

    print("Speed        Delay    Use Case")
    print("-" * 50)
    for speed, delay, use_case in recommendations:
        print(f"{speed:12} {delay:8} {use_case}")

    print("\n🔧 How to Change Speed:")
    print("1. Edit graph/workflow.py:")
    print("   Change: await asyncio.sleep(0.005)")
    print("   To:     await asyncio.sleep(0.001)  # for very_fast")

    print("\n2. Or use streaming_config.py:")
    print("   set_speed_preset('very_fast')")

    print("\n3. For instant streaming (no delay):")
    print("   Comment out: # await asyncio.sleep(0.005)")


async def interactive_speed_test():
    """Interactive test to find your preferred speed."""
    print("\n🎮 Interactive Speed Test")
    print("=" * 60)

    speeds = [
        ("Instant", 0.0),
        ("Very Fast", 0.001),
        ("Fast", 0.005),
        ("Normal", 0.01),
        ("Slow", 0.02),
    ]

    sample = "This is a sample response about FDA regulatory requirements."

    print("Watch each speed and note which feels best for you:\n")

    for i, (name, delay) in enumerate(speeds, 1):
        print(f"{i}. {name} ({delay}s delay):")
        print("   ", end="")

        for char in sample:
            print(char, end="", flush=True)
            if delay > 0:
                await asyncio.sleep(delay)

        print("\n")
        await asyncio.sleep(1)

    print("🎯 Which speed felt best?")
    print("1. Instant - No streaming effect")
    print("2. Very Fast - Barely visible streaming")
    print("3. Fast - Quick but smooth (current)")
    print("4. Normal - Comfortable reading pace")
    print("5. Slow - Deliberate, easy to follow")


async def main():
    """Main test function."""
    print("🚀 FDA Regulatory Assistant - Streaming Speed Tests")
    print("=" * 70)

    # Show current configuration
    print("Current streaming delay: 0.005s (fast)")
    print("This is 2x faster than the original 0.01s setting")

    # Run tests
    await compare_streaming_speeds()
    await test_recommended_speeds()
    print_speed_recommendations()
    await interactive_speed_test()

    print("\n" + "=" * 70)
    print("🏁 Speed Test Complete!")
    print("\n💡 Quick Summary:")
    print("   - Current: 0.005s (fast) - good for most users")
    print("   - Faster: 0.001s (very_fast) - for impatient users")
    print("   - Instant: 0.0s - no streaming effect")
    print("\n🔧 To change: Edit the delays in graph/workflow.py")


if __name__ == "__main__":
    asyncio.run(main())
