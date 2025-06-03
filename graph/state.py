"""
Simplified Graph state definitions for FDA Regulatory Assistant LangGraph workflow.

This module defines simplified state structures using LangGraph's built-in constructs
for better maintainability and cleaner agent communication.
"""

from typing import List, Dict, Any, Optional, Literal, TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.documents import Document
import operator


class ComplianceGapState(TypedDict):
    """
    Simplified state structure for the regulatory compliance gap analysis workflow.

    Uses LangGraph's built-in message passing pattern for cleaner agent communication.
    """

    # Core LangGraph state - messages automatically accumulate with operator.add
    messages: Annotated[List[BaseMessage], operator.add]

    # Team and routing management
    team_members: List[str]
    next: str

    # Workflow context
    workflow_type: Literal["question_answering", "gap_analysis"]
    user_question: Optional[str]
    uploaded_files: List[Dict[str, Any]]

    # Document processing (simplified)
    processed_documents: List[Document]

    # Agent analysis results (for gap analysis workflow)
    cybersecurity_analysis: Optional[Dict[str, Any]]
    regulatory_analysis: Optional[Dict[str, Any]]
    gap_analysis: Optional[Dict[str, Any]]
    document_metadata: Optional[Dict[str, Any]]

    # Final outputs
    final_response: Optional[str]
    response_sources: List[Dict[str, Any]]


class AgentState(TypedDict):
    """
    Individual agent state for specialized analysis.

    Used by individual agents to track their specific analysis
    and findings within the broader workflow.
    """

    agent_name: str
    analysis_type: str
    input_documents: List[Document]
    findings: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    confidence_score: float
    analysis_timestamp: str
    sources_used: List[str]


class DocumentAnalysisState(TypedDict):
    """
    State for document-specific analysis.

    Tracks analysis of individual documents within a submission package.
    """

    document_id: str
    document_name: str
    document_type: str  # "technical", "clinical", "quality", "labeling", etc.
    content: str
    metadata: Dict[str, Any]

    # Analysis results
    compliance_status: Dict[str, str]  # requirement -> status
    identified_gaps: List[Dict[str, Any]]
    strengths: List[str]
    weaknesses: List[str]

    # Regulatory mapping
    applicable_regulations: List[str]
    required_sections: List[str]
    missing_sections: List[str]


class GapAnalysisResult(TypedDict):
    """
    Structure for gap analysis results.

    Comprehensive gap analysis findings from the auditor agent.
    """

    # Overall assessment
    overall_compliance_score: float
    readiness_level: Literal[
        "ready", "needs_minor_updates", "needs_major_updates", "not_ready"
    ]

    # Gap categories
    critical_gaps: List[Dict[str, Any]]
    major_gaps: List[Dict[str, Any]]
    minor_gaps: List[Dict[str, Any]]

    # By regulation type
    regulatory_gaps: List[Dict[str, Any]]
    cybersecurity_gaps: List[Dict[str, Any]]
    quality_gaps: List[Dict[str, Any]]
    clinical_gaps: List[Dict[str, Any]]

    # Recommendations
    immediate_actions: List[Dict[str, Any]]
    short_term_actions: List[Dict[str, Any]]
    long_term_actions: List[Dict[str, Any]]

    # Timeline and effort
    estimated_timeline: str
    estimated_effort: str
    priority_order: List[str]

    # Supporting data
    evidence: List[Dict[str, Any]]
    regulatory_references: List[Dict[str, Any]]

    # Report metadata
    analysis_date: str
    analyst_agents: List[str]
    confidence_level: float


class WorkflowConfig(TypedDict):
    """
    Configuration for the LangGraph workflow.

    Controls agent behavior and workflow routing.
    """

    # Agent configuration
    max_iterations: int
    timeout_seconds: int
    enable_streaming: bool

    # Analysis configuration
    gap_analysis_depth: Literal["basic", "comprehensive", "detailed"]
    include_recommendations: bool
    include_timeline: bool

    # Document processing
    chunk_size: int
    chunk_overlap: int
    max_documents: int

    # Response configuration
    response_format: Literal["conversational", "structured", "report"]
    include_sources: bool
    max_response_length: int


