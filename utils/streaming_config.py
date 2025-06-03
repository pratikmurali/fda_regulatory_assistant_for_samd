"""
Streaming Configuration for FDA Regulatory Assistant

This module provides configuration options for adjusting streaming behavior
in the Chainlit UI to optimize user experience.
"""

# =============================================================================
# Streaming Speed Configuration
# =============================================================================

# Character-by-character streaming delay (in seconds)
# Lower values = faster streaming, higher values = slower streaming
CHAR_DELAY = 0.005  # 5ms delay (default: fast but visible)

# Alternative speed presets:
SPEED_PRESETS = {
    "instant": 0.0,  # No delay - fastest possible
    "very_fast": 0.001,  # 1ms delay
    "fast": 0.005,  # 5ms delay (current setting)
    "normal": 0.01,  # 10ms delay (original setting)
    "slow": 0.02,  # 20ms delay
    "very_slow": 0.05,  # 50ms delay
}

# =============================================================================
# Streaming Mode Configuration
# =============================================================================

# Streaming granularity options
STREAMING_MODES = {
    "character": "char",  # Character-by-character (smoothest)
    "word": "word",  # Word-by-word (faster)
    "sentence": "sentence",  # Sentence-by-sentence (fastest)
    "chunk": "chunk",  # Custom chunk size
}

# Current streaming mode
STREAMING_MODE = "character"  # Default: character-by-character

# Word-by-word streaming settings
WORD_DELAY = 0.05  # 50ms delay between words

# Sentence-by-sentence streaming settings
SENTENCE_DELAY = 0.2  # 200ms delay between sentences

# Custom chunk size (for chunk mode)
CHUNK_SIZE = 10  # Characters per chunk
CHUNK_DELAY = 0.02  # 20ms delay between chunks

# =============================================================================
# Advanced Streaming Options
# =============================================================================

# Adaptive streaming: adjust speed based on content length
ADAPTIVE_STREAMING = False

# Speed multipliers for different content types
CONTENT_SPEED_MULTIPLIERS = {
    "progress_indicators": 1.0,  # Normal speed for progress updates
    "main_content": 1.0,  # Normal speed for main response
    "sources": 0.5,  # Slower for sources (more readable)
    "headers": 0.8,  # Slightly slower for section headers
}

# Minimum and maximum delays for adaptive streaming
MIN_DELAY = 0.001  # 1ms minimum
MAX_DELAY = 0.02  # 20ms maximum

# =============================================================================
# Utility Functions
# =============================================================================


def get_streaming_delay(content_type: str = "main_content") -> float:
    """
    Get the appropriate streaming delay for content type.

    Args:
        content_type: Type of content being streamed

    Returns:
        Delay in seconds
    """
    base_delay = CHAR_DELAY
    multiplier = CONTENT_SPEED_MULTIPLIERS.get(content_type, 1.0)

    if ADAPTIVE_STREAMING:
        adjusted_delay = base_delay * multiplier
        return max(MIN_DELAY, min(MAX_DELAY, adjusted_delay))

    return base_delay


def set_speed_preset(preset_name: str) -> None:
    """
    Set streaming speed using a preset.

    Args:
        preset_name: Name of the speed preset
    """
    global CHAR_DELAY
    if preset_name in SPEED_PRESETS:
        CHAR_DELAY = SPEED_PRESETS[preset_name]
        print(f"✅ Streaming speed set to '{preset_name}' ({CHAR_DELAY}s delay)")
    else:
        available = ", ".join(SPEED_PRESETS.keys())
        print(f"❌ Unknown preset '{preset_name}'. Available: {available}")


def get_current_config() -> dict:
    """
    Get current streaming configuration.

    Returns:
        Dictionary with current settings
    """
    return {
        "char_delay": CHAR_DELAY,
        "streaming_mode": STREAMING_MODE,
        "adaptive_streaming": ADAPTIVE_STREAMING,
        "word_delay": WORD_DELAY,
        "sentence_delay": SENTENCE_DELAY,
        "chunk_size": CHUNK_SIZE,
        "chunk_delay": CHUNK_DELAY,
    }


def print_speed_options():
    """Print available speed options for easy reference."""
    print("🚀 Streaming Speed Options:")
    print("=" * 40)

    print("\n📊 Speed Presets:")
    for name, delay in SPEED_PRESETS.items():
        chars_per_sec = 1 / delay if delay > 0 else "∞"
        print(f"   {name:10} - {delay:5.3f}s delay ({chars_per_sec} chars/sec)")

    print(f"\n⚡ Current Setting: {CHAR_DELAY}s delay")

    print("\n🔧 To Change Speed:")
    print("   1. Edit CHAR_DELAY in streaming_config.py")
    print("   2. Or use: set_speed_preset('fast')")
    print("   3. Or modify delays directly in graph/workflow.py")

    print("\n💡 Recommendations:")
    print("   - 'instant' (0.0s): Fastest, no streaming effect")
    print("   - 'very_fast' (0.001s): Very fast but still visible")
    print("   - 'fast' (0.005s): Good balance (current)")
    print("   - 'normal' (0.01s): Original setting")
    print("   - 'slow' (0.02s): More readable for long responses")


# =============================================================================
# Quick Speed Test
# =============================================================================


async def test_streaming_speed():
    """Test current streaming speed with sample text."""
    import asyncio

    sample_text = "This is a test of the current streaming speed configuration."
    print(f"🧪 Testing streaming speed (delay: {CHAR_DELAY}s)")
    print("Sample text:", sample_text)
    print("Streaming:")

    start_time = asyncio.get_event_loop().time()

    for i, char in enumerate(sample_text):
        print(char, end="", flush=True)
        if CHAR_DELAY > 0:
            await asyncio.sleep(CHAR_DELAY)

    end_time = asyncio.get_event_loop().time()
    total_time = end_time - start_time
    chars_per_sec = len(sample_text) / total_time if total_time > 0 else float("inf")

    print("\n\n📊 Results:")
    print(f"   Characters: {len(sample_text)}")
    print(f"   Time: {total_time:.2f}s")
    print(f"   Speed: {chars_per_sec:.1f} chars/sec")


if __name__ == "__main__":
    print_speed_options()

    # Example usage:
    # set_speed_preset("very_fast")
    # print(get_current_config())
