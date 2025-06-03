"""
LangGraph agents for FDA Regulatory Assistant.

This module implements multi-agent workflow using LangGraph's built-in constructs
for clean communication and maintainable state management.
"""

import functools
from langchain_openai import ChatOpenAI
from graph.state import create_supervisor_agent, agent_node, create_agent
from tools import (
    retrieve_cybersecurity_information,
    retrieve_regulatory_information,
    analyze_document_compliance,
    generate_gap_analysis_report,
    identify_document_gaps,
    perform_gap_analysis,
    chunk_document,
)


def document_processor_node(state, name: str):
    """
    Special node function for document processor that handles file processing from state.
    """
    from langchain_core.messages import HumanMessage
    from langchain_core.documents import Document

    # Process uploaded files from state
    uploaded_files = state.get("uploaded_files", [])

    if uploaded_files:
        # Convert uploaded files to Document objects
        processed_docs = []
        for file_data in uploaded_files:
            if file_data.get("type") != "error":
                doc = Document(
                    page_content=file_data.get("content", ""),
                    metadata={
                        "source": file_data.get("name", "unknown"),
                        "file_type": file_data.get("type", "unknown"),
                        "file_size": file_data.get("size", 0),
                    },
                )
                processed_docs.append(doc)

        # Chunk documents if they're large
        if processed_docs:
            chunked_docs = chunk_document.invoke({"docs": processed_docs})

            # Create document metadata
            document_metadata = {
                "total_documents": len(uploaded_files),
                "document_names": [file_data.get('name', 'Unknown') for file_data in uploaded_files if file_data.get("type") != "error"],
                "processing_timestamp": "",
                "total_chunks": len(chunked_docs),
            }

            # Create response message
            response_content = (
                f"✅ Document processing complete!\n\n"
                f"📄 Processed {len(uploaded_files)} uploaded files\n"
                f"📝 Created {len(chunked_docs)} document chunks\n"
                f"🔍 Documents are now ready for compliance analysis\n\n"
                f"Files processed:\n"
            )

            for file_data in uploaded_files:
                if file_data.get("type") != "error":
                    response_content += f"- {file_data.get('name', 'Unknown')} ({file_data.get('type', 'unknown')})\n"

            response_content += (
                "\nDocuments are ready for cybersecurity and regulatory analysis."
            )

            # Return state updates
            return {
                "messages": [HumanMessage(content=response_content, name=name)],
                "processed_documents": chunked_docs,
                "document_metadata": document_metadata,
            }
        else:
            response_content = "⚠️ No valid documents found to process."
    else:
        response_content = "⚠️ No uploaded files found in the state."

    return {"messages": [HumanMessage(content=response_content, name=name)]}


