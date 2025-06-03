"""
Example of using LangGraph agents with the FDA Regulatory Assistant tools.

This script demonstrates how to:
1. Pre-warm RAG chains using the chain manager
2. Create LangGraph agents with regulatory tools
3. Use agents to answer complex regulatory questions
"""

import asyncio
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from langchain_openai import ChatOpenAI
from utils.langgraph_utils import create_agent
from ragchains.chain_manager import get_chain_manager
from tools import (
    retrieve_cybersecurity_information,
    retrieve_regulatory_information,
    analyze_document_compliance,
    generate_compliance_checklist,
    validate_submission_format,
)


async def main():
    """Main example function."""

    print("🚀 FDA Regulatory Assistant - LangGraph Agent Example")
    print("=" * 60)

    # Step 1: Pre-warm the RAG chains
    print("\n1. Pre-warming RAG chains...")
    chain_manager = get_chain_manager()
    await chain_manager.prewarm_chains()

    # Verify chains are initialized
    status = chain_manager.is_initialized()
    print(
        f"   Cybersecurity chain: {'✅ Ready' if status['cybersecurity'] else '❌ Not ready'}"
    )
    print(
        f"   Regulatory chain: {'✅ Ready' if status['regulatory'] else '❌ Not ready'}"
    )

    # Step 2: Create LangGraph agents with different tool sets
    print("\n2. Creating specialized agents...")

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Cybersecurity specialist agent
    cybersecurity_tools = [
        retrieve_cybersecurity_information,
        analyze_document_compliance,
        generate_compliance_checklist,
    ]

    cybersecurity_agent = create_agent(
        llm=llm,
        tools=cybersecurity_tools,
        system_prompt="""You are a cybersecurity specialist for FDA medical device regulations.
        You help with cybersecurity compliance, SOUP documentation, vulnerability management,
        and cybersecurity requirements for Software as Medical Device (SaMD).
        Use the available tools to provide accurate, detailed responses.""",
    )

    # Regulatory specialist agent
    regulatory_tools = [
        retrieve_regulatory_information,
        validate_submission_format,
        generate_compliance_checklist,
        analyze_document_compliance,
    ]

    regulatory_agent = create_agent(
        llm=llm,
        tools=regulatory_tools,
        system_prompt="""You are a regulatory affairs specialist for FDA medical devices.
        You help with 510K submissions, PMA applications, regulatory compliance,
        and general FDA guidance for medical devices.
        Use the available tools to provide accurate, detailed responses.""",
    )

    print("   ✅ Cybersecurity specialist agent created")
    print("   ✅ Regulatory specialist agent created")

    # Step 3: Test the agents with sample questions
    print("\n3. Testing agents with sample questions...")

    # Test cybersecurity agent
    print("\n   🔒 Testing Cybersecurity Agent:")
    cybersecurity_question = {
        "messages": [
            {
                "role": "user",
                "content": "What are the key cybersecurity requirements for a Class II medical device with AI/ML components? Please provide specific guidance on SOUP documentation.",
            }
        ]
    }

    try:
        cyber_response = cybersecurity_agent.invoke(cybersecurity_question)
        print(f"   Response: {cyber_response['output'][:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test regulatory agent
    print("\n   📋 Testing Regulatory Agent:")
    regulatory_question = {
        "messages": [
            {
                "role": "user",
                "content": "What documents are required for a 510K submission for a Class II cardiac monitoring device? Please generate a compliance checklist.",
            }
        ]
    }

    try:
        reg_response = regulatory_agent.invoke(regulatory_question)
        print(f"   Response: {reg_response['output'][:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Step 4: Demonstrate direct tool usage
    print("\n4. Direct tool usage examples...")

    # Direct cybersecurity query
    print("\n   🔍 Direct cybersecurity query:")
    try:
        cyber_result = retrieve_cybersecurity_information.invoke(
            {"question": "What is SOUP in the context of medical device cybersecurity?"}
        )
        print(f"   Answer: {cyber_result['answer'][:150]}...")
        print(f"   📚 Sources: {len(cyber_result.get('sources', []))} documents")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Direct regulatory query
    print("\n   📖 Direct regulatory query:")
    try:
        reg_result = retrieve_regulatory_information.invoke(
            {"question": "What are the key components of a 510K submission?"}
        )
        print(f"   Answer: {reg_result['answer'][:150]}...")
        print(f"   📚 Sources: {len(reg_result.get('sources', []))} documents")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Generate compliance checklist
    print("\n   📝 Generate compliance checklist:")
    try:
        checklist = generate_compliance_checklist.invoke(
            {"regulation_type": "510k", "device_class": "II"}
        )
        print(f"   Generated checklist with {checklist['total_items']} items")
        print("   First 3 items:")
        for item in checklist["items"][:3]:
            print(f"     - {item['description']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n✅ LangGraph Agent Example completed successfully!")
    print("\n💡 Key Benefits:")
    print("   - RAG chains are pre-loaded and shared across all agents")
    print("   - Tools can access pre-initialized chains without re-loading documents")
    print("   - Agents can be specialized with different tool combinations")
    print("   - Both direct tool usage and agent-based workflows are supported")


def run_sync_example():
    """Run a synchronous example for testing."""
    print("🔧 Synchronous Tool Testing")
    print("=" * 30)

    # Test direct tool access (assumes chains are already initialized)
    chain_manager = get_chain_manager()
    status = chain_manager.is_initialized()

    if not status["cybersecurity"] or not status["regulatory"]:
        print("⚠️  Warning: RAG chains not initialized. Run the async example first.")
        return

    # Test cybersecurity tool
    print("\n🔒 Testing cybersecurity tool:")
    try:
        result = retrieve_cybersecurity_information.invoke(
            {
                "question": "What are the main cybersecurity controls for medical devices?"
            }
        )
        print(f"Answer: {result['answer'][:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test regulatory tool
    print("\n📋 Testing regulatory tool:")
    try:
        result = retrieve_regulatory_information.invoke(
            {"question": "What is the difference between 510K and PMA?"}
        )
        print(f"Answer: {result['answer'][:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        run_sync_example()
    else:
        asyncio.run(main())