def create_initial_state(
    user_input: str,
    uploaded_files: Optional[List[Dict[str, Any]]] = None,
    workflow_type: Literal["question_answering", "gap_analysis"] = "question_answering",
) -> ComplianceGapState:
    """
    Create simplified initial state for the compliance gap analysis workflow.

    Args:
        user_input: User's question or request
        uploaded_files: List of uploaded file metadata
        workflow_type: Type of workflow to execute

    Returns:
        Initial ComplianceGapState
    """
    # Determine team members based on workflow type
    if workflow_type == "gap_analysis":
        team_members = [
            "cybersecurity_agent",
            "regulatory_agent",
            "auditor_agent",
            "report_generator",
        ]
    else:
        team_members = ["cybersecurity_agent", "regulatory_agent"]

    return ComplianceGapState(
        # Core LangGraph state
        messages=[HumanMessage(content=user_input)],
        team_members=team_members,
        next="supervisor",
        # Workflow context
        workflow_type=workflow_type,
        user_question=user_input,
        uploaded_files=uploaded_files or [],
        # Document processing
        processed_documents=[],
        # Agent analysis results
        cybersecurity_analysis=None,
        regulatory_analysis=None,
        gap_analysis=None,
        document_metadata=None,
        # Final outputs
        final_response=None,
        response_sources=[],
    )


def get_completed_agents_from_messages(messages: List[BaseMessage]) -> List[str]:
    """
    Extract completed agents from message history.

    This replaces the old state-based tracking with message-based tracking
    for the simplified LangGraph approach.

    Args:
        messages: List of messages in the conversation

    Returns:
        List of agent names that have completed their analysis
    """
    completed_agents = []

    for message in messages:
        if hasattr(message, "name") and message.name:
            agent_name = message.name
            if agent_name not in completed_agents and agent_name != "supervisor":
                completed_agents.append(agent_name)

    return completed_agents


def is_workflow_complete(state: ComplianceGapState) -> bool:
    """
    Check if the workflow is complete based on message history.

    This uses the simplified approach where completion is determined
    by the supervisor's final_response rather than complex state tracking.

    Args:
        state: Current workflow state

    Returns:
        True if workflow is complete
    """
    # Check if supervisor has provided a final response
    return state.get("final_response") is not None


def compile_final_response_from_messages(messages: List[BaseMessage], workflow_type: str, termination_reason: str) -> str:
    """
    Compile a comprehensive final response from agent messages.

    This function extracts the actual analysis content from specialist agents
    and presents it as a cohesive FDA auditor assessment.

    Args:
        messages: List of messages from the conversation
        workflow_type: Type of workflow (question_answering or gap_analysis)
        termination_reason: Reason for termination

    Returns:
        Compiled final response as FDA auditor
    """
    # Extract agent responses (excluding human and supervisor messages)
    agent_responses = []
    for message in messages:
        if hasattr(message, "name") and message.name and message.name != "supervisor":
            # Clean up the message content by removing source sections for compilation
            content = message.content
            if "📚 **Sources referenced:**" in content:
                content = content.split("📚 **Sources referenced:**")[0].strip()

            agent_responses.append({
                "agent": message.name,
                "content": content
            })

    if not agent_responses:
        return f"Analysis completed ({termination_reason}). Please let me know if you need any additional information or clarification."

    # Compile the final response based on workflow type
    if workflow_type == "question_answering":
        # For Q&A, present the specialist's analysis as FDA auditor assessment
        specialist_analysis = agent_responses[-1]["content"]  # Get the latest/most relevant analysis
        agent_name = agent_responses[-1]["agent"]

        final_response = f"""**FDA Auditor Assessment:**

Based on my review and specialist analysis, here are the key findings:

{specialist_analysis}

**Regulatory Context:**
This assessment is based on current FDA guidance documents and regulatory requirements. The analysis above provides the technical details you requested from our {agent_name.replace('_', ' ')} specialist.

**Recommendations:**
Please review the specific requirements and guidance documents referenced above. If you need clarification on any specific aspect or have additional questions about compliance requirements, I'm here to help.

Do you need any additional clarifications?"""

    else:  # gap_analysis
        # For gap analysis, compile all agent findings
        final_response = f"""**FDA Auditor Assessment - Compliance Gap Analysis:**

Based on comprehensive analysis by our specialist team, here is the regulatory assessment:

"""

        for response in agent_responses:
            agent_name = response["agent"].replace("_", " ").title()
            final_response += f"**{agent_name} Findings:**\n{response['content']}\n\n"

        final_response += """**Overall Assessment:**
The compliance gap analysis has been completed by our specialist team. Please review the findings above and address any identified gaps before proceeding with your regulatory submission.

Do you need any additional clarifications?"""

    return final_response


