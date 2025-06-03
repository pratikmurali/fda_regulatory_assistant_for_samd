from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


def agent_node(state, agent, name):
    """
    Process agent state and return formatted message.

    Args:
        state: The current state containing messages
        agent: The agent executor to invoke
        name: The name to assign to the output message

    Returns:
        Dict with messages key containing a HumanMessage with the agent's output
    """
    result = agent.invoke(state)
    return {"messages": [HumanMessage(content=result["output"], name=name)]}


def create_agent(
    llm: ChatOpenAI,
    tools: list,
    system_prompt: str,
) -> AgentExecutor:
    """Create a function-calling agent and add it to the graph.

    Args:
        llm: The language model to use for the agent
        tools: List of tools available to the agent
        system_prompt: Instructions for the agent

    Returns:
        An AgentExecutor that can be invoked with a state dictionary
    """
    system_prompt += (
        "\nWork autonomously according to your specialty, using the tools available to you."
        " Do not ask for clarification."
        " Your other team members (and other teams) will collaborate with you with their own specialties."
        " You are chosen for a reason! You are one of the following team members: {team_members}."
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_functions_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor


def create_team_supervisor(llm: ChatOpenAI, system_prompt, members) -> str:
    """An LLM-based router.

    Creates a supervisor agent that decides which team member should act next.

    Args:
        llm: The language model to use for routing decisions
        system_prompt: Instructions for the supervisor
        members: List of team member names that can be selected

    Returns:
        A runnable chain that takes messages and returns the next team member to act
    """
    options = ["FINISH"] + members
    function_def = {
        "name": "route",
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {
                "next": {
                    "title": "Next",
                    "anyOf": [
                        {"enum": options},
                    ],
                },
            },
            "required": ["next"],
        },
    }
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next?"
                " Or should we FINISH? Select one of: {options}",
            ),
        ]
    ).partial(options=str(options), team_members=", ".join(members))
    return (
        prompt
        | llm.bind_functions(functions=[function_def], function_call="route")
        | JsonOutputFunctionsParser()
    )
