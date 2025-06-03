"""
Simple test script for the tools integration with RAG chains.

Run this from the project root directory:
python test_tools_integration.py
"""

import asyncio
from ragchains.chain_manager import get_chain_manager
from tools import (
    retrieve_cybersecurity_information,
    retrieve_regulatory_information,
    generate_compliance_checklist,
)


async def test_chain_manager():
    """Test the RAG chain manager functionality."""
    print("🧪 Testing RAG Chain Manager Integration")
    print("=" * 50)

    # Step 1: Get chain manager and check initial status
    print("\n1. Initializing Chain Manager...")
    chain_manager = get_chain_manager()

    initial_status = chain_manager.is_initialized()
    print(f"   Initial status - Cybersecurity: {initial_status['cybersecurity']}")
    print(f"   Initial status - Regulatory: {initial_status['regulatory']}")

    # Step 2: Pre-warm chains
    print("\n2. Pre-warming RAG chains...")
    try:
        await chain_manager.prewarm_chains()

        final_status = chain_manager.is_initialized()
        print(
            f"   ✅ Cybersecurity chain: {'Ready' if final_status['cybersecurity'] else 'Failed'}"
        )
        print(
            f"   ✅ Regulatory chain: {'Ready' if final_status['regulatory'] else 'Failed'}"
        )

    except Exception as e:
        print(f"   ❌ Error pre-warming chains: {e}")
        return False

    return True


def test_tools_sync():
    """Test the tools with synchronous access."""
    print("\n3. Testing Tools (Synchronous Access)...")

    # Test cybersecurity tool
    print("\n   🔒 Testing cybersecurity tool:")
    try:
        result = retrieve_cybersecurity_information.invoke(
            {"question": "What is SOUP in medical device cybersecurity?"}
        )
        print(f"   ✅ Success: {result['answer'][:100]}...")
        print(f"   📚 Sources: {len(result.get('sources', []))} documents")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test regulatory tool
    print("\n   📋 Testing regulatory tool:")
    try:
        result = retrieve_regulatory_information.invoke(
            {"question": "What are the main components of a 510K submission?"}
        )
        print(f"   ✅ Success: {result['answer'][:100]}...")
        print(f"   📚 Sources: {len(result.get('sources', []))} documents")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test compliance checklist tool
    print("\n   📝 Testing compliance checklist tool:")
    try:
        result = generate_compliance_checklist.invoke(
            {"regulation_type": "510k", "device_class": "II"}
        )
        print(f"   ✅ Success: Generated {result['total_items']} checklist items")
        print("   📋 First 3 items:")
        for item in result["items"][:3]:
            print(f"      - {item['description']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def test_chain_manager_async():
    """Test direct chain manager async methods."""
    print("\n4. Testing Chain Manager (Async Access)...")

    chain_manager = get_chain_manager()

    # Test cybersecurity chain
    print("\n   🔒 Testing cybersecurity chain (async):")
    try:
        result = await chain_manager.query_cybersecurity_chain(
            "What are the key cybersecurity principles for medical devices?"
        )
        print(f"   ✅ Success: {result['answer'][:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test regulatory chain
    print("\n   📋 Testing regulatory chain (async):")
    try:
        result = await chain_manager.query_regulatory_chain(
            "What is the difference between 510K and PMA submissions?"
        )
        print(f"   ✅ Success: {result['answer'][:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def main():
    """Main test function."""
    print("🚀 FDA Regulatory Assistant - Tools Integration Test")
    print("=" * 60)

    # Test chain manager initialization
    chains_ready = await test_chain_manager()

    if not chains_ready:
        print("\n❌ Chain initialization failed. Cannot proceed with tool tests.")
        return

    # Test tools with synchronous access
    test_tools_sync()

    # Test chain manager with async access
    await test_chain_manager_async()

    print("\n" + "=" * 60)
    print("✅ Integration test completed!")
    print("\n💡 Next steps:")
    print("   - Chains are now pre-loaded and ready for use")
    print("   - Tools can be used in LangGraph agents")
    print("   - Chainlit interface will use the same pre-loaded chains")
    print("   - Run 'python examples/langgraph_agent_example.py' for agent examples")


def run_simple_test():
    """Run a simple synchronous test."""
    print("🔧 Simple Tools Test (Synchronous)")
    print("=" * 40)

    chain_manager = get_chain_manager()
    status = chain_manager.is_initialized()

    if not status["cybersecurity"] or not status["regulatory"]:
        print("⚠️  Warning: RAG chains not initialized.")
        print("   Run the full async test first: python test_tools_integration.py")
        return

    print("✅ Chains are initialized. Testing tools...")

    # Test a simple tool
    try:
        result = generate_compliance_checklist.invoke(
            {"regulation_type": "510k", "device_class": "II"}
        )
        print(f"✅ Compliance checklist generated: {result['total_items']} items")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "simple":
        run_simple_test()
    else:
        asyncio.run(main())