def create_supervisor_agent(llm, system_prompt: str, members: List[str]):
    """
    Create a supervisor agent with robust error handling and termination logic.

    Since we have a dedicated document processor agent, tools are no longer needed
    for the supervisor. This implementation focuses on routing and final response compilation.
    """
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import JsonOutputParser
    from pydantic import BaseModel, Field, field_validator
    from typing import Literal

    options = ["FINISH"] + members

    class SupervisorResponse(BaseModel):
        """Schema for supervisor responses with validation."""

        next: Literal[
            "FINISH",
            "document_processor",
            "cybersecurity_agent",
            "regulatory_agent",
            "auditor_agent",
            "report_generator",
        ] = Field(
            description="Next agent to route to, or FINISH if providing final response"
        )
        final_response: str = Field(
            default="",
            description="Final compiled response if next is FINISH, empty otherwise",
        )
        reasoning: str = Field(
            default="", description="Brief explanation of the routing decision"
        )

        @field_validator("next")
        @classmethod
        def validate_next(cls, v):
            valid_options = [
                "FINISH",
                "document_processor",
                "cybersecurity_agent",
                "regulatory_agent",
                "auditor_agent",
                "report_generator",
            ]
            if v not in valid_options:
                raise ValueError(
                    f"Invalid routing option: {v}. Must be one of {valid_options}"
                )
            return v

        @field_validator("final_response")
        @classmethod
        def validate_final_response(cls, v):
            # Simplified validation - we'll handle the cross-field validation in the supervisor_node
            return v

    # Enhanced system prompt with critical routing rules and termination logic
    enhanced_prompt = (
        system_prompt
        + f"""

CRITICAL ROUTING RULES AND TERMINATION LOGIC:

1. ALWAYS analyze message history FIRST to identify completed agents
2. NEVER route to an agent that has already provided a response
3. Follow these EXACT sequences:

   QUESTION ANSWERING WORKFLOW:
   - If no specialist has responded: Route to appropriate specialist (cybersecurity_agent OR regulatory_agent)
   - If specialist has responded: FINISH with final assessment

   GAP ANALYSIS WORKFLOW:
   - If no agents completed: document_processor
   - If document_processor completed but not cybersecurity_agent: cybersecurity_agent
   - If cybersecurity_agent completed but not regulatory_agent: regulatory_agent
   - If regulatory_agent completed but not auditor_agent: auditor_agent
   - If auditor_agent completed but not report_generator: report_generator
   - If report_generator completed: FINISH

4. TERMINATION CONDITIONS (ALWAYS FINISH if ANY of these are true):
   - You have already provided a final_response in previous messages
   - More than 6 agent messages exist in conversation
   - All required agents for the workflow have completed
   - Any error in determining next agent

5. When next=FINISH, ALWAYS provide a comprehensive final_response

Available routing options: {options}

DEBUGGING: Always include your reasoning for the routing decision.
"""
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", enhanced_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "ANALYZE CONVERSATION HISTORY:\n"
                "1. Count agent messages (exclude human/supervisor messages)\n"
                "2. Identify which agents have already responded\n"
                "3. Check workflow type and determine next step\n"
                "4. Apply termination conditions\n\n"
                "{format_instructions}",
            ),
        ]
    )

    parser = JsonOutputParser(pydantic_object=SupervisorResponse)
    formatted_prompt = prompt.partial(
        format_instructions=parser.get_format_instructions()
    )

    def supervisor_node(state):
        """Supervisor node with robust termination logic and error handling."""
        try:
            # First, analyze the current state to determine if we should terminate
            messages = state.get("messages", [])
            workflow_type = state.get("workflow_type", "question_answering")

            # Get completed agents from message history
            completed_agents = get_completed_agents_from_messages(messages)
            agent_message_count = len([m for m in messages if hasattr(m, "name") and m.name and m.name != "supervisor"])

            # Check for termination conditions BEFORE calling LLM
            should_terminate = False
            termination_reason = ""

            # Condition 1: Too many agent messages (safety limit)
            if agent_message_count >= 6:
                should_terminate = True
                termination_reason = "Maximum agent interactions reached"

            # Condition 2: Check if supervisor already provided final response
            elif state.get("final_response"):
                should_terminate = True
                termination_reason = "Final response already provided"

            # Condition 3: Check workflow completion
            elif workflow_type == "question_answering" and len(completed_agents) >= 1:
                should_terminate = True
                termination_reason = "Question answering workflow complete"

            elif workflow_type == "gap_analysis":
                required_agents = ["document_processor", "cybersecurity_agent", "regulatory_agent", "auditor_agent", "report_generator"]
                if all(agent in completed_agents for agent in required_agents):
                    should_terminate = True
                    termination_reason = "Gap analysis workflow complete"

            # If we should terminate, compile final response from agent analyses
            if should_terminate:
                # Extract the latest agent responses to compile final assessment
                final_response = compile_final_response_from_messages(messages, workflow_type, termination_reason)
                return {
                    "next": "FINISH",
                    "final_response": final_response,
                }

            # Otherwise, proceed with LLM routing decision
            chain = (
                formatted_prompt
                | llm.bind(response_format={"type": "json_object"})
                | parser
            )
            parsed_dict = chain.invoke(state)

            # Convert dict to Pydantic object for proper validation
            result = SupervisorResponse(**parsed_dict)

            # Additional validation: prevent routing to already completed agents
            if result.next != "FINISH" and result.next in completed_agents:
                # Force termination if trying to route to completed agent
                final_response = compile_final_response_from_messages(messages, workflow_type, "Attempted duplicate routing prevented")
                return {
                    "next": "FINISH",
                    "final_response": final_response,
                }

            # Validate the result manually since Pydantic cross-field validation can be tricky
            if result.next == "FINISH" and not result.final_response.strip():
                # If supervisor wants to finish but didn't provide response, compile from messages
                final_response = compile_final_response_from_messages(messages, workflow_type, "LLM requested finish without response")
                return {
                    "next": "FINISH",
                    "final_response": final_response,
                }

            # Ensure we return the expected format for the graph
            return {"next": result.next, "final_response": result.final_response}

        except Exception as e:
            # Fallback to prevent infinite loops
            print(f"Supervisor error: {e}")
            # Try to compile response from available messages
            try:
                messages = state.get("messages", [])
                workflow_type = state.get("workflow_type", "question_answering")
                final_response = compile_final_response_from_messages(messages, workflow_type, "Error in supervisor routing")
            except:
                final_response = "Analysis completed. There was an issue with the supervisor routing, but the analysis has been completed by the specialist agents."

            return {
                "next": "FINISH",
                "final_response": final_response,
            }

    return supervisor_node


