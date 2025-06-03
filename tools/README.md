# FDA Regulatory Assistant Tools Module

This module provides a comprehensive set of agentic tools for FDA regulatory document processing, compliance analysis, and submission assistance.

## Overview

The tools module is designed to work with LangChain agents and can be used for:
- Document processing and analysis
- Regulatory compliance checking
- Submission format validation
- Comparative analysis
- Metadata extraction
- Compliance checklist generation

## Available Tools

### 1. `chunk_document`
Splits documents into smaller, manageable chunks for processing.

**Parameters:**
- `docs`: List of Document objects to chunk
- `chunk_size`: Maximum size of each chunk (default: 1000)
- `chunk_overlap`: Overlap between chunks (default: 80)

**Returns:** List of chunked Document objects

### 2. `search_regulatory_database`
Searches through regulatory documents for specific information.

**Parameters:**
- `query`: Search query string
- `document_type`: Type of document ("guidance", "regulation", "standard", "all")

**Returns:** Dictionary with search results and metadata

### 3. `analyze_document_compliance`
Analyzes a document for compliance with specific FDA regulations.

**Parameters:**
- `document`: Document to analyze
- `regulation_type`: Type of regulation ("510k", "pma", "de_novo", "qsr")

**Returns:** Dictionary with compliance analysis results

### 4. `extract_regulatory_requirements`
Extracts regulatory requirements from documents.

**Parameters:**
- `document`: Document to extract requirements from
- `requirement_type`: Type of requirements ("clinical", "technical", "quality", "all")

**Returns:** List of extracted requirements with metadata

### 5. `validate_submission_format`
Validates document format against FDA submission requirements.

**Parameters:**
- `document`: Document to validate
- `submission_type`: Type of submission ("510k", "pma", "de_novo", "ide")

**Returns:** Dictionary with validation results

### 6. `generate_compliance_checklist`
Generates a compliance checklist for specific regulations and device classes.

**Parameters:**
- `regulation_type`: Type of regulation ("510k", "pma", "de_novo", "qsr")
- `device_class`: FDA device class ("I", "II", "III")

**Returns:** Dictionary with structured compliance checklist

### 7. `compare_documents`
Compares two documents for similarities and differences.

**Parameters:**
- `doc1`: First document to compare
- `doc2`: Second document to compare
- `comparison_type`: Type of comparison ("content", "structure", "metadata")

**Returns:** Dictionary with comparison results

### 8. `extract_document_metadata`
Extracts and enhances metadata from documents.

**Parameters:**
- `document`: Document to extract metadata from

**Returns:** Dictionary with extracted and enhanced metadata

### 9. `retrieve_cybersecurity_information`
Retrieves cybersecurity information from the pre-loaded cybersecurity RAG chain.

**Parameters:**
- `question`: The cybersecurity question to ask

**Returns:** Dictionary with answer and sources from cybersecurity documents

### 10. `retrieve_regulatory_information`
Retrieves regulatory information from the pre-loaded regulatory RAG chain.

**Parameters:**
- `question`: The regulatory question to ask

**Returns:** Dictionary with answer and sources from regulatory documents

## RAG Chain Integration

The tools module integrates with a centralized RAG Chain Manager that:

- **Pre-loads documents once** at application startup
- **Maintains singleton instances** of RAG chains for performance
- **Provides thread-safe access** to chains from multiple contexts
- **Supports both async and sync access patterns**

### Chain Manager Benefits

1. **Performance**: Documents are loaded only once, not per tool invocation
2. **Memory Efficiency**: Single instances of vector stores and embeddings
3. **Consistency**: All tools use the same pre-loaded knowledge base
4. **Flexibility**: Works with Chainlit UI, LangGraph agents, and direct tool usage

### Pre-warming Chains

```python
from ragchains.chain_manager import get_chain_manager

# Get the chain manager
chain_manager = get_chain_manager()

# Pre-warm both chains (async)
await chain_manager.prewarm_chains()

# Check initialization status
status = chain_manager.is_initialized()
print(f"Cybersecurity: {status['cybersecurity']}")
print(f"Regulatory: {status['regulatory']}")
```

## Usage Examples

### Basic Usage

```python
from tools import (
    chunk_document,
    analyze_document_compliance,
    retrieve_cybersecurity_information,
    retrieve_regulatory_information
)
from langchain_core.documents import Document

# Create a document
doc = Document(
    page_content="Your document content here...",
    metadata={"source": "example.pdf"}
)

# Chunk the document
chunks = chunk_document.invoke({
    "docs": [doc],
    "chunk_size": 1000,
    "chunk_overlap": 100
})

# Analyze compliance
compliance = analyze_document_compliance.invoke({
    "document": doc,
    "regulation_type": "510k"
})

# Query RAG chains (requires pre-warmed chains)
cyber_info = retrieve_cybersecurity_information.invoke({
    "question": "What are SOUP requirements for medical devices?"
})

regulatory_info = retrieve_regulatory_information.invoke({
    "question": "What documents are needed for 510K submission?"
})
```

### Using with LangGraph Agents

```python
import asyncio
from langchain_openai import ChatOpenAI
from utils.langgraph_utils import create_agent
from ragchains.chain_manager import get_chain_manager
from tools import (
    retrieve_cybersecurity_information,
    retrieve_regulatory_information,
    analyze_document_compliance,
    generate_compliance_checklist,
    validate_submission_format
)

async def create_regulatory_agent():
    # Pre-warm chains first
    chain_manager = get_chain_manager()
    await chain_manager.prewarm_chains()

    # Create an agent with regulatory tools
    llm = ChatOpenAI(model="gpt-4")
    tools = [
        retrieve_regulatory_information,
        retrieve_cybersecurity_information,
        analyze_document_compliance,
        generate_compliance_checklist,
        validate_submission_format
    ]

    agent = create_agent(
        llm=llm,
        tools=tools,
        system_prompt="You are a regulatory compliance specialist with access to FDA guidance documents..."
    )

    return agent

# Usage
agent = asyncio.run(create_regulatory_agent())
response = agent.invoke({
    "messages": [{"role": "user", "content": "What are the cybersecurity requirements for Class II devices?"}]
})
```

## Installation and Setup

The tools module is part of the FDA Regulatory Assistant project. Ensure you have the required dependencies:

```bash
# Install project dependencies
pip install -r requirements.txt
```

## Testing

Run the example usage script to test the tools:

```bash
python tools/example_usage.py
```

## Module Structure

```
tools/
├── __init__.py          # Module initialization and exports
├── tools.py             # Main tools implementation
├── example_usage.py     # Usage examples and demos
└── README.md           # This documentation
```

## Integration with Existing Code

The tools module maintains backward compatibility with existing code:

- `ragchains/tools/agent_tools.py` now imports from the main tools module
- All existing imports will continue to work without modification
- New tools are available through the main tools module

## Contributing

When adding new tools:

1. Add the tool function to `tools/tools.py`
2. Use the `@tool` decorator from LangChain
3. Include comprehensive docstrings
4. Add the tool to the `__init__.py` exports
5. Update this README with documentation
6. Add usage examples to `example_usage.py`

## Notes

- All tools are designed to work with LangChain's Document objects
- Tools return structured data (dictionaries/lists) for easy processing
- Error handling and validation should be added for production use
- Some tools (like `search_regulatory_database`) contain placeholder implementations
