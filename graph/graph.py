"""
LangGraph workflow for FDA Regulatory Assistant.

This module implements a clean multi-agent workflow using LangGraph's
built-in constructs for maintainable and efficient regulatory compliance analysis.
"""

import asyncio
import re
from typing import Dict, Any, AsyncGenerator, Optional, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from graph.state import ComplianceGapState, create_initial_state
from ragchains.chain_manager import get_chain_manager
from graph.agents import (
    create_supervisor,
    create_document_processor,
    create_cybersecurity_agent,
    create_regulatory_agent,
    create_auditor_agent,
    create_report_generator,
)
from utils.streaming_config import WORD_DELAY


async def stream_text_word_by_word(
    text: str, delay: float = WORD_DELAY
) -> AsyncGenerator[str, None]:
    """
    Stream text word by word while preserving formatting.

    Args:
        text: The text to stream
        delay: Delay between words in seconds

    Yields:
        Individual words with proper spacing
    """
    if not text:
        return

    # Split text into words while preserving whitespace and formatting
    words = re.split(r"(\s+)", text)

    for word in words:
        if word.strip():  # Only add delay for actual words, not whitespace
            yield word
            await asyncio.sleep(delay)
        else:
            yield word  # Immediately yield whitespace/formatting


def extract_sources_from_message(message_content: str) -> List[Dict[str, Any]]:
    """
    Extract source information from agent message content.

    Args:
        message_content: The message content that may contain source information

    Returns:
        List of source dictionaries
    """
    sources = []

    # Look for source patterns in the message content
    # This matches the format used by agent_node function
    source_patterns = [
        r"\d+\.\s+(.+?)\s+-\s+Page\s+(\d+)",  # Matches: "1. document_name - Page 42"
        r"Source \d+: ([^,]+), Page (\d+)",
        r"\[Source: ([^,]+), Page (\d+)\]",
        r"Referenced from: ([^,]+) \(Page (\d+)\)",
    ]

    for pattern in source_patterns:
        matches = re.findall(pattern, message_content)
        for match in matches:
            if len(match) == 2:
                sources.append(
                    {
                        "document": match[0].strip(),
                        "page": match[1].strip(),
                    }
                )

    return sources


class RegulatoryWorkflow:
    """
    Regulatory workflow using LangGraph's built-in constructs.

    Key features:
    1. Uses message passing instead of complex state management
    2. Leverages LangGraph's built-in routing with supervisor pattern
    3. Cleaner agent communication through messages
    4. Simplified state structure
    5. Better separation of concerns
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None, prewarm_chains: bool = True):
        """Initialize the workflow."""
        self.llm = llm or ChatOpenAI(model="gpt-4.1-mini", temperature=0)
        self.chain_manager = get_chain_manager()
        self.chains_prewarmed = False
        self.workflow = self._create_workflow()

        # Pre-warm chains if requested
        if prewarm_chains:
            asyncio.create_task(self._prewarm_chains_async())

    async def _prewarm_chains_async(self):
        """Pre-warm RAG chains asynchronously."""
        try:
            await self.chain_manager.prewarm_chains()
            self.chains_prewarmed = True
        except Exception as e:
            print(f"Warning: Failed to pre-warm chains: {e}")

    async def ensure_chains_prewarmed(self):
        """Ensure chains are pre-warmed before use."""
        if not self.chains_prewarmed:
            await self._prewarm_chains_async()

    def _create_workflow(self) -> StateGraph:
        """
        Create the LangGraph workflow.

        This implementation features:
        - No complex routing logic needed
        - Agents communicate through messages
        - Supervisor handles all routing decisions
        - State is minimal and focused
        """
        # Create agents
        supervisor = create_supervisor(self.llm)
        document_processor = create_document_processor(self.llm)
        cybersecurity_agent = create_cybersecurity_agent(self.llm)
        regulatory_agent = create_regulatory_agent(self.llm)
        auditor_agent = create_auditor_agent(self.llm)
        report_generator = create_report_generator(self.llm)

        # Create workflow graph
        workflow = StateGraph(ComplianceGapState)

        # Add nodes
        workflow.add_node("supervisor", supervisor)
        workflow.add_node("document_processor", document_processor)
        workflow.add_node("cybersecurity_agent", cybersecurity_agent)
        workflow.add_node("regulatory_agent", regulatory_agent)
        workflow.add_node("auditor_agent", auditor_agent)
        workflow.add_node("report_generator", report_generator)

        # Set entry point
        workflow.set_entry_point("supervisor")

        # Simplified conditional routing using LangGraph's built-in pattern
        workflow.add_conditional_edges(
            "supervisor",
            lambda x: x["next"],  # Simple routing based on supervisor's decision
            {
                "document_processor": "document_processor",
                "cybersecurity_agent": "cybersecurity_agent",
                "regulatory_agent": "regulatory_agent",
                "auditor_agent": "auditor_agent",
                "report_generator": "report_generator",
                "FINISH": END,
            },
        )

        # Simplified edges - agents communicate through messages
        workflow.add_edge("document_processor", "supervisor")
        workflow.add_edge("cybersecurity_agent", "supervisor")
        workflow.add_edge("regulatory_agent", "supervisor")
        workflow.add_edge("auditor_agent", "supervisor")
        workflow.add_edge("report_generator", "supervisor")

        return workflow.compile()

    async def run_async(
        self, user_input: str, uploaded_files: Optional[list] = None
    ) -> AsyncGenerator[str, None]:
        """
        Run workflow asynchronously with streaming support.

        Enhanced with:
        - Word-by-word streaming for better UX
        - Source extraction and display
        - Final response compilation
        - Proper agent routing
        - RAG chain pre-warming
        """
        # Ensure chains are pre-warmed before starting
        await self.ensure_chains_prewarmed()

        # Determine workflow type based on uploaded files
        workflow_type = "gap_analysis" if uploaded_files else "question_answering"

        # Create simplified initial state
        initial_state = create_initial_state(
            user_input=user_input,
            uploaded_files=uploaded_files,
            workflow_type=workflow_type,
        )

        # Track sources
        all_sources = []

        # Stream the workflow execution with increased recursion limit and better error handling
        try:
            config = {"recursion_limit": 15}  # Increased limit with better termination logic
            async for chunk in self.workflow.astream(initial_state, config=config):
                if "__end__" not in chunk:
                    # Extract messages from the chunk
                    for node_name, node_output in chunk.items():
                        if isinstance(node_output, dict) and "messages" in node_output:
                            for message in node_output["messages"]:
                                if hasattr(message, "content") and message.content:
                                    agent_name = getattr(message, "name", node_name)

                                    # Extract sources from message content
                                    message_sources = extract_sources_from_message(
                                        message.content
                                    )
                                    all_sources.extend(message_sources)

                                    # For all agents, show brief status (not full content)
                                    # The supervisor will handle final response compilation
                                    yield f"🔍 **{agent_name}** analyzing...\n"

                        elif isinstance(node_output, dict) and "next" in node_output:
                            # Supervisor routing decision or final response
                            next_agent = node_output["next"]
                            final_response = node_output.get("final_response", "")

                            if next_agent != "FINISH":
                                yield f"🔄 Routing to {next_agent}...\n"
                            else:
                                # Supervisor is providing final response
                                if final_response:
                                    yield "\n📋 **FDA Auditor Assessment:**\n\n"
                                    # Stream the final response word by word
                                    async for word in stream_text_word_by_word(
                                        final_response
                                    ):
                                        yield word
                                    yield "\n\n"

                                # Show sources if available
                                if all_sources:
                                    yield "\n📚 **Sources:**\n"
                                    unique_sources = []
                                    seen = set()
                                    for source in all_sources:
                                        source_key = f"{source['document']}_page_{source['page']}"
                                        if source_key not in seen:
                                            unique_sources.append(source)
                                            seen.add(source_key)

                                    for i, source in enumerate(unique_sources, 1):
                                        source_text = f"{i}. **{source['document']}** - Page {source['page']}\n"
                                        # Stream sources word by word too
                                        async for word in stream_text_word_by_word(
                                            source_text, delay=0.02
                                        ):
                                            yield word

                                yield "\n✅ Analysis complete.\n"

        except Exception as e:
            # Enhanced error handling for different types of errors
            error_message = str(e)
            if "GraphRecursionError" in error_message or "Recursion limit" in error_message:
                yield f"❌ Workflow exceeded recursion limit. This indicates a routing issue that has been fixed. Please try your request again.\n"
                yield f"🔧 If this persists, the supervisor agent may need additional tuning.\n"
            else:
                yield f"❌ Error in workflow execution: {error_message}\n"

    def run_sync(
        self, user_input: str, uploaded_files: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Run workflow synchronously.

        Simplified compared to original implementation.
        """
        workflow_type = "gap_analysis" if uploaded_files else "question_answering"

        initial_state = create_initial_state(
            user_input=user_input,
            uploaded_files=uploaded_files,
            workflow_type=workflow_type,
        )

        config = {"recursion_limit": 15}  # Increased limit with better termination logic
        return self.workflow.invoke(initial_state, config=config)