def agent_node(state: ComplianceGapState, agent, name: str) -> Dict[str, Any]:
    """
    Simplified agent node that communicates through messages.

    This replaces complex state updates with simple message passing.
    Enhanced to extract and include source information from tool responses.
    Also extracts structured analysis data for gap analysis workflow.
    """
    result = agent.invoke(state)

    # Handle different agent types (supervisor with tools vs regular agents)
    if isinstance(result, dict) and "output" in result:
        # Regular agent with AgentExecutor
        agent_output = result["output"]
    elif isinstance(result, dict) and "next" in result:
        # Supervisor agent returning routing decision
        return result
    else:
        # Fallback for other agent types
        agent_output = str(result)

    # Initialize state updates
    state_updates = {"messages": [HumanMessage(content=agent_output, name=name)]}

    # Extract structured analysis data from tool outputs for gap analysis workflow
    if "intermediate_steps" in result and state.get("workflow_type") == "gap_analysis":
        for step in result["intermediate_steps"]:
            if len(step) >= 2:
                tool_action, tool_output = step[0], step[1]
                tool_name = getattr(tool_action, 'tool', None)

                # Store analysis results based on agent and tool
                if isinstance(tool_output, dict):
                    if name == "cybersecurity_agent":
                        state_updates["cybersecurity_analysis"] = tool_output
                    elif name == "regulatory_agent":
                        state_updates["regulatory_analysis"] = tool_output
                    elif name == "auditor_agent" and tool_name == "perform_gap_analysis":
                        state_updates["gap_analysis"] = tool_output
                    elif name == "document_processor":
                        # Extract document metadata
                        if "metadata" in tool_output:
                            state_updates["document_metadata"] = tool_output["metadata"]
                        elif "documents" in tool_output:
                            # Create metadata from processed documents
                            docs = tool_output["documents"]
                            metadata = {
                                "total_documents": len(docs),
                                "document_names": [doc.metadata.get("source", "unknown") for doc in docs],
                                "processing_timestamp": tool_output.get("timestamp", ""),
                            }
                            state_updates["document_metadata"] = metadata

    # Try to extract sources from intermediate steps if available
    sources_info = ""
    if "intermediate_steps" in result:
        for step in result["intermediate_steps"]:
            if len(step) >= 2:
                _, tool_output = step[0], step[1]

                # Check if tool output is already a dictionary with sources
                if isinstance(tool_output, dict) and "sources" in tool_output:
                    sources = tool_output["sources"]
                    if sources:
                        sources_info += "\n\n📚 **Sources referenced:**\n"
                        for j, source in enumerate(sources, 1):
                            doc_name = source.get("document", "Unknown document")
                            page = source.get("page", "Unknown page")
                            sources_info += f"{j}. {doc_name} - Page {page}\n"

                # Check if tool output is a string that contains sources (from RAG chains)
                elif isinstance(tool_output, str):
                    try:
                        # Try to parse as JSON if it looks like a dictionary string
                        import json

                        if tool_output.strip().startswith(
                            "{"
                        ) and tool_output.strip().endswith("}"):
                            parsed_output = json.loads(tool_output)
                            if (
                                isinstance(parsed_output, dict)
                                and "sources" in parsed_output
                            ):
                                sources = parsed_output["sources"]
                                if sources:
                                    sources_info += "\n\n📚 **Sources referenced:**\n"
                                    for j, source in enumerate(sources, 1):
                                        doc_name = source.get(
                                            "document", "Unknown document"
                                        )
                                        page = source.get("page", "Unknown page")
                                        sources_info += (
                                            f"{j}. {doc_name} - Page {page}\n"
                                        )
                    except (json.JSONDecodeError, KeyError):
                        pass

    # Combine agent output with sources
    full_content = agent_output + sources_info
    state_updates["messages"] = [HumanMessage(content=full_content, name=name)]

    return state_updates


def create_agent(llm, tools: list, system_prompt: str):
    """
    Create a function-calling agent with simplified prompting.
    """
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    system_prompt += (
        "\nWork autonomously according to your specialty, using the tools available to you."
        " Do not ask for clarification."
        " Your other team members will collaborate with you with their own specialties."
        " You are chosen for a reason! You are one of the following team members: {team_members}."
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_openai_functions_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, return_intermediate_steps=True)
    return executor
