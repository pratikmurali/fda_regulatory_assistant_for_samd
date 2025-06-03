from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from utils.langgraph_utils import agent_node, create_agent, create_team_supervisor


def test_agent_node():
    # Setup mock agent
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {"output": "Test output"}

    # Test function
    state = {"messages": []}
    result = agent_node(state, mock_agent, "test_agent")

    # Verify results
    assert "messages" in result
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], HumanMessage)
    assert result["messages"][0].content == "Test output"
    assert result["messages"][0].name == "test_agent"


@patch("utils.langgraph_utils.create_openai_functions_agent")
@patch("utils.langgraph_utils.AgentExecutor")
def test_create_agent(mock_agent_executor, mock_create_agent):
    # Setup
    mock_llm = MagicMock(spec=ChatOpenAI)
    mock_tools = [MagicMock()]
    mock_agent = MagicMock()
    mock_executor = MagicMock()

    mock_create_agent.return_value = mock_agent
    mock_agent_executor.return_value = mock_executor

    # Test function
    result = create_agent(mock_llm, mock_tools, "Test prompt")

    # Verify results
    assert result == mock_executor
    mock_create_agent.assert_called_once()
    mock_agent_executor.assert_called_once_with(agent=mock_agent, tools=mock_tools)


@patch("utils.langgraph_utils.JsonOutputFunctionsParser")
def test_create_team_supervisor(mock_parser):
    # Setup
    mock_llm = MagicMock(spec=ChatOpenAI)
    mock_llm.bind_functions.return_value = "bound_llm"
    mock_parser.return_value = MagicMock()
    mock_parser.return_value.__ror__.return_value = "final_chain"

    # Test function
    result = create_team_supervisor(mock_llm, "Test prompt", ["member1", "member2"])

    # Verify results
    assert result == "final_chain"
    mock_llm.bind_functions.assert_called_once()
    assert "functions" in mock_llm.bind_functions.call_args.kwargs
    assert mock_llm.bind_functions.call_args.kwargs["function_call"] == "route"
