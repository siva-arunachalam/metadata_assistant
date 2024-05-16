from typing import TypedDict, List, Annotated, Dict, Any
import operator
import json
import re
from langchain_core.messages import BaseMessage, ToolMessage
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from metadata import DatasetMetadata
from prompts import template
from tools import get_sample_data


class AgentState(TypedDict):
    """TypedDict representing the state of the agent."""
    table_name: str
    model_name: str
    messages: Annotated[List[BaseMessage], operator.add]
    metadata: DatasetMetadata
    generation_status: str
    parsing_status: str


class MetadataGenerator:
    """Class responsible for generating metadata using the Language Model (LLM)."""

    def __init__(self):
        """Initializes the MetadataGenerator with the prompt, tools, tool executor, output parser, and workflow graph."""
        self.prompt = template
        self.tools = [get_sample_data]
        self.tool_executor = ToolExecutor(tools=self.tools)
        self.parser = PydanticOutputParser(pydantic_object=DatasetMetadata)
        self.wf = self._build_graph()


    def _build_graph(self) -> StateGraph:
        """Builds the workflow graph for the metadata generation process."""
        g = StateGraph(AgentState)
        g.add_node("prompt", self._prompt)
        g.add_node("model", self._model)
        g.add_node("tool", self._tool)
        g.add_node("parse", self._parse)
        g.add_edge("prompt", "model")
        g.add_edge("tool", "model")
        g.add_edge("parse", END)
        g.add_conditional_edges(
            "model",
            self._should_continue,
            {
                "tool": "tool",
                "parse": "parse"
            }
        )
        g.set_entry_point("prompt")
        wf = g.compile()
        return wf


    def _prompt(self, state: AgentState) -> Dict[str, Any]:
        """Generates the prompt."""
        table_name = state['table_name']
        format_instructions = self.parser.get_format_instructions()
        input = {"table_name": table_name, "format_instructions": format_instructions}
        response = self.prompt.invoke(input)
        return {'messages': response.messages}


    def _model(self, state: AgentState) -> Dict[str, Any]:
        """Invokes the LLM model to generate metadata."""
        model_name = state['model_name']
        self.model = ChatOpenAI(model_name=model_name, temperature=0).bind_tools(tools=self.tools)
        messages = state['messages']
        response = self.model.invoke(messages)
        return {'messages': [response]}


    def _tool(self, state: AgentState) -> Dict[str, Any]:
        """Executes tool calls."""
        message = state['messages'][-1]
        tool_call = message.tool_calls[0]
        id = tool_call['id']
        tool = tool_call['name']
        tool_input = tool_call['args']
        action = ToolInvocation(tool=tool, tool_input=tool_input)
        response = self.tool_executor.invoke(action)
        tool_message = ToolMessage(content=str(response), name=tool, tool_call_id=id)
        return {'messages': [tool_message], 'parsing_status': 'n/a'}


    def _extract_json_content(self, text: str) -> str:
        """Extracts JSON content from the given text."""
        pattern = r'```json\s*(.*?)```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)

        pattern = r'```(.*?)```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)
        return None


    def _parse(self, state: AgentState) -> Dict[str, Any]:
        """Parses the generated metadata from the LLM response."""
        last_message = state['messages'][-1]
        json_text = self._extract_json_content(last_message.content)
        print(f"json_text:\n{json_text}")
        if not json_text:
            raise ValueError("Json text is empty")
        try:
            obj = DatasetMetadata(**json.loads(json_text))
        except Exception as e:
            raise ValueError("unable to extract json content from the response")
        return {'parsing_status': "pass", 'metadata': obj}


    def _should_continue(self, state: AgentState) -> str:
        """Determines whether to continue with tool execution or parse the output"""
        message = state['messages'][-1]
        if len(message.tool_calls) > 0:
            return "tool"
        return "parse"


    def generate_metadata(self, table_name: str, model_name: str) -> Dict[str, Any]:
        """Generates metadata for the given table using the specified LLM model."""
        input = {
            "table_name": table_name,
            "model_name": model_name
        }
        response = self.wf.invoke(input)
        return response
    