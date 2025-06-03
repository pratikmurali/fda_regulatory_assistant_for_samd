"""
Test script to verify the streaming fix works correctly.

This script tests:
- Token-by-token streaming in question answering
- Character-by-character streaming in responses
- Proper streaming behavior in Chainlit
"""

import asyncio
import sys
import os
import time

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from graph.workflow import process_user_request
from ragchains.chain_manager import get_chain_manager


async def test_streaming_question():
    """Test streaming for a simple question."""
    print("🧪 Testing Streaming for Question Answering")
    print("=" * 50)

    # Pre-warm chains
    chain_manager = get_chain_manager()
    await chain_manager.prewarm_chains()

    question = "What is SOUP documentation for medical devices?"
    print(f"Question: {question}")
    print("\nStreaming response:")
    print("-" * 30)

    start_time = time.time()
    chunk_count = 0
    total_chars = 0

    async for chunk in process_user_request(
        user_input=question, uploaded_files=None, stream=True
    ):
        chunk_count += 1
        total_chars += len(chunk)

        # Print chunk with timing info
        elapsed = time.time() - start_time
        print(
            f"[{elapsed:.2f}s] Chunk {chunk_count}: '{chunk[:50]}{'...' if len(chunk) > 50 else ''}'"
        )

        # Simulate real-time processing
        await asyncio.sleep(0.1)

    end_time = time.time()
    total_time = end_time - start_time

    print("-" * 30)
    print("✅ Streaming completed!")
    print("📊 Stats:")
    print(f"   - Total chunks: {chunk_count}")
    print(f"   - Total characters: {total_chars}")
    print(f"   - Total time: {total_time:.2f}s")
    print(f"   - Avg chars per chunk: {total_chars / chunk_count:.1f}")
    print(f"   - Streaming rate: {total_chars / total_time:.1f} chars/sec")

    # Check if streaming is working properly
    if chunk_count > 10:  # Should have many small chunks for good streaming
        print("🎉 Streaming appears to be working correctly!")
        return True
    else:
        print("⚠️  Streaming might not be optimal - too few chunks")
        return False


async def test_streaming_cybersecurity():
    """Test streaming for a cybersecurity question."""
    print("\n🧪 Testing Cybersecurity Streaming")
    print("=" * 50)

    question = "What are the cybersecurity requirements for Class II medical devices?"
    print(f"Question: {question}")
    print("\nStreaming response:")
    print("-" * 30)

    start_time = time.time()
    response_parts = []

    async for chunk in process_user_request(
        user_input=question, uploaded_files=None, stream=True
    ):
        response_parts.append(chunk)
        # Show progress indicators
        if "🔒" in chunk or "📋" in chunk or "📚" in chunk:
            elapsed = time.time() - start_time
            print(f"[{elapsed:.2f}s] Progress: {chunk.strip()}")

    full_response = "".join(response_parts)

    print("-" * 30)
    print("✅ Cybersecurity streaming completed!")
    print(f"📊 Response length: {len(full_response)} characters")

    # Check for sources
    has_sources = "Sources:" in full_response
    print(f"📚 Sources included: {has_sources}")

    return has_sources


async def test_streaming_performance():
    """Test streaming performance and behavior."""
    print("\n🧪 Testing Streaming Performance")
    print("=" * 50)

    questions = [
        "What is FDA guidance for AI/ML medical devices?",
        "What cybersecurity documentation is required?",
        "What are 510K submission requirements?",
    ]

    results = []

    for i, question in enumerate(questions, 1):
        print(f"\nTest {i}/3: {question[:40]}...")

        start_time = time.time()
        chunk_count = 0

        async for chunk in process_user_request(
            user_input=question, uploaded_files=None, stream=True
        ):
            chunk_count += 1
            # Don't print all chunks to avoid spam
            if chunk_count % 10 == 0:
                elapsed = time.time() - start_time
                print(f"   [{elapsed:.1f}s] {chunk_count} chunks processed...")

        total_time = time.time() - start_time
        results.append(
            {
                "question": question,
                "chunks": chunk_count,
                "time": total_time,
                "chunks_per_sec": chunk_count / total_time,
            }
        )

        print(f"   ✅ Completed: {chunk_count} chunks in {total_time:.2f}s")

    print("\n📊 Performance Summary:")
    for i, result in enumerate(results, 1):
        print(
            f"   Test {i}: {result['chunks']} chunks, {result['time']:.2f}s, {result['chunks_per_sec']:.1f} chunks/sec"
        )

    avg_chunks_per_sec = sum(r["chunks_per_sec"] for r in results) / len(results)
    print(f"   Average: {avg_chunks_per_sec:.1f} chunks/sec")

    # Good streaming should have reasonable chunk rate
    if avg_chunks_per_sec > 5:
        print("🎉 Streaming performance looks good!")
        return True
    else:
        print("⚠️  Streaming might be too slow")
        return False


async def test_chainlit_compatibility():
    """Test compatibility with Chainlit streaming."""
    print("\n🧪 Testing Chainlit Compatibility")
    print("=" * 50)

    print("Testing if chunks are suitable for Chainlit streaming...")

    question = "What is required for medical device cybersecurity?"
    chunks = []

    async for chunk in process_user_request(
        user_input=question, uploaded_files=None, stream=True
    ):
        chunks.append(chunk)

    # Analyze chunk characteristics
    single_char_chunks = sum(1 for chunk in chunks if len(chunk) == 1)
    multi_char_chunks = sum(1 for chunk in chunks if len(chunk) > 1)
    empty_chunks = sum(1 for chunk in chunks if len(chunk) == 0)

    print("📊 Chunk Analysis:")
    print(f"   - Total chunks: {len(chunks)}")
    print(f"   - Single character chunks: {single_char_chunks}")
    print(f"   - Multi character chunks: {multi_char_chunks}")
    print(f"   - Empty chunks: {empty_chunks}")

    # Check for proper streaming characteristics
    has_progress_indicators = any("🔄" in chunk or "✅" in chunk for chunk in chunks)
    has_final_response = any("📋" in chunk for chunk in chunks)
    has_sources = any("📚" in chunk for chunk in chunks)

    print("📋 Content Analysis:")
    print(f"   - Progress indicators: {has_progress_indicators}")
    print(f"   - Final response section: {has_final_response}")
    print(f"   - Sources section: {has_sources}")

    # Good for Chainlit if we have character-level streaming
    if single_char_chunks > 100:  # Should have many single character chunks
        print("🎉 Streaming is optimized for Chainlit!")
        return True
    else:
        print("⚠️  Streaming might not be optimal for Chainlit")
        return False


async def main():
    """Main test function."""
    print("🚀 Testing Streaming Fix")
    print("=" * 60)

    # Run all tests
    test1 = await test_streaming_question()
    test2 = await test_streaming_cybersecurity()
    test3 = await test_streaming_performance()
    test4 = await test_chainlit_compatibility()

    print("\n" + "=" * 60)
    print("🏁 Test Results Summary:")
    print(f"   Basic Streaming: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"   Cybersecurity Streaming: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"   Performance: {'✅ PASS' if test3 else '❌ FAIL'}")
    print(f"   Chainlit Compatibility: {'✅ PASS' if test4 else '❌ FAIL'}")

    if all([test1, test2, test3, test4]):
        print("\n🎉 All streaming tests passed! The fix should work correctly.")
        print("\n💡 To test in Chainlit:")
        print("   chainlit run main.py")
        print("   Ask: 'What is SOUP documentation for medical devices?'")
        print("   You should see character-by-character streaming!")
    else:
        print("\n⚠️  Some streaming tests failed. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main())
