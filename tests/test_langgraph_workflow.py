"""
Test script for the complete LangGraph workflow implementation.

This script tests the entire FDA Regulatory Assistant workflow including:
- RAG chain manager initialization
- LangGraph agents and workflow
- Question answering and gap analysis
- Streaming responses
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from ragchains.chain_manager import get_chain_manager
from graph.workflow import get_workflow, process_user_request
from tools import (
    retrieve_cybersecurity_information,
    retrieve_regulatory_information,
    process_uploaded_documents,
)


async def test_chain_manager():
    """Test the RAG chain manager."""
    print("🧪 Testing RAG Chain Manager")
    print("=" * 40)

    chain_manager = get_chain_manager()

    # Check initial status
    initial_status = chain_manager.is_initialized()
    print(f"Initial status: {initial_status}")

    # Pre-warm chains
    print("Pre-warming chains...")
    await chain_manager.prewarm_chains()

    # Check final status
    final_status = chain_manager.is_initialized()
    print(f"Final status: {final_status}")

    # Test direct queries
    print("\nTesting direct queries...")
    cyber_result = await chain_manager.query_cybersecurity_chain(
        "What is SOUP in medical device cybersecurity?"
    )
    print(
        f"Cybersecurity query result: {len(cyber_result.get('answer', ''))} characters"
    )

    reg_result = await chain_manager.query_regulatory_chain(
        "What are the main components of a 510K submission?"
    )
    print(f"Regulatory query result: {len(reg_result.get('answer', ''))} characters")

    return final_status["cybersecurity"] and final_status["regulatory"]


def test_tools_sync():
    """Test tools with synchronous access."""
    print("\n🔧 Testing Tools (Synchronous)")
    print("=" * 40)

    # Test cybersecurity tool
    print("Testing cybersecurity tool...")
    try:
        result = retrieve_cybersecurity_information.invoke(
            {
                "question": "What are the key cybersecurity principles for medical devices?"
            }
        )
        print(f"✅ Success: {len(result.get('answer', ''))} characters")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test regulatory tool
    print("Testing regulatory tool...")
    try:
        result = retrieve_regulatory_information.invoke(
            {"question": "What documents are required for 510K submission?"}
        )
        print(f"✅ Success: {len(result.get('answer', ''))} characters")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test document processing
    print("Testing document processing...")
    try:
        sample_files = [
            {
                "name": "device_description.txt",
                "content": "This is a Class II cardiac monitoring device with AI/ML capabilities for arrhythmia detection.",
                "type": ".txt",
            },
            {
                "name": "cybersecurity_plan.txt",
                "content": "Cybersecurity risk assessment and SOUP documentation for the device software components.",
                "type": ".txt",
            },
        ]

        result = process_uploaded_documents.invoke({"files_data": sample_files})
        print(f"✅ Processed {result['document_count']} documents")
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_workflow_question_answering():
    """Test the question answering workflow."""
    print("\n❓ Testing Question Answering Workflow")
    print("=" * 40)

    workflow = get_workflow()

    # Test cybersecurity question
    print("Testing cybersecurity question...")
    try:
        response_chunks = []
        async for chunk in workflow.run_question_answering(
            question="What are the FDA cybersecurity requirements for Class II medical devices?",
            stream=True,
        ):
            response_chunks.append(chunk)

        full_response = "".join(response_chunks)
        print(f"✅ Response length: {len(full_response)} characters")
        print(f"First 100 chars: {full_response[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test regulatory question
    print("\nTesting regulatory question...")
    try:
        response_chunks = []
        async for chunk in workflow.run_question_answering(
            question="What are the essential components of a 510K premarket notification?",
            stream=True,
        ):
            response_chunks.append(chunk)

        full_response = "".join(response_chunks)
        print(f"✅ Response length: {len(full_response)} characters")
        print(f"First 100 chars: {full_response[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_workflow_gap_analysis():
    """Test the gap analysis workflow."""
    print("\n📊 Testing Gap Analysis Workflow")
    print("=" * 40)

    workflow = get_workflow()

    # Create sample uploaded files
    sample_files = [
        {
            "name": "device_description.txt",
            "content": """
            Device Name: CardioMonitor Pro AI
            Class: II
            Intended Use: Continuous cardiac monitoring with AI-powered arrhythmia detection

            The device incorporates machine learning algorithms for real-time ECG analysis.
            Clinical studies demonstrate 99.2% accuracy in arrhythmia detection.
            The device is intended for use in hospital and clinical settings.
            """,
            "type": ".txt",
            "size": 300,
        },
        {
            "name": "cybersecurity_documentation.txt",
            "content": """
            Cybersecurity Risk Assessment

            The device software includes the following SOUP components:
            - TensorFlow ML framework
            - OpenSSL cryptographic library
            - Linux operating system

            Vulnerability management procedures are in place.
            Incident response plan has been developed.
            """,
            "type": ".txt",
            "size": 250,
        },
        {
            "name": "clinical_data.txt",
            "content": """
            Clinical Study Results

            Study population: 500 patients
            Primary endpoint: Arrhythmia detection accuracy
            Results: 99.2% sensitivity, 98.8% specificity

            Adverse events: None related to device malfunction
            Predicate device comparison shows substantial equivalence.
            """,
            "type": ".txt",
            "size": 200,
        },
    ]

    print(f"Testing gap analysis with {len(sample_files)} sample files...")
    try:
        response_chunks = []
        async for chunk in workflow.run_gap_analysis(
            uploaded_files=sample_files,
            user_request="Please perform a comprehensive gap analysis of my 510K submission documents",
            stream=True,
        ):
            response_chunks.append(chunk)
            # Print progress updates
            if any(keyword in chunk for keyword in ["✅", "🔄", "📊", "🚨"]):
                print(f"Progress: {chunk.strip()}")

        full_response = "".join(response_chunks)
        print(
            f"\n✅ Gap analysis completed. Response length: {len(full_response)} characters"
        )

        # Show summary
        if "Overall Compliance Score:" in full_response:
            lines = full_response.split("\n")
            for line in lines:
                if (
                    "Overall Compliance Score:" in line
                    or "Critical Issues:" in line
                    or "Readiness Level:" in line
                ):
                    print(f"Summary: {line.strip()}")

    except Exception as e:
        print(f"❌ Error: {e}")


async def test_process_user_request():
    """Test the main process_user_request function."""
    print("\n🎯 Testing Main Process User Request Function")
    print("=" * 40)

    # Test question answering
    print("Testing question processing...")
    try:
        response_chunks = []
        async for chunk in process_user_request(
            user_input="What are the cybersecurity requirements for AI/ML medical devices?",
            uploaded_files=None,
            stream=True,
        ):
            response_chunks.append(chunk)

        full_response = "".join(response_chunks)
        print(f"✅ Question answered. Response length: {len(full_response)} characters")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test gap analysis
    print("\nTesting gap analysis processing...")
    try:
        sample_files = [
            {
                "name": "submission_summary.txt",
                "content": "This is a 510K submission for a Class II cardiac monitoring device with AI capabilities.",
                "type": ".txt",
                "size": 100,
            }
        ]

        response_chunks = []
        async for chunk in process_user_request(
            user_input="Analyze my submission for compliance gaps",
            uploaded_files=sample_files,
            stream=True,
        ):
            response_chunks.append(chunk)

        full_response = "".join(response_chunks)
        print(
            f"✅ Gap analysis completed. Response length: {len(full_response)} characters"
        )
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Main test function."""
    print("🚀 FDA Regulatory Assistant - Complete Workflow Test")
    print("=" * 60)

    # Test 1: Chain Manager
    chains_ready = await test_chain_manager()
    if not chains_ready:
        print("❌ Chain manager test failed. Stopping tests.")
        return

    # Test 2: Tools
    test_tools_sync()

    # Test 3: Question Answering Workflow
    await test_workflow_question_answering()

    # Test 4: Gap Analysis Workflow
    await test_workflow_gap_analysis()

    # Test 5: Main Process Function
    await test_process_user_request()

    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("\n💡 Next steps:")
    print("   - Run 'chainlit run main.py' to test the UI")
    print("   - Upload ZIP files to test gap analysis")
    print("   - Ask questions to test the Q&A workflow")


if __name__ == "__main__":
    asyncio.run(main())
