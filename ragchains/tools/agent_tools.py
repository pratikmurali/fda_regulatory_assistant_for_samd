"""
Legacy agent tools module.

This module now imports tools from the main tools module to maintain
backward compatibility while centralizing tool definitions.
"""

# Import tools from the main tools module
from tools.tools import (
    chunk_document,
    search_regulatory_database,
    analyze_document_compliance,
    extract_regulatory_requirements,
    validate_submission_format,
    generate_compliance_checklist,
    compare_documents,
    extract_document_metadata,
    retrieve_cybersecurity_information,
    retrieve_regulatory_information,
)

# Re-export for backward compatibility
__all__ = [
    "chunk_document",
    "search_regulatory_database",
    "analyze_document_compliance",
    "extract_regulatory_requirements",
    "validate_submission_format",
    "generate_compliance_checklist",
    "compare_documents",
    "extract_document_metadata",
    "retrieve_cybersecurity_information",
    "retrieve_regulatory_information",
]
