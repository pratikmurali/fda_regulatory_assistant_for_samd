"""
Test script to verify the bug fixes for:
1. Sources not showing in cybersecurity responses
2. ZIP file processing errors
"""

import asyncio
import sys
import os
import zipfile
import io

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from ragchains.chain_manager import get_chain_manager
from graph.workflow import process_user_request
from main import process_zip_file


async def test_cybersecurity_sources():
    """Test that cybersecurity responses include sources."""
    print("🧪 Testing Cybersecurity Sources Bug Fix")
    print("=" * 50)

    # Pre-warm chains
    chain_manager = get_chain_manager()
    await chain_manager.prewarm_chains()

    # Test cybersecurity question
    print("Testing cybersecurity question with sources...")

    response_chunks = []
    async for chunk in process_user_request(
        user_input="What is SOUP documentation and why is it important for medical device cybersecurity?",
        uploaded_files=None,
        stream=True,
    ):
        response_chunks.append(chunk)
        # Print chunks that contain source information
        if "Sources:" in chunk or "Page" in chunk:
            print(f"📚 Source chunk: {chunk.strip()}")

    full_response = "".join(response_chunks)

    # Check if sources are included
    has_sources = "Sources:" in full_response
    has_page_refs = "Page" in full_response

    print(f"\n✅ Response includes sources: {has_sources}")
    print(f"✅ Response includes page references: {has_page_refs}")
    print(f"📊 Total response length: {len(full_response)} characters")

    if has_sources and has_page_refs:
        print("🎉 Bug Fix 1 SUCCESSFUL: Sources are now included in responses!")
    else:
        print("❌ Bug Fix 1 FAILED: Sources still not showing properly")

    return has_sources and has_page_refs


def create_test_zip_file() -> bytes:
    """Create a test ZIP file for testing."""
    print("\n🔧 Creating test ZIP file...")

    # Create in-memory ZIP file
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Add test files
        zip_file.writestr(
            "device_description.txt",
            """
Device Name: TestDevice Pro
Class: II
Intended Use: Cardiac monitoring with AI capabilities

This device incorporates machine learning algorithms for arrhythmia detection.
Clinical studies show 99% accuracy in detecting atrial fibrillation.
The device is intended for hospital use by trained medical professionals.
""",
        )

        zip_file.writestr(
            "cybersecurity_plan.txt",
            """
Cybersecurity Risk Assessment

SOUP Components:
1. TensorFlow 2.8.0 - Machine learning framework
2. OpenSSL 1.1.1 - Cryptographic library
3. Linux Kernel 5.4 - Operating system

Vulnerability Management:
- Regular security updates scheduled
- Penetration testing completed
- Incident response plan documented
""",
        )

        zip_file.writestr(
            "clinical_data.txt",
            """
Clinical Study Results

Study Population: 1000 patients
Primary Endpoint: Arrhythmia detection accuracy
Secondary Endpoints: False positive rate, usability

Results:
- Sensitivity: 99.2%
- Specificity: 98.8%
- False positive rate: 1.2%

Conclusion: Device demonstrates substantial equivalence to predicate device.
""",
        )

    zip_content = zip_buffer.getvalue()
    print(f"✅ Created test ZIP file: {len(zip_content)} bytes")
    return zip_content


