"""
Test script to demonstrate word-by-word streaming vs character-by-character streaming.

This shows the speed improvement of the new word-by-word streaming.
"""

import asyncio
import time


async def test_character_streaming(text: str, delay: float = 0.005):
    """Test character-by-character streaming (old method)."""
    print("🔤 Character-by-Character Streaming (OLD):")
    print("   ", end="")

    start_time = time.time()

    for char in text:
        print(char, end="", flush=True)
        await asyncio.sleep(delay)

    end_time = time.time()
    total_time = end_time - start_time

    print(
        f"\n   ⏱️  Time: {total_time:.2f}s | Speed: {len(text) / total_time:.1f} chars/sec"
    )
    return total_time


async def test_word_streaming(text: str, delay: float = 0.05):
    """Test word-by-word streaming (new method)."""
    print("\n📝 Word-by-Word Streaming (NEW):")
    print("   ", end="")

    start_time = time.time()

    words = text.split()
    for word in words:
        print(word + " ", end="", flush=True)
        await asyncio.sleep(delay)

    end_time = time.time()
    total_time = end_time - start_time

    print(
        f"\n   ⏱️  Time: {total_time:.2f}s | Speed: {len(words) / total_time:.1f} words/sec"
    )
    return total_time


async def compare_streaming_methods():
    """Compare character vs word streaming side by side."""
    print("🚀 Streaming Method Comparison")
    print("=" * 60)

    # Sample FDA response
    sample_text = """SOUP Documentation for Medical Devices

SOUP stands for "Software of Unknown Provenance." In the context of medical devices, SOUP refers to software components that are not developed by the device manufacturer and whose development processes, quality controls, and security measures are not fully known or documented. This can include third-party libraries, open-source software, or any software that is integrated into a medical device."""

    print(
        f"Sample text: {len(sample_text)} characters, {len(sample_text.split())} words"
    )
    print("=" * 60)

    # Test character streaming
    char_time = await test_character_streaming(sample_text, 0.005)

    await asyncio.sleep(1)  # Pause between tests

    # Test word streaming
    word_time = await test_word_streaming(sample_text, 0.05)

    # Calculate improvement
    speedup = char_time / word_time if word_time > 0 else float("inf")

    print("\n" + "=" * 60)
    print("📊 Performance Comparison:")
    print(f"   Character streaming: {char_time:.2f}s")
    print(f"   Word streaming:      {word_time:.2f}s")
    print(f"   Speed improvement:   {speedup:.1f}x faster! 🚀")

    return speedup


async def test_different_word_delays():
    """Test different delays for word streaming."""
    print("\n🔧 Testing Different Word Delays")
    print("=" * 60)

    sample = "What are the cybersecurity requirements for Class II medical devices with AI/ML capabilities?"
    delays = [0.01, 0.03, 0.05, 0.1, 0.2]

    for delay in delays:
        print(f"\n⏱️  {delay}s delay between words:")
        print("   ", end="")

        start_time = time.time()
        words = sample.split()

        for word in words:
            print(word + " ", end="", flush=True)
            await asyncio.sleep(delay)

        end_time = time.time()
        total_time = end_time - start_time
        words_per_sec = len(words) / total_time

        print(f"\n   📊 {total_time:.1f}s total | {words_per_sec:.1f} words/sec")


async def simulate_real_response():
    """Simulate a real FDA response with word streaming."""
    print("\n🎯 Simulated Real Response (Word Streaming)")
    print("=" * 60)

    response_parts = [
        "🤔 **Analyzing your question...**\n\n",
        "🔄 **Supervisor** is analyzing...\n\n",
        "📋 **Final Analysis:**\n\n",
        "**SOUP Documentation for Medical Devices**\n\n",
        "SOUP stands for Software of Unknown Provenance. In the context of medical devices, SOUP refers to software components that are not developed by the device manufacturer and whose development processes, quality controls, and security measures are not fully known or documented.\n\n",
        "📚 **Sources:** 2 FDA guidance documents referenced\n\n",
        "1. **Cybersecurity in Medical Devices** - Page 15\n",
        "2. **Premarket Submissions for Management of Cybersecurity** - Page 8\n",
    ]

    total_start = time.time()

    for part in response_parts:
        if part.startswith(("🤔", "🔄", "📋", "📚")):
            # Progress indicators - show immediately
            print(part, end="")
        else:
            # Main content - stream word by word
            words = part.split()
            for word in words:
                print(word + " ", end="", flush=True)
                await asyncio.sleep(0.05)

        await asyncio.sleep(0.2)  # Small pause between sections

    total_time = time.time() - total_start
    print(f"\n\n📊 Total response time: {total_time:.1f}s")


async def main():
    """Main test function."""
    print("🚀 Word-by-Word Streaming Test")
    print("=" * 70)

    # Compare methods
    speedup = await compare_streaming_methods()

    # Test different delays
    await test_different_word_delays()

    # Simulate real response
    await simulate_real_response()

    print("\n" + "=" * 70)
    print("🏁 Test Complete!")
    print(f"\n✅ Word streaming is {speedup:.1f}x faster than character streaming")
    print("💡 Benefits of word-by-word streaming:")
    print("   - Much faster overall response time")
    print("   - Still maintains streaming visual effect")
    print("   - More natural reading rhythm")
    print("   - Better for longer responses")

    print("\n🔧 Current Configuration:")
    print("   - Method: Word-by-word streaming")
    print("   - Delay: 0.05s between words")
    print("   - Speed: ~20 words per second")


if __name__ == "__main__":
    asyncio.run(main())
