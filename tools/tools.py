"""
Agentic tools for FDA Regulatory Assistant.

This module contains LangChain tools that can be used by agents for
document processing, regulatory analysis, and compliance checking.
"""

from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken
import re
from datetime import datetime
from ragchains.chain_manager import get_chain_manager


def tiktoken_len(text: str) -> int:
    """Calculate length of text in tokens using tiktoken"""
    tokens = tiktoken.encoding_for_model("gpt-4").encode(text)
    return len(tokens)


@tool
def chunk_document(
    docs: List[Document], chunk_size: int = 1000, chunk_overlap: int = 80
) -> List[Document]:
    """
    Chunk a document into smaller sections for processing.

    Args:
        docs: List of Document objects to chunk
        chunk_size: Maximum size of each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks

    Returns:
        List of chunked Document objects
    """
    # Create text splitter with token-aware chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=tiktoken_len
    )

    # Split documents into chunks
    chunked_docs = text_splitter.split_documents(docs)

    return chunked_docs


@tool
def search_regulatory_database(
    query: str, document_type: str = "all"
) -> Dict[str, Any]:
    """
    Search through regulatory documents for specific information.

    Args:
        query: Search query string
        document_type: Type of document to search ("guidance", "regulation", "standard", "all")

    Returns:
        Dictionary containing search results with relevance scores
    """
    # This is a placeholder implementation
    # In a real implementation, this would interface with a vector database
    # or search engine containing regulatory documents

    search_results = {
        "query": query,
        "document_type": document_type,
        "results": [
            {
                "title": f"FDA Guidance on {query}",
                "relevance_score": 0.95,
                "document_id": "FDA-2023-001",
                "summary": f"Regulatory guidance related to {query}",
                "url": "https://fda.gov/guidance/example",
            }
        ],
        "total_results": 1,
        "search_timestamp": datetime.now().isoformat(),
    }

    return search_results


@tool
def analyze_document_compliance(
    document: Document, regulation_type: str = "510k"
) -> Dict[str, Any]:
    """
    Analyze a document for compliance with specific FDA regulations.

    Args:
        document: Document to analyze
        regulation_type: Type of regulation to check against ("510k", "pma", "de_novo", "qsr")

    Returns:
        Dictionary containing compliance analysis results
    """
    content = document.page_content

    # Define compliance criteria based on regulation type
    compliance_criteria = {
        "510k": [
            "predicate device identification",
            "substantial equivalence comparison",
            "safety and effectiveness data",
            "labeling information",
            "risk analysis",
        ],
        "pma": [
            "clinical data",
            "manufacturing information",
            "risk-benefit analysis",
            "labeling",
            "quality system information",
        ],
        "de_novo": [
            "classification rationale",
            "risk classification",
            "special controls",
            "clinical data",
            "predicate device analysis",
        ],
        "qsr": [
            "design controls",
            "document controls",
            "management responsibility",
            "corrective and preventive actions",
            "production and process controls",
        ],
        "cybersecurity": [
            "SOUP documentation",
            "cybersecurity risk assessment",
            "vulnerability management",
            "security controls implementation",
            "threat modeling",
            "security testing documentation",
            "incident response plan",
            "security architecture documentation",
        ],
    }

    criteria = compliance_criteria.get(regulation_type, compliance_criteria["510k"])

    # Simple keyword-based compliance check
    compliance_results = {}
    for criterion in criteria:
        # Check if criterion-related keywords are present
        keywords = criterion.split()
        found_keywords = [kw for kw in keywords if kw.lower() in content.lower()]
        compliance_score = len(found_keywords) / len(keywords)

        compliance_results[criterion] = {
            "score": compliance_score,
            "found_keywords": found_keywords,
            "status": "compliant" if compliance_score > 0.5 else "needs_attention",
        }

    overall_score = sum(
        result["score"] for result in compliance_results.values()
    ) / len(compliance_results)

    return {
        "regulation_type": regulation_type,
        "overall_compliance_score": overall_score,
        "criteria_analysis": compliance_results,
        "recommendations": [
            f"Review {criterion}"
            for criterion, result in compliance_results.items()
            if result["status"] == "needs_attention"
        ],
        "analysis_timestamp": datetime.now().isoformat(),
    }


