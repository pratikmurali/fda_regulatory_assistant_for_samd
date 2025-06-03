"""
Test script to verify proper spacing between response and sources section.
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from graph.workflow import process_user_request
from ragchains.chain_manager import get_chain_manager


async def test_sources_spacing():
    """Test that there's proper spacing between response and sources."""
    print("🧪 Testing Sources Spacing")
    print("=" * 50)

    # Pre-warm chains
    chain_manager = get_chain_manager()
    await chain_manager.prewarm_chains()

    question = "What is SOUP documentation for medical devices?"
    print(f"Question: {question}")
    print("\nResponse with sources spacing:")
    print("-" * 50)

    response_chunks = []
    async for chunk in process_user_request(
        user_input=question, uploaded_files=None, stream=True
    ):
        response_chunks.append(chunk)
        print(chunk, end="", flush=True)

    print("\n" + "-" * 50)

    # Analyze the full response
    full_response = "".join(response_chunks)

    # Check for proper spacing patterns
    has_sources = "📚 **Sources:**" in full_response

    if has_sources:
        # Find the sources section
        sources_index = full_response.find("📚 **Sources:**")

        # Check what comes before the sources section
        before_sources = full_response[:sources_index]

        # Count newlines before sources
        trailing_newlines = len(before_sources) - len(before_sources.rstrip("\n"))

        print(f"✅ Sources section found: {has_sources}")
        print(f"📊 Newlines before sources: {trailing_newlines}")
        print("🔍 Last 50 chars before sources:")
        print(repr(before_sources[-50:]))

        # Check if spacing looks good (should have at least 2 newlines for proper separation)
        good_spacing = trailing_newlines >= 2
        print(f"✅ Good spacing: {good_spacing}")

        return good_spacing
    else:
        print("❌ No sources section found")
        return False


async def demonstrate_expected_format():
    """Show what the expected format should look like."""
    print("\n🎯 Expected Format")
    print("=" * 50)

    expected_format = """**SOUP Documentation for Medical Devices**

SOUP stands for "Software of Unknown Provenance." In the context of medical devices, SOUP refers to software components that are not developed by the device manufacturer and whose development processes, quality controls, and security measures are not fully known or documented.

Key requirements include:
1. Documentation of all SOUP components
2. Risk assessment for each component
3. Cybersecurity considerations

📚 **Sources:** 2 FDA guidance documents referenced

1. **Cybersecurity in Medical Devices** - Page 15
2. **Premarket Submissions for Management of Cybersecurity** - Page 8"""

    print("Expected spacing pattern:")
    print(expected_format)

    print("\n🔍 Analysis:")
    sources_index = expected_format.find("📚 **Sources:**")
    before_sources = expected_format[:sources_index]
    trailing_newlines = len(before_sources) - len(before_sources.rstrip("\n"))

    print(f"   - Newlines before sources: {trailing_newlines}")
    print(f"   - Last chars before sources: {repr(before_sources[-10:])}")
    print("   - This creates proper visual separation")


async def main():
    """Main test function."""
    print("🚀 Testing Sources Section Spacing")
    print("=" * 60)

    # Test actual spacing
    spacing_good = await test_sources_spacing()

    # Show expected format
    await demonstrate_expected_format()

    print("\n" + "=" * 60)
    print("🏁 Test Results:")
    print(f"   Sources Spacing: {'✅ GOOD' if spacing_good else '❌ NEEDS FIX'}")

    if spacing_good:
        print("\n🎉 Perfect! Sources section has proper spacing.")
        print("💡 The response and sources are now properly separated.")
    else:
        print("\n⚠️  Sources spacing needs adjustment.")

    print("\n📋 Expected Pattern:")
    print("   [Response content]")
    print("   ")  # Empty line
    print("   📚 **Sources:** ...")


if __name__ == "__main__":
    asyncio.run(main())