def test_zip_processing():
    """Test ZIP file processing bug fix."""
    print("\n🧪 Testing ZIP File Processing Bug Fix")
    print("=" * 50)

    # Create test ZIP file
    test_zip_content = create_test_zip_file()

    # Test ZIP processing
    print("Testing ZIP file processing...")
    try:
        files_data = process_zip_file(test_zip_content)

        print("✅ ZIP processing successful!")
        print(f"📁 Extracted {len(files_data)} files:")

        for file_info in files_data:
            name = file_info.get("name", "Unknown")
            content_length = len(file_info.get("content", ""))
            file_type = file_info.get("type", "Unknown")

            print(f"   - {name} ({file_type}): {content_length} characters")

            # Check for errors
            if file_info.get("type") == "error":
                print(f"     ❌ Error: {file_info.get('content', '')}")

        # Check if all expected files were extracted
        expected_files = [
            "device_description.txt",
            "cybersecurity_plan.txt",
            "clinical_data.txt",
        ]
        extracted_files = [f["name"] for f in files_data if f.get("type") != "error"]

        all_files_extracted = all(
            expected in extracted_files for expected in expected_files
        )

        if (
            all_files_extracted
            and len([f for f in files_data if f.get("type") == "error"]) == 0
        ):
            print("🎉 Bug Fix 2 SUCCESSFUL: ZIP file processing works correctly!")
            return True
        else:
            print("❌ Bug Fix 2 FAILED: Some files missing or errors occurred")
            return False

    except Exception as e:
        print(f"❌ ZIP processing failed: {str(e)}")
        return False


async def test_gap_analysis_with_zip():
    """Test complete gap analysis workflow with ZIP file."""
    print("\n🧪 Testing Complete Gap Analysis with ZIP")
    print("=" * 50)

    # Create test ZIP file
    test_zip_content = create_test_zip_file()

    # Process ZIP file
    files_data = process_zip_file(test_zip_content)

    if not files_data or any(f.get("type") == "error" for f in files_data):
        print("❌ Cannot test gap analysis - ZIP processing failed")
        return False

    print("Testing gap analysis workflow...")
    try:
        response_chunks = []
        async for chunk in process_user_request(
            user_input="Please perform a comprehensive gap analysis of my regulatory submission documents",
            uploaded_files=files_data,
            stream=True,
        ):
            response_chunks.append(chunk)
            # Print progress updates
            if any(keyword in chunk for keyword in ["✅", "🔄", "📊", "🚨", "📋"]):
                print(f"Progress: {chunk.strip()}")

        full_response = "".join(response_chunks)

        # Check for key elements in response
        has_compliance_score = "Compliance Score:" in full_response
        has_gap_analysis = "Gap Analysis" in full_response
        has_recommendations = "Recommendation" in full_response

        print(f"\n✅ Response includes compliance score: {has_compliance_score}")
        print(f"✅ Response includes gap analysis: {has_gap_analysis}")
        print(f"✅ Response includes recommendations: {has_recommendations}")
        print(f"📊 Total response length: {len(full_response)} characters")

        if has_compliance_score and has_gap_analysis and has_recommendations:
            print("🎉 Gap Analysis with ZIP SUCCESSFUL!")
            return True
        else:
            print("❌ Gap Analysis incomplete - missing key elements")
            return False

    except Exception as e:
        print(f"❌ Gap analysis failed: {str(e)}")
        return False


async def main():
    """Main test function."""
    print("🚀 Bug Fix Verification Tests")
    print("=" * 60)

    # Test 1: Cybersecurity sources
    sources_fixed = await test_cybersecurity_sources()

    # Test 2: ZIP file processing
    zip_fixed = test_zip_processing()

    # Test 3: Complete workflow
    workflow_fixed = await test_gap_analysis_with_zip()

    print("\n" + "=" * 60)
    print("🏁 Test Results Summary:")
    print(
        f"   Bug Fix 1 (Sources): {'✅ FIXED' if sources_fixed else '❌ STILL BROKEN'}"
    )
    print(f"   Bug Fix 2 (ZIP): {'✅ FIXED' if zip_fixed else '❌ STILL BROKEN'}")
    print(f"   Workflow Test: {'✅ WORKING' if workflow_fixed else '❌ ISSUES'}")

    if sources_fixed and zip_fixed and workflow_fixed:
        print("\n🎉 All bugs fixed and workflow working correctly!")
    else:
        print("\n⚠️  Some issues remain - check the output above for details")


if __name__ == "__main__":
    asyncio.run(main())