@tool
def extract_regulatory_requirements(
    document: Document, requirement_type: str = "all"
) -> List[Dict[str, Any]]:
    """
    Extract regulatory requirements from a document.

    Args:
        document: Document to extract requirements from
        requirement_type: Type of requirements to extract ("clinical", "technical", "quality", "all")

    Returns:
        List of extracted requirements with metadata
    """
    content = document.page_content

    # Pattern matching for common requirement indicators
    requirement_patterns = {
        "clinical": [
            r"clinical\s+(?:study|trial|data|evidence)",
            r"safety\s+and\s+effectiveness",
            r"clinical\s+evaluation",
        ],
        "technical": [
            r"technical\s+(?:specification|requirement|standard)",
            r"performance\s+(?:criteria|standard|requirement)",
            r"design\s+(?:control|requirement|specification)",
        ],
        "quality": [
            r"quality\s+(?:system|management|control)",
            r"ISO\s+\d+",
            r"good\s+manufacturing\s+practice",
        ],
    }

    if requirement_type == "all":
        patterns = []
        for pattern_list in requirement_patterns.values():
            patterns.extend(pattern_list)
    else:
        patterns = requirement_patterns.get(requirement_type, [])

    requirements = []
    for i, pattern in enumerate(patterns):
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # Extract surrounding context
            start = max(0, match.start() - 100)
            end = min(len(content), match.end() + 100)
            context = content[start:end].strip()

            requirements.append(
                {
                    "requirement_id": f"REQ_{i + 1}_{len(requirements) + 1}",
                    "type": requirement_type,
                    "matched_text": match.group(),
                    "context": context,
                    "position": match.start(),
                    "confidence": 0.8,  # Simple confidence score
                }
            )

    return requirements


@tool
def validate_submission_format(
    document: Document, submission_type: str = "510k"
) -> Dict[str, Any]:
    """
    Validate document format against FDA submission requirements.

    Args:
        document: Document to validate
        submission_type: Type of submission ("510k", "pma", "de_novo", "ide")

    Returns:
        Dictionary containing validation results
    """
    content = document.page_content

    # Define format requirements for different submission types
    format_requirements = {
        "510k": {
            "required_sections": [
                "device description",
                "intended use",
                "substantial equivalence comparison",
                "performance data",
                "labeling",
            ],
            "max_pages": 150,
            "required_metadata": ["device_name", "classification"],
        },
        "pma": {
            "required_sections": [
                "device description",
                "clinical studies",
                "manufacturing information",
                "risk analysis",
                "labeling",
            ],
            "max_pages": 500,
            "required_metadata": ["device_name", "clinical_sites"],
        },
    }

    requirements = format_requirements.get(submission_type, format_requirements["510k"])

    # Check for required sections
    section_validation = {}
    for section in requirements["required_sections"]:
        section_found = section.lower() in content.lower()
        section_validation[section] = {
            "present": section_found,
            "status": "valid" if section_found else "missing",
        }

    # Estimate page count (rough approximation)
    estimated_pages = len(content) // 2000  # Assuming ~2000 chars per page

    validation_results = {
        "submission_type": submission_type,
        "section_validation": section_validation,
        "page_count": {
            "estimated": estimated_pages,
            "max_allowed": requirements["max_pages"],
            "status": "valid"
            if estimated_pages <= requirements["max_pages"]
            else "exceeds_limit",
        },
        "overall_status": "valid",  # Would be calculated based on all checks
        "validation_timestamp": datetime.now().isoformat(),
    }

    return validation_results