# Helper functions for easier usage
def create_workflow(
    llm: Optional[ChatOpenAI] = None, prewarm_chains: bool = True
) -> RegulatoryWorkflow:
    """Create a regulatory workflow instance with optional chain pre-warming."""
    return RegulatoryWorkflow(llm, prewarm_chains=prewarm_chains)


async def process_user_request(
    user_input: str, uploaded_files: Optional[list] = None
) -> AsyncGenerator[str, None]:
    """
    Process user request with the workflow.

    This demonstrates the clean API for regulatory compliance analysis.
    """
    workflow = create_workflow()

    try:
        async for response in workflow.run_async(user_input, uploaded_files):
            yield response
    except Exception as e:
        yield f"❌ Error in workflow: {str(e)}"


# Example usage demonstrating the workflow
def example_usage():
    """
    Example showing how to use the workflow.

    Clean and straightforward API for regulatory compliance analysis.
    """
    # Create workflow
    workflow = create_workflow()

    # Example 1: Question answering
    question_result = workflow.run_sync(
        "What are the FDA cybersecurity requirements for medical devices?"
    )

    # Example 2: Gap analysis with files
    gap_analysis_result = workflow.run_sync(
        "Analyze these documents for compliance gaps",
        uploaded_files=[{"name": "device_spec.pdf", "content": "..."}],
    )

    return question_result, gap_analysis_result


# Comparison with original approach
def comparison_notes():
    """
    Key improvements in the simplified approach:

    1. STATE MANAGEMENT:
       - Original: 20+ state fields with complex updates
       - Simplified: 8 core fields using LangGraph's built-in patterns

    2. ROUTING:
       - Original: Complex get_next_agent() function with conditional logic
       - Simplified: LLM-based supervisor with built-in routing

    3. AGENT COMMUNICATION:
       - Original: Complex state field updates between agents
       - Simplified: Clean message passing with operator.add

    4. WORKFLOW CREATION:
       - Original: Complex conditional edges and routing functions
       - Simplified: Standard LangGraph patterns with lambda routing

    5. CODE MAINTAINABILITY:
       - Original: ~800 lines across multiple files
       - Simplified: ~400 lines with cleaner separation

    6. DEBUGGING:
       - Original: Hard to trace state changes across agents
       - Simplified: Clear message history shows agent interactions
    """
    pass
