"""
Test script to verify that word-by-word streaming preserves formatting.

This demonstrates that the new regex-based word splitting maintains:
- Line breaks
- Indentation
- Multiple spaces
- Bullet points
- Numbered lists
"""

import asyncio
import re


async def test_old_word_streaming(text: str):
    """Test old word streaming method (breaks formatting)."""
    print("❌ OLD Method (Breaks Formatting):")
    print("-" * 50)

    words = text.split()
    result = ""
    for word in words:
        result += word + " "
        print(word + " ", end="", flush=True)
        await asyncio.sleep(0.01)  # Fast for demo

    print("\n" + "-" * 50)
    print("Result:")
    print(repr(result))  # Show actual characters
    return result


async def test_new_word_streaming(text: str):
    """Test new word streaming method (preserves formatting)."""
    print("\n✅ NEW Method (Preserves Formatting):")
    print("-" * 50)

    # Same regex pattern as in workflow.py
    word_pattern = r"(\S+)(\s*)"
    matches = re.findall(word_pattern, text)

    result = ""
    for word, whitespace in matches:
        chunk = word + whitespace
        result += chunk
        print(chunk, end="", flush=True)
        await asyncio.sleep(0.01)  # Fast for demo

    # Handle any remaining whitespace at the end
    if text and text[-1].isspace():
        remaining_whitespace = re.search(r"\s*$", text)
        if remaining_whitespace and remaining_whitespace.group():
            result += remaining_whitespace.group()

    print("\n" + "-" * 50)
    print("Result:")
    print(repr(result))  # Show actual characters
    return result


async def test_formatting_preservation():
    """Test with various formatting scenarios."""
    print("🧪 Testing Formatting Preservation")
    print("=" * 70)

    # Test case 1: Simple numbered list
    test1 = """A 510(k) submission includes:

1. Indications for Use
2. Device Description
3. Predicate Device Comparison

These are essential components."""

    print("📝 Test 1: Numbered List with Line Breaks")
    old_result1 = await test_old_word_streaming(test1)
    new_result1 = await test_new_word_streaming(test1)

    print(
        f"\n🔍 Formatting preserved: {old_result1 != new_result1 and new_result1 == test1}"
    )

    # Test case 2: Indented bullet points
    test2 = """Performance Testing includes:

    - Nonclinical studies
    - Clinical investigations
        • Safety data
        • Effectiveness data
    - Adverse event reporting"""

    print("\n" + "=" * 70)
    print("📝 Test 2: Indented Bullet Points")
    old_result2 = await test_old_word_streaming(test2)
    new_result2 = await test_new_word_streaming(test2)

    print(
        f"\n🔍 Formatting preserved: {old_result2 != new_result2 and new_result2 == test2}"
    )

    # Test case 3: Multiple spaces and special formatting
    test3 = """**SOUP Documentation**

Definition:    Software of Unknown Provenance
Purpose:       Cybersecurity compliance
Requirements:
               • Documentation
               • Risk assessment"""

    print("\n" + "=" * 70)
    print("📝 Test 3: Multiple Spaces and Alignment")
    old_result3 = await test_old_word_streaming(test3)
    new_result3 = await test_new_word_streaming(test3)

    print(
        f"\n🔍 Formatting preserved: {old_result3 != new_result3 and new_result3 == test3}"
    )

    return all([new_result1 == test1, new_result2 == test2, new_result3 == test3])


async def demonstrate_real_response():
    """Demonstrate with a real FDA response format."""
    print("\n🎯 Real FDA Response Format Test")
    print("=" * 70)

    real_response = """**510(k) Submission Components**

A 510(k) submission package for Class II medical devices includes:

1. **Indications for Use**: Clear statement describing intended use

2. **Device Description**: Detailed description including:
   - Components and materials
   - Operating principles
   - Technological characteristics

3. **Predicate Device Comparison**:
   - Application numbers
   - Product codes
   - Similarities and differences

4. **Performance Testing**:
   - Nonclinical laboratory studies
   - Clinical investigations
   - Safety and effectiveness data

📚 **Sources:** 3 FDA guidance documents referenced

1. **21 CFR Part 814 Subpart B** - Page 2
2. **guidance-ai-enabled-device-software-functions** - Page 55"""

    print("Streaming with formatting preservation:")
    print("-" * 50)

    word_pattern = r"(\S+)(\s*)"
    matches = re.findall(word_pattern, real_response)

    streamed_result = ""
    for word, whitespace in matches:
        chunk = word + whitespace
        streamed_result += chunk
        print(chunk, end="", flush=True)
        await asyncio.sleep(0.02)  # Slightly slower for readability

    print("\n" + "-" * 50)
    print(f"✅ Perfect match: {streamed_result == real_response}")
    print(f"📊 Original length: {len(real_response)} chars")
    print(f"📊 Streamed length: {len(streamed_result)} chars")

    return streamed_result == real_response


async def main():
    """Main test function."""
    print("🚀 Word-by-Word Streaming with Formatting Preservation")
    print("=" * 80)

    # Test formatting preservation
    formatting_preserved = await test_formatting_preservation()

    # Test with real response
    real_response_preserved = await demonstrate_real_response()

    print("\n" + "=" * 80)
    print("🏁 Test Results:")
    print(
        f"   Formatting Preservation: {'✅ PASS' if formatting_preserved else '❌ FAIL'}"
    )
    print(
        f"   Real Response Test: {'✅ PASS' if real_response_preserved else '❌ FAIL'}"
    )

    if formatting_preserved and real_response_preserved:
        print("\n🎉 SUCCESS! Word-by-word streaming now preserves all formatting!")
        print("\n💡 Benefits:")
        print("   ✅ Fast word-by-word streaming")
        print("   ✅ Preserves line breaks and indentation")
        print("   ✅ Maintains bullet points and numbering")
        print("   ✅ Keeps multiple spaces and alignment")
        print("   ✅ Perfect for structured FDA responses")
    else:
        print("\n⚠️  Some formatting issues detected. Check the test output above.")

    print("\n🔧 Technical Details:")
    print("   - Uses regex pattern: r'(\\S+)(\\s*)'")
    print("   - Captures words + following whitespace")
    print("   - Preserves all original formatting")
    print("   - 30ms delay between words")


if __name__ == "__main__":
    asyncio.run(main())