@tool
def generate_compliance_checklist(
    regulation_type: str = "510k", device_class: str = "II"
) -> Dict[str, Any]:
    """
    Generate a compliance checklist for a specific regulation and device class.

    Args:
        regulation_type: Type of regulation ("510k", "pma", "de_novo", "qsr")
        device_class: FDA device class ("I", "II", "III")

    Returns:
        Dictionary containing structured compliance checklist
    """
    # Define checklist items based on regulation type and device class
    checklists = {
        "510k": {
            "I": [
                "Device description and intended use",
                "Predicate device identification",
                "Comparison table with predicate",
                "Performance testing data",
                "Labeling information",
            ],
            "II": [
                "Device description and intended use",
                "Predicate device identification",
                "Substantial equivalence comparison",
                "Performance testing data",
                "Software documentation (if applicable)",
                "Biocompatibility data",
                "Sterilization validation (if applicable)",
                "Labeling information",
                "Risk analysis",
            ],
            "III": [
                "Device description and intended use",
                "Predicate device identification",
                "Substantial equivalence comparison",
                "Clinical data",
                "Performance testing data",
                "Software documentation (if applicable)",
                "Biocompatibility data",
                "Sterilization validation (if applicable)",
                "Labeling information",
                "Risk analysis",
                "Quality system information",
            ],
        },
        "pma": {
            "III": [
                "Device description and intended use",
                "Clinical protocol and data",
                "Manufacturing information",
                "Risk-benefit analysis",
                "Non-clinical laboratory studies",
                "Software documentation (if applicable)",
                "Biocompatibility data",
                "Sterilization validation (if applicable)",
                "Labeling information",
                "Quality system information",
                "Post-market study commitments",
            ]
        },
    }

    checklist_items = checklists.get(regulation_type, {}).get(device_class, [])

    # Create structured checklist with status tracking
    checklist = {
        "regulation_type": regulation_type,
        "device_class": device_class,
        "total_items": len(checklist_items),
        "items": [
            {
                "id": f"ITEM_{i + 1:03d}",
                "description": item,
                "status": "pending",
                "priority": "high" if i < 3 else "medium",
                "notes": "",
            }
            for i, item in enumerate(checklist_items)
        ],
        "completion_percentage": 0,
        "generated_timestamp": datetime.now().isoformat(),
    }

    return checklist


@tool
def compare_documents(
    doc1: Document, doc2: Document, comparison_type: str = "content"
) -> Dict[str, Any]:
    """
    Compare two documents for similarities and differences.

    Args:
        doc1: First document to compare
        doc2: Second document to compare
        comparison_type: Type of comparison ("content", "structure", "metadata")

    Returns:
        Dictionary containing comparison results
    """
    if comparison_type == "content":
        # Simple content similarity using word overlap
        words1 = set(doc1.page_content.lower().split())
        words2 = set(doc2.page_content.lower().split())

        common_words = words1.intersection(words2)
        total_words = words1.union(words2)

        similarity_score = len(common_words) / len(total_words) if total_words else 0

        comparison_result = {
            "comparison_type": comparison_type,
            "similarity_score": similarity_score,
            "common_words_count": len(common_words),
            "unique_to_doc1": len(words1 - words2),
            "unique_to_doc2": len(words2 - words1),
            "total_unique_words": len(total_words),
            "doc1_length": len(doc1.page_content),
            "doc2_length": len(doc2.page_content),
        }

    elif comparison_type == "metadata":
        # Compare metadata
        meta1 = doc1.metadata
        meta2 = doc2.metadata

        common_keys = set(meta1.keys()).intersection(set(meta2.keys()))
        matching_values = sum(
            1 for key in common_keys if meta1.get(key) == meta2.get(key)
        )

        comparison_result = {
            "comparison_type": comparison_type,
            "common_metadata_keys": list(common_keys),
            "matching_values_count": matching_values,
            "doc1_unique_keys": list(set(meta1.keys()) - set(meta2.keys())),
            "doc2_unique_keys": list(set(meta2.keys()) - set(meta1.keys())),
            "metadata_similarity": matching_values / len(common_keys)
            if common_keys
            else 0,
        }

    else:  # structure comparison
        # Simple structure comparison based on line counts and patterns
        lines1 = doc1.page_content.split("\n")
        lines2 = doc2.page_content.split("\n")

        comparison_result = {
            "comparison_type": comparison_type,
            "doc1_line_count": len(lines1),
            "doc2_line_count": len(lines2),
            "line_count_difference": abs(len(lines1) - len(lines2)),
            "structure_similarity": 1
            - (abs(len(lines1) - len(lines2)) / max(len(lines1), len(lines2))),
        }

    comparison_result["comparison_timestamp"] = datetime.now().isoformat()
    return comparison_result


