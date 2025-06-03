"""
Example usage of the FDA Regulatory Assistant tools module.

This script demonstrates how to use the various agentic tools
for document processing and regulatory compliance analysis.
"""

from langchain_core.documents import Document
from tools import (
    chunk_document,
    search_regulatory_database,
    analyze_document_compliance,
    extract_regulatory_requirements,
    validate_submission_format,
    generate_compliance_checklist,
    compare_documents,
    extract_document_metadata,
)


def main():
    """Demonstrate usage of the tools module."""

    # Create sample documents for testing
    sample_doc1 = Document(
        page_content="""
        Device Name: CardioMonitor Pro
        Manufacturer: MedTech Solutions Inc.
        Model Number: CM-2024-001
        Classification: Class II Medical Device

        This device is intended for continuous cardiac monitoring in hospital settings.
        The device provides real-time ECG monitoring with automated arrhythmia detection.

        Clinical studies have demonstrated safety and effectiveness for the intended use.
        The device incorporates advanced signal processing algorithms for noise reduction.
        Performance testing data shows 99.5% accuracy in arrhythmia detection.

        Substantial equivalence comparison with predicate device XYZ-123 shows
        similar technological characteristics and intended use.
        """,
        metadata={
            "source": "510k_submission_draft.pdf",
            "device_type": "cardiac_monitor",
            "submission_type": "510k",
        },
    )

    sample_doc2 = Document(
        page_content="""
        Product Name: HeartWatch Advanced
        Company: CardioTech Corp
        Model #: HW-2024-002
        Class: II

        Intended for cardiac rhythm monitoring in clinical environments.
        Features automated detection of cardiac arrhythmias using AI algorithms.

        Clinical evaluation data demonstrates equivalent performance to existing devices.
        Technical specifications include 12-lead ECG capability with digital filtering.
        Risk analysis has been conducted according to ISO 14971 standards.
        """,
        metadata={
            "source": "competitor_analysis.pdf",
            "device_type": "cardiac_monitor",
            "submission_type": "510k",
        },
    )

    print("🔧 FDA Regulatory Assistant Tools Demo")
    print("=" * 50)

    # 1. Document chunking
    print("\n1. Document Chunking:")
    chunks = chunk_document.invoke(
        {"docs": [sample_doc1], "chunk_size": 500, "chunk_overlap": 50}
    )
    print(f"   Original document split into {len(chunks)} chunks")

    # 2. Compliance analysis
    print("\n2. Compliance Analysis:")
    compliance = analyze_document_compliance.invoke(
        {"document": sample_doc1, "regulation_type": "510k"}
    )
    print(f"   Overall compliance score: {compliance['overall_compliance_score']:.2f}")
    print(f"   Recommendations: {len(compliance['recommendations'])} items")

    # 3. Generate compliance checklist
    print("\n3. Compliance Checklist Generation:")
    checklist = generate_compliance_checklist.invoke(
        {"regulation_type": "510k", "device_class": "II"}
    )
    print(f"   Generated checklist with {checklist['total_items']} items")
    print("   First 3 items:")
    for item in checklist["items"][:3]:
        print(f"     - {item['description']}")

    # 4. Extract regulatory requirements
    print("\n4. Regulatory Requirements Extraction:")
    requirements = extract_regulatory_requirements.invoke(
        {"document": sample_doc1, "requirement_type": "all"}
    )
    print(f"   Found {len(requirements)} regulatory requirements")

    # 5. Document comparison
    print("\n5. Document Comparison:")
    comparison = compare_documents.invoke(
        {"doc1": sample_doc1, "doc2": sample_doc2, "comparison_type": "content"}
    )
    print(f"   Content similarity score: {comparison['similarity_score']:.2f}")
    print(f"   Common words: {comparison['common_words_count']}")

    # 6. Metadata extraction
    print("\n6. Metadata Extraction:")
    metadata = extract_document_metadata.invoke({"document": sample_doc1})
    print(f"   Word count: {metadata['word_count']}")
    print(f"   Device name: {metadata.get('device_name', 'Not found')}")
    print(f"   Manufacturer: {metadata.get('manufacturer', 'Not found')}")

    # 7. Submission format validation
    print("\n7. Submission Format Validation:")
    validation = validate_submission_format.invoke(
        {"document": sample_doc1, "submission_type": "510k"}
    )
    print(f"   Overall status: {validation['overall_status']}")
    print(f"   Estimated pages: {validation['page_count']['estimated']}")

    # 8. Regulatory database search (mock)
    print("\n8. Regulatory Database Search:")
    search_results = search_regulatory_database.invoke(
        {"query": "cardiac monitoring device", "document_type": "guidance"}
    )
    print(f"   Found {search_results['total_results']} results")
    if search_results["results"]:
        print(f"   Top result: {search_results['results'][0]['title']}")

    print("\n✅ Tools demo completed successfully!")


if __name__ == "__main__":
    main()
