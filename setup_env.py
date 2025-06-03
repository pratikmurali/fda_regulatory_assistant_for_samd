"""
Environment setup script for FDA Regulatory Assistant.

This script helps set up the Python environment and test the installation.
"""

import sys
import importlib.util
from pathlib import Path


def setup_python_path():
    """Add the project root to Python path."""
    project_root = Path(__file__).parent.absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root


def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing module imports...")

    modules_to_test = [
        "ragchains",
        "tools",
        "utils",
        "loaders",
        "prompts",
        "ragchains.chain_manager",
        "utils.langgraph_utils",
    ]

    try:
        for module_name in modules_to_test:
            if importlib.util.find_spec(module_name) is not None:
                print(f"   ✅ {module_name} module")
            else:
                print(f"   ❌ {module_name} module not found")
                return False

        # Test specific function imports
        try:
            from ragchains.chain_manager import get_chain_manager
            from tools import (
                retrieve_cybersecurity_information,
                retrieve_regulatory_information,
            )
            from utils.langgraph_utils import create_agent

            # Verify functions are callable
            assert callable(get_chain_manager)
            assert callable(retrieve_cybersecurity_information)
            assert callable(retrieve_regulatory_information)
            assert callable(create_agent)

            print("   ✅ Specific function imports successful")
        except ImportError as e:
            print(f"   ❌ Function import error: {e}")
            return False

        return True

    except Exception as e:
        print(f"   ❌ Import test error: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n🔍 Checking dependencies...")

    required_packages = [
        "langchain",
        "langchain_openai",
        "langchain_community",
        "langgraph",
        "chainlit",
        "tiktoken",
        "qdrant_client",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Install with: pip install " + " ".join(missing_packages))
        return False

    return True


def main():
    """Main setup function."""
    print("🚀 FDA Regulatory Assistant - Environment Setup")
    print("=" * 50)

    # Setup Python path
    project_root = setup_python_path()
    print(f"📁 Project root: {project_root}")
    print("🐍 Python path updated")

    # Check dependencies
    deps_ok = check_dependencies()

    # Test imports
    imports_ok = test_imports()

    print("\n" + "=" * 50)

    if deps_ok and imports_ok:
        print("✅ Environment setup successful!")
        print("\n🎯 Ready to run:")
        print("   python test_tools_integration.py")
        print("   python examples/langgraph_agent_example.py")
        print("   chainlit run main.py")
    else:
        print("❌ Environment setup failed!")
        print("   Please install missing dependencies and try again.")


if __name__ == "__main__":
    main()