@tool
def extract_document_metadata(document: Document) -> Dict[str, Any]:
    """
    Extract and enhance metadata from a document.

    Args:
        document: Document to extract metadata from

    Returns:
        Dictionary containing extracted and enhanced metadata
    """
    content = document.page_content
    existing_metadata = document.metadata.copy()

    # Extract additional metadata from content
    enhanced_metadata = existing_metadata.copy()

    # Extract dates
    date_patterns = [
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",  # MM/DD/YYYY
        r"\b\d{4}-\d{2}-\d{2}\b",  # YYYY-MM-DD
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
    ]

    dates_found = []
    for pattern in date_patterns:
        dates_found.extend(re.findall(pattern, content, re.IGNORECASE))

    # Extract device-related information
    device_patterns = {
        "device_name": r"(?:device\s+name|product\s+name):\s*([^\n]+)",
        "manufacturer": r"(?:manufacturer|company):\s*([^\n]+)",
        "model_number": r"(?:model\s+(?:number|#)):\s*([^\n]+)",
        "classification": r"(?:class\s+(?:I{1,3}|1|2|3)|classification):\s*([^\n]+)",
    }

    for key, pattern in device_patterns.items():
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            enhanced_metadata[key] = match.group(1).strip()

    # Calculate content statistics
    enhanced_metadata.update(
        {
            "content_length": len(content),
            "word_count": len(content.split()),
            "line_count": len(content.split("\n")),
            "paragraph_count": len([p for p in content.split("\n\n") if p.strip()]),
            "dates_found": dates_found,
            "extraction_timestamp": datetime.now().isoformat(),
        }
    )

    return enhanced_metadata


@tool
def retrieve_cybersecurity_information(question: str) -> Dict[str, Any]:
    """
    Retrieve cybersecurity information from the pre-loaded cybersecurity RAG chain.

    Args:
        question: The cybersecurity question to ask

    Returns:
        Dictionary containing cybersecurity information with answer and sources
    """
    chain_manager = get_chain_manager()
    return chain_manager.query_cybersecurity_chain_sync(question)


@tool
def retrieve_regulatory_information(question: str) -> Dict[str, Any]:
    """
    Retrieve regulatory information from the pre-loaded regulatory RAG chain.

    Args:
        question: The regulatory question to ask

    Returns:
        Dictionary containing regulatory information with answer and sources
    """
    chain_manager = get_chain_manager()
    return chain_manager.query_regulatory_chain_sync(question)