def create_supervisor(llm: ChatOpenAI):
    """
    Create a supervisor with enhanced state awareness and error handling.
    """
    team_members = [
        "document_processor",
        "cybersecurity_agent",
        "regulatory_agent",
        "auditor_agent",
        "report_generator",
    ]

    system_prompt = (
        "You are an FDA auditor supervisor managing a team of specialists. Your role is to:"
        "\n1. Analyze conversation state and route to appropriate specialists"
        "\n2. Compile final responses as an authoritative FDA auditor"
        "\n3. Ensure efficient workflow progression without loops"
        "\n\nSTATE ANALYSIS FIRST:"
        "\nBefore routing, examine the conversation history to identify:"
        "\n- Which agents have already provided responses (check message names/signatures)"
        "\n- Workflow type: gap_analysis (files uploaded) or question_answering (no files)"
        "\n- Whether you've already provided a final FDA auditor assessment"
        "\n- The EXACT keywords in the user's question to determine correct agent"
        "\n\nROUTING RULES:"
        "\n- Gap analysis: document_processor → cybersecurity_agent → regulatory_agent → auditor_agent → report_generator → FINISH"
        "\n- Question answering: Route to ONE specialist FIRST, then FINISH only AFTER they respond with sources"
        "\n- NEVER provide direct answers - ALWAYS route to specialists first to get sources and detailed analysis"
        "\n- NEVER route to an agent that has already responded"
        "\n- ALWAYS progress forward in the sequence"
        "\n\nAGENT SELECTION RULES (CRITICAL - FOLLOW EXACTLY):"
        "\n- CYBERSECURITY AGENT: Use for questions containing these keywords:"
        "\n  * cybersecurity, cyber security, cyber-security"
        "\n  * SOUP, software of unknown provenance"
        "\n  * vulnerability, vulnerabilities, CVE, CWE"
        "\n  * security, threat, malware, encryption"
        "\n  * penetration testing, security testing"
        "\n  * authentication, authorization"
        "\n- REGULATORY AGENT: Use for questions containing these keywords:"
        "\n  * 510K, 510(k), predicate device"
        "\n  * PMA, premarket approval"
        "\n  * regulatory, submission, FDA approval"
        "\n  * compliance (without cybersecurity context)"
        "\n  * guidance documents, regulatory pathway"
        "\n  * QSR, quality system regulation"
        "\n- IMPORTANT: If question contains BOTH cybersecurity AND regulatory keywords, choose cybersecurity_agent"
        "\n- If unclear, analyze the PRIMARY focus of the question"
        "\n\nTERMINATION CONDITIONS (CRITICAL - ALWAYS FOLLOW):"
        "\n- Question answering: FINISH only AFTER a specialist has responded with analysis and sources"
        "\n- Gap analysis: FINISH only after report_generator completes"
        "\n- If you've already provided final assessment: FINISH"
        "\n- If 6+ agent messages exist: FINISH with summary"
        "\n- NEVER route to the same agent twice - check message history first"
        "\n\nFINAL RESPONSE (when next=FINISH):"
        "\nProvide comprehensive FDA auditor assessment including:"
        "\n- Synthesized findings from specialist analysis"
        "\n- Regulatory context and compliance requirements"
        "\n- Clear recommendations and next steps"
        "\n- Professional, authoritative tone"
        "\n- End with: 'Do you need any additional clarifications?'"
        "\n\nERROR HANDLING:"
        "\n- If workflow type unclear: assume question_answering"
        "\n- If no agent match: route to regulatory_agent"
        "\n- If routing impossible: FINISH with available information"
    )

    return create_supervisor_agent(llm, system_prompt, team_members)


def create_document_processor(llm: ChatOpenAI = None):
    """
    Create a document processor agent that handles file processing and document preparation.

    Note: llm parameter is kept for consistency with other agent creation functions,
    but is not used since document processing is handled directly from state.
    """
    return functools.partial(document_processor_node, name="document_processor")


def create_cybersecurity_agent(llm: ChatOpenAI):
    """
    Create a cybersecurity agent using the helper functions.
    """
    tools = [retrieve_cybersecurity_information, analyze_document_compliance]

    system_prompt = (
        "You are a cybersecurity specialist focused on FDA cybersecurity guidance. "
        "Analyze documents and questions for cybersecurity compliance issues. "
        "Use your tools to retrieve relevant information and provide detailed analysis."
    )

    agent = create_agent(llm, tools, system_prompt)
    return functools.partial(agent_node, agent=agent, name="cybersecurity_agent")


def create_regulatory_agent(llm: ChatOpenAI):
    """
    Create a regulatory agent using the helper functions.
    """
    tools = [retrieve_regulatory_information, analyze_document_compliance]

    system_prompt = (
        "You are a regulatory specialist focused on FDA regulatory guidance. "
        "Analyze documents and questions for regulatory compliance issues. "
        "For gap analysis workflows, analyze the processed documents for regulatory compliance. "
        "Use your tools to retrieve relevant information and provide detailed regulatory analysis. "
        "Focus on FDA regulatory requirements, submission guidelines, and compliance standards."
    )

    agent = create_agent(llm, tools, system_prompt)
    return functools.partial(agent_node, agent=agent, name="regulatory_agent")


