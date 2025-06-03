"""
Test script to verify the cleaned up main.py works correctly.

This script tests:
- Import functionality
- File processing functions
- Basic workflow integration
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def test_imports():
    """Test that all imports in main.py work correctly."""
    print("🧪 Testing main.py imports...")

    try:
        # Test individual imports
        import chainlit as cl

        print("   ✅ chainlit imported successfully")

        from ragchains.chain_manager import get_chain_manager

        print("   ✅ chain_manager imported successfully")

        from graph.workflow import process_user_request

        print("   ✅ workflow imported successfully")

        from typing import List, Dict, Any

        print("   ✅ typing imports successful")

        import zipfile
        import io
        import os

        print("   ✅ standard library imports successful")

        return True

    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False


def test_file_processing_functions():
    """Test the file processing functions from main.py."""
    print("\n🧪 Testing file processing functions...")

    try:
        # Import the functions
        from main import extract_text_from_file, process_zip_file

        # Test text extraction
        test_content = b"This is a test document for regulatory compliance."
        extracted_text = extract_text_from_file(test_content, "test.txt")

        if "test document" in extracted_text:
            print("   ✅ extract_text_from_file works correctly")
        else:
            print("   ❌ extract_text_from_file failed")
            return False

        # Test ZIP processing with invalid content
        invalid_zip = b"This is not a ZIP file"
        result = process_zip_file(invalid_zip)

        # Should return error file
        if result and result[0].get("type") == "error":
            print("   ✅ process_zip_file handles invalid files correctly")
        else:
            print("   ❌ process_zip_file error handling failed")
            return False

        return True

    except Exception as e:
        print(f"   ❌ Function test error: {e}")
        return False


def test_chain_manager_access():
    """Test that chain manager can be accessed."""
    print("\n🧪 Testing chain manager access...")

    try:
        from main import chain_manager

        # Check if chain manager is accessible
        if chain_manager is not None:
            print("   ✅ Chain manager accessible")

            # Check initialization status
            status = chain_manager.is_initialized()
            print(f"   📊 Chain status: {status}")

            return True
        else:
            print("   ❌ Chain manager is None")
            return False

    except Exception as e:
        print(f"   ❌ Chain manager test error: {e}")
        return False


def test_main_structure():
    """Test the overall structure of main.py."""
    print("\n🧪 Testing main.py structure...")

    try:
        # Read the main.py file
        with open("main.py", "r") as f:
            content = f.read()

        # Check for required components
        checks = [
            (
                "Module docstring",
                '"""' in content and "FDA Regulatory Assistant" in content,
            ),
            ("File processing functions", "extract_text_from_file" in content),
            ("ZIP processing", "process_zip_file" in content),
            (
                "Chainlit handlers",
                "@cl.on_chat_start" in content and "@cl.on_message" in content,
            ),
            ("No chat profiles", "@cl.set_chat_profiles" not in content),
            (
                "Unified welcome message",
                "FDA Regulatory Assistant" in content and "specialist team" in content,
            ),
            ("LangGraph integration", "process_user_request" in content),
        ]

        all_passed = True
        for check_name, check_result in checks:
            if check_result:
                print(f"   ✅ {check_name}")
            else:
                print(f"   ❌ {check_name}")
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"   ❌ Structure test error: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Testing Cleaned Up main.py")
    print("=" * 40)

    # Run tests
    imports_ok = test_imports()
    functions_ok = test_file_processing_functions()
    chain_manager_ok = test_chain_manager_access()
    structure_ok = test_main_structure()

    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Functions: {'✅ PASS' if functions_ok else '❌ FAIL'}")
    print(f"   Chain Manager: {'✅ PASS' if chain_manager_ok else '❌ FAIL'}")
    print(f"   Structure: {'✅ PASS' if structure_ok else '❌ FAIL'}")

    if all([imports_ok, functions_ok, chain_manager_ok, structure_ok]):
        print("\n🎉 All tests passed! main.py is cleaned up and working correctly.")
        print("\n💡 Ready to run:")
        print("   chainlit run main.py")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()