@tool
def process_uploaded_documents(files_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process uploaded documents from a regulatory submission package.

    Args:
        files_data: List of file data dictionaries with 'name', 'content', 'type'

    Returns:
        Dictionary containing processed documents and metadata
    """
    processed_docs = []
    document_types = {}

    for file_data in files_data:
        # Create document object
        doc = Document(
            page_content=file_data.get("content", ""),
            metadata={
                "source": file_data.get("name", "unknown"),
                "file_type": file_data.get("type", "unknown"),
                "size": len(file_data.get("content", "")),
                "processed_timestamp": datetime.now().isoformat(),
            },
        )
        processed_docs.append(doc)

        # Categorize document type
        filename = file_data.get("name", "").lower()
        if any(term in filename for term in ["clinical", "study", "trial"]):
            doc_type = "clinical"
        elif any(term in filename for term in ["technical", "specification", "design"]):
            doc_type = "technical"
        elif any(term in filename for term in ["quality", "qms", "iso"]):
            doc_type = "quality"
        elif any(term in filename for term in ["cyber", "security", "soup"]):
            doc_type = "cybersecurity"
        elif any(term in filename for term in ["label", "ifu", "instruction"]):
            doc_type = "labeling"
        else:
            doc_type = "general"

        document_types[file_data.get("name", "unknown")] = doc_type

    return {
        "processed_documents": processed_docs,
        "document_count": len(processed_docs),
        "document_types": document_types,
        "total_content_length": sum(len(doc.page_content) for doc in processed_docs),
        "processing_timestamp": datetime.now().isoformat(),
    }


@tool
def convert_uploaded_files_to_documents(
    files_data: List[Dict[str, Any]],
) -> List[Document]:
    """
    Convert uploaded file data to LangChain Document objects.

    Args:
        files_data: List of file data dictionaries with 'name', 'content', 'type', 'size'

    Returns:
        List of Document objects ready for processing
    """
    documents = []

    for file_data in files_data:
        # Skip error files
        if file_data.get("type") == "error":
            continue

        # Create document object
        doc = Document(
            page_content=file_data.get("content", ""),
            metadata={
                "source": file_data.get("name", "unknown"),
                "file_type": file_data.get("type", "unknown"),
                "file_size": file_data.get("size", 0),
                "processed_timestamp": datetime.now().isoformat(),
            },
        )
        documents.append(doc)

    return documents


@tool
def process_uploaded_files_from_state(state_info: str) -> Dict[str, Any]:
    """
    Process uploaded files from the workflow state.

    This tool is designed to work with the document processor agent
    to extract and process uploaded files from the state.

    Args:
        state_info: Information about the current state (not used directly,
                   but required for tool signature)

    Returns:
        Dictionary containing processing results and status
    """
    # This is a placeholder tool that will be enhanced to work with state
    # For now, return a message indicating the tool was called
    return {
        "status": "tool_called",
        "message": "Document processor tool was invoked. Files should be processed by the agent using uploaded_files from state.",
        "processed_documents": [],
        "document_count": 0,
        "processing_timestamp": datetime.now().isoformat(),
    }


@tool
def perform_gap_analysis(
    cybersecurity_findings: Dict[str, Any],
    regulatory_findings: Dict[str, Any],
    documents: List[Document],
) -> Dict[str, Any]:
    """
    Perform comprehensive gap analysis based on cybersecurity and regulatory findings.

    Args:
        cybersecurity_findings: Results from cybersecurity agent analysis
        regulatory_findings: Results from regulatory agent analysis
        documents: List of processed documents

    Returns:
        Dictionary containing comprehensive gap analysis results
    """
    gaps = []
    recommendations = []

    # Analyze cybersecurity gaps - FIXED: Handle the actual structure from analyze_document_compliance
    if cybersecurity_findings:
        # Check if cybersecurity findings have the expected "gaps" field
        cyber_gaps = cybersecurity_findings.get("gaps", [])

        # If no gaps field, extract gaps from criteria_analysis (from analyze_document_compliance)
        if not cyber_gaps and "criteria_analysis" in cybersecurity_findings:
            criteria_analysis = cybersecurity_findings["criteria_analysis"]
            for criterion, result in criteria_analysis.items():
                if result.get("status") == "needs_attention":
                    # Determine severity based on compliance score and cybersecurity criticality
                    score = result.get("score", 0)
                    # Cybersecurity gaps are generally more critical
                    if score == 0:
                        severity = "critical"
                    elif score < 0.4:  # Slightly higher threshold for cybersecurity
                        severity = "major"
                    else:
                        severity = "minor"

                    gaps.append(
                        {
                            "category": "cybersecurity",
                            "severity": severity,
                            "description": f"Missing or insufficient {criterion}",
                            "requirement": criterion,
                            "evidence": f"Found keywords: {result.get('found_keywords', [])}",
                            "recommendation": f"Implement comprehensive {criterion} documentation and controls",
                        }
                    )
        else:
            # Handle existing gaps format
            for gap in cyber_gaps:
                gaps.append(
                    {
                        "category": "cybersecurity",
                        "severity": gap.get("severity", "medium"),
                        "description": gap.get("description", ""),
                        "requirement": gap.get("requirement", ""),
                        "evidence": gap.get("evidence", ""),
                        "recommendation": gap.get("recommendation", ""),
                    }
                )

    # Analyze regulatory gaps - FIXED: Handle the actual structure from analyze_document_compliance
    if regulatory_findings:
        # Check if regulatory findings have the expected "gaps" field
        reg_gaps = regulatory_findings.get("gaps", [])

        # If no gaps field, extract gaps from criteria_analysis (from analyze_document_compliance)
        if not reg_gaps and "criteria_analysis" in regulatory_findings:
            criteria_analysis = regulatory_findings["criteria_analysis"]
            for criterion, result in criteria_analysis.items():
                if result.get("status") == "needs_attention":
                    # Determine severity based on compliance score
                    score = result.get("score", 0)
                    if score == 0:
                        severity = "critical"
                    elif score < 0.3:
                        severity = "major"
                    else:
                        severity = "minor"

                    gaps.append(
                        {
                            "category": "regulatory",
                            "severity": severity,
                            "description": f"Missing or insufficient {criterion}",
                            "requirement": criterion,
                            "evidence": f"Found keywords: {result.get('found_keywords', [])}",
                            "recommendation": f"Review and include comprehensive {criterion} section",
                        }
                    )
        else:
            # Handle existing gaps format
            for gap in reg_gaps:
                gaps.append(
                    {
                        "category": "regulatory",
                        "severity": gap.get("severity", "medium"),
                        "description": gap.get("description", ""),
                        "requirement": gap.get("requirement", ""),
                        "evidence": gap.get("evidence", ""),
                        "recommendation": gap.get("recommendation", ""),
                    }
                )

    # Calculate overall compliance score based on actual gaps found
    if gaps:
        # Use a more realistic calculation based on the number of gaps
        total_possible_requirements = 10  # Base requirements for a typical 510k submission
        compliance_score = max(0, (total_possible_requirements - len(gaps)) / total_possible_requirements)
    else:
        # If no gaps found, check if we actually analyzed anything
        # Combine scores from both cybersecurity and regulatory analysis
        scores = []
        if regulatory_findings and "overall_compliance_score" in regulatory_findings:
            scores.append(regulatory_findings["overall_compliance_score"])
        if cybersecurity_findings and "overall_compliance_score" in cybersecurity_findings:
            scores.append(cybersecurity_findings["overall_compliance_score"])

        if scores:
            # Use the average of available scores
            compliance_score = sum(scores) / len(scores)
        else:
            compliance_score = 1.0  # Default to perfect if no analysis data

    # Categorize gaps by severity
    critical_gaps = [g for g in gaps if g["severity"] == "critical"]
    major_gaps = [g for g in gaps if g["severity"] == "major"]
    minor_gaps = [g for g in gaps if g["severity"] == "minor"]

    # Generate recommendations
    if critical_gaps:
        recommendations.append(
            {
                "priority": "immediate",
                "action": "Address critical compliance gaps before submission",
                "timeline": "1-2 weeks",
                "effort": "high",
            }
        )

    if major_gaps:
        recommendations.append(
            {
                "priority": "high",
                "action": "Resolve major gaps to ensure submission success",
                "timeline": "2-4 weeks",
                "effort": "medium",
            }
        )

    # Determine readiness assessment based on gaps and compliance score
    if critical_gaps:
        readiness = "not_ready"
    elif major_gaps or compliance_score < 0.7:
        readiness = "needs_updates"
    elif compliance_score < 0.9:
        readiness = "needs_minor_updates"
    else:
        readiness = "ready"

    return {
        "overall_compliance_score": compliance_score,
        "total_gaps": len(gaps),
        "critical_gaps": critical_gaps,
        "major_gaps": major_gaps,
        "minor_gaps": minor_gaps,
        "recommendations": recommendations,
        "readiness_assessment": readiness,
        "analysis_timestamp": datetime.now().isoformat(),
    }


@tool
def generate_gap_analysis_report(
    gap_analysis: Dict[str, Any],
    cybersecurity_analysis: Dict[str, Any],
    regulatory_analysis: Dict[str, Any],
    document_metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate a comprehensive gap analysis report.

    Args:
        gap_analysis: Results from gap analysis
        cybersecurity_analysis: Cybersecurity findings
        regulatory_analysis: Regulatory findings
        document_metadata: Metadata about processed documents

    Returns:
        Dictionary containing formatted report and executive summary
    """

    # Generate executive summary
    compliance_score = gap_analysis.get("overall_compliance_score", 0)
    total_gaps = gap_analysis.get("total_gaps", 0)
    critical_gaps = len(gap_analysis.get("critical_gaps", []))

    executive_summary = f"""
EXECUTIVE SUMMARY - FDA REGULATORY SUBMISSION GAP ANALYSIS

Overall Compliance Score: {compliance_score:.1%}
Total Gaps Identified: {total_gaps}
Critical Issues: {critical_gaps}

Readiness Assessment: {gap_analysis.get("readiness_assessment", "Unknown").upper()}

Key Findings:
- {len(gap_analysis.get("critical_gaps", []))} critical gaps requiring immediate attention
- {len(gap_analysis.get("major_gaps", []))} major gaps needing resolution
- {len(gap_analysis.get("minor_gaps", []))} minor gaps for improvement

Recommendation: {"PROCEED WITH CAUTION" if compliance_score < 0.8 else "READY FOR SUBMISSION" if compliance_score > 0.9 else "ADDRESS GAPS BEFORE SUBMISSION"}
"""

    # Generate detailed report
    report_sections = []

    # Document overview
    report_sections.append(f"""
1. DOCUMENT OVERVIEW
   - Total Documents Analyzed: {document_metadata.get("document_count", 0)}
   - Document Types: {", ".join(document_metadata.get("document_types", {}).values())}
   - Total Content Length: {document_metadata.get("total_content_length", 0):,} characters
""")

    # Cybersecurity findings
    if cybersecurity_analysis:
        report_sections.append(f"""
2. CYBERSECURITY ANALYSIS
   - Compliance Score: {cybersecurity_analysis.get("compliance_score", "N/A")}
   - Key Findings: {len(cybersecurity_analysis.get("findings", []))} items identified
   - SOUP Documentation: {"Complete" if cybersecurity_analysis.get("soup_complete") else "Incomplete"}
""")

    # Regulatory findings
    if regulatory_analysis:
        report_sections.append(f"""
3. REGULATORY ANALYSIS
   - 510K Readiness: {regulatory_analysis.get("readiness_level", "Unknown")}
   - Required Sections: {len(regulatory_analysis.get("required_sections", []))} identified
   - Missing Elements: {len(regulatory_analysis.get("missing_elements", []))} found
""")

    # Gap analysis details
    report_sections.append(f"""
4. GAP ANALYSIS DETAILS

Critical Gaps ({len(gap_analysis.get("critical_gaps", []))}):
""")

    for i, gap in enumerate(gap_analysis.get("critical_gaps", [])[:5], 1):
        report_sections.append(f"   {i}. {gap.get('description', 'No description')}")

    report_sections.append(f"""
Major Gaps ({len(gap_analysis.get("major_gaps", []))}):
""")

    for i, gap in enumerate(gap_analysis.get("major_gaps", [])[:5], 1):
        report_sections.append(f"   {i}. {gap.get('description', 'No description')}")

    # Recommendations
    report_sections.append("""
5. RECOMMENDATIONS

Immediate Actions:
""")

    for i, rec in enumerate(gap_analysis.get("recommendations", [])[:3], 1):
        if rec.get("priority") == "immediate":
            report_sections.append(
                f"   {i}. {rec.get('action', 'No action specified')}"
            )

    full_report = "\n".join(report_sections)

    return {
        "executive_summary": executive_summary.strip(),
        "full_report": full_report.strip(),
        "report_metadata": {
            "generated_timestamp": datetime.now().isoformat(),
            "total_sections": len(report_sections),
            "compliance_score": compliance_score,
            "readiness_level": gap_analysis.get("readiness_assessment", "unknown"),
        },
    }


@tool
def identify_document_gaps(
    document: Document, regulation_type: str = "510k"
) -> Dict[str, Any]:
    """
    Identify specific gaps in a single document against regulatory requirements.

    Args:
        document: Document to analyze
        regulation_type: Type of regulation to check against

    Returns:
        Dictionary containing document-specific gap analysis
    """
    content = document.page_content.lower()
    metadata = document.metadata

    # Define required elements for different document types
    required_elements = {
        "510k": {
            "device_description": [
                "device description",
                "intended use",
                "indications for use",
            ],
            "predicate_comparison": [
                "predicate device",
                "substantial equivalence",
                "comparison",
            ],
            "performance_data": ["performance testing", "verification", "validation"],
            "risk_analysis": ["risk analysis", "risk management", "iso 14971"],
            "labeling": ["labeling", "instructions for use", "ifu"],
            "biocompatibility": [
                "biocompatibility",
                "iso 10993",
                "biological evaluation",
            ],
            "software": ["software documentation", "software lifecycle", "iec 62304"],
        }
    }

    elements = required_elements.get(regulation_type, required_elements["510k"])

    gaps = []
    present_elements = []

    for element_name, keywords in elements.items():
        found = any(keyword in content for keyword in keywords)

        if found:
            present_elements.append(element_name)
        else:
            gaps.append(
                {
                    "element": element_name,
                    "description": f"Missing or insufficient {element_name.replace('_', ' ')}",
                    "keywords_searched": keywords,
                    "severity": "major"
                    if element_name in ["device_description", "predicate_comparison"]
                    else "minor",
                    "recommendation": f"Include comprehensive {element_name.replace('_', ' ')} section",
                }
            )

    return {
        "document_name": metadata.get("source", "unknown"),
        "regulation_type": regulation_type,
        "gaps_found": gaps,
        "present_elements": present_elements,
        "compliance_percentage": len(present_elements) / len(elements) * 100,
        "analysis_timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    print(
        retrieve_cybersecurity_information(
            "What is the best way to secure a medical device?"
        )
    )
    print(
        retrieve_regulatory_information(
            "What are the requirements for a 510K submission?"
        )
    )