def create_auditor_agent(llm: ChatOpenAI):
    """
    Create an auditor agent using the helper functions.
    """
    def auditor_agent_node(state):
        """
        Custom auditor agent node that performs gap analysis using state data.
        """
        from langchain_core.messages import HumanMessage

        # Extract analysis data from state
        cybersecurity_analysis = state.get("cybersecurity_analysis", {})
        regulatory_analysis = state.get("regulatory_analysis", {})
        processed_documents = state.get("processed_documents", [])

        # Perform gap analysis using the tool
        try:
            gap_analysis_result = perform_gap_analysis.invoke({
                "cybersecurity_findings": cybersecurity_analysis,
                "regulatory_findings": regulatory_analysis,
                "documents": processed_documents,
            })

            # Format the response
            compliance_score = gap_analysis_result.get("overall_compliance_score", 0)
            total_gaps = gap_analysis_result.get("total_gaps", 0)
            readiness = gap_analysis_result.get("readiness_assessment", "unknown")

            response_content = f"""**AUDITOR ASSESSMENT**

Compliance Analysis Complete:
- Overall Compliance Score: {compliance_score:.1%}
- Total Gaps Identified: {total_gaps}
- Readiness Assessment: {readiness.upper()}

Critical Issues: {len(gap_analysis_result.get("critical_gaps", []))}
Major Issues: {len(gap_analysis_result.get("major_gaps", []))}
Minor Issues: {len(gap_analysis_result.get("minor_gaps", []))}

The comprehensive gap analysis has been completed and is ready for report generation.
"""

            # Store the gap analysis in state
            return {
                "messages": [HumanMessage(content=response_content, name="auditor_agent")],
                "gap_analysis": gap_analysis_result
            }

        except Exception as e:
            response_content = f"Error performing gap analysis: {str(e)}. Available data: cybersecurity_analysis={bool(cybersecurity_analysis)}, regulatory_analysis={bool(regulatory_analysis)}, documents={len(processed_documents)}"
            return {"messages": [HumanMessage(content=response_content, name="auditor_agent")]}

    return auditor_agent_node


def create_report_generator(llm: ChatOpenAI):
    """
    Create a report generator using the helper functions.
    """
    def report_generator_node(state):
        """
        Custom report generator node that directly accesses state data.
        """
        from langchain_core.messages import HumanMessage

        # Extract analysis data from state
        gap_analysis = state.get("gap_analysis", {})
        cybersecurity_analysis = state.get("cybersecurity_analysis", {})
        regulatory_analysis = state.get("regulatory_analysis", {})
        document_metadata = state.get("document_metadata", {})

        # Check if we have the required data
        if not gap_analysis:
            # If no gap analysis data, create a basic one from available data
            gap_analysis = {
                "overall_compliance_score": 0.5,
                "total_gaps": 0,
                "critical_gaps": [],
                "major_gaps": [],
                "minor_gaps": [],
                "recommendations": [],
                "readiness_assessment": "needs_analysis",
                "analysis_timestamp": "",
            }

        # Call the tool directly with state data
        try:
            report_result = generate_gap_analysis_report.invoke({
                "gap_analysis": gap_analysis,
                "cybersecurity_analysis": cybersecurity_analysis,
                "regulatory_analysis": regulatory_analysis,
                "document_metadata": document_metadata,
            })

            # Format the response
            executive_summary = report_result.get("executive_summary", "")
            full_report = report_result.get("full_report", "")

            response_content = f"""**COMPLIANCE GAP ANALYSIS REPORT**

{executive_summary}

---

{full_report}
"""

        except Exception as e:
            response_content = f"Error generating report: {str(e)}. Available data: gap_analysis={bool(gap_analysis)}, cybersecurity_analysis={bool(cybersecurity_analysis)}, regulatory_analysis={bool(regulatory_analysis)}, document_metadata={bool(document_metadata)}"

        return {"messages": [HumanMessage(content=response_content, name="report_generator")]}

    return report_generator_node
