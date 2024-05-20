from typing import TypedDict, List, Annotated, Dict, Any, Set
import operator
import json
import re
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from metadata import DatasetMetadata
from prompts import template
from tools import get_sample_data
from database import get_column_names


class AgentState(TypedDict):
    """TypedDict representing the state of the agent."""
    table_name: str
    model_name: str
    columns: Set[str]
    columns_per_batch: int = 20
    processed_columns: Set[str]
    next_column_batch: List[str]
    messages: Annotated[List[BaseMessage], operator.add]
    metadata: DatasetMetadata


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
        g.add_node("init", self._init_state)
        g.add_node("prompt", self._prompt)
        g.add_node("model", self._model)
        g.add_node("tool", self._tool)
        g.add_node("parse", self._parse)
        g.add_edge("init", "prompt")
        g.add_edge("prompt", "model")
        g.add_edge("tool", "model")
        g.add_conditional_edges(
            "model",
            self._should_execute_tools,
            {
                "yes": "tool",
                "no": "parse"
            }
        )
        g.add_conditional_edges(
            "parse",
            self._should_continue_generation,
            {
                "yes": "model",
                "no": END
            }
        )
        g.set_entry_point("init")
        wf = g.compile()
        return wf


    def _print_state(self, func, state):
        print(f"__ {func} __")
        print(f"keys in state: {state.keys()}")
        keys = ['columns', 'processed_columns', 'next_column_batch']
        for key in keys:
            print(f"** {key}: {state[key]}")
        print("===")
        
            
    def _init_state(self, state: AgentState) -> Dict[str, Any]:
        """Initialize state."""
        self._print_state("_init_state", state)
        columns = set(get_column_names(state['table_name']))
        processed_columns = set()
        next_column_batch = set()
        return {'columns': columns, 'next_column_batch': next_column_batch, 'processed_columns': processed_columns}


    def _prompt(self, state: AgentState) -> Dict[str, Any]:
        """Generates the prompt."""
        self._print_state("_prompt", state)
        table_name = state['table_name']
        format_instructions = self.parser.get_format_instructions()
        next_column_batch = self._next_column_batch(state)
        input = {"table_name": table_name, "format_instructions": format_instructions, 'next_column_batch': next_column_batch}
        response = self.prompt.invoke(input)
        return {'messages': response.messages, 'next_column_batch': next_column_batch}


    def _model(self, state: AgentState) -> Dict[str, Any]:
        """Invokes the LLM model to generate metadata."""
        self._print_state("_model", state)
        model_name = state['model_name']
        self.model = ChatOpenAI(model_name=model_name, temperature=0).bind_tools(tools=self.tools)
        messages = state['messages']
        response = self.model.invoke(messages)
        return {'messages': [response]}


    def _tool(self, state: AgentState) -> Dict[str, Any]:
        """Executes tool calls."""
        self._print_state("_tool", state)
        message = state['messages'][-1]
        tool_call = message.tool_calls[0]
        id = tool_call['id']
        tool = tool_call['name']
        tool_input = tool_call['args']
        action = ToolInvocation(tool=tool, tool_input=tool_input)
        response = self.tool_executor.invoke(action)
        tool_message = ToolMessage(content=str(response), name=tool, tool_call_id=id)
        return {'messages': [tool_message]}


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

        pattern = r'\s*(.*)\s*'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)
        return None


    def _update_metadata(self, metadata, state: AgentState) -> None:
        """Update object"""
        self._print_state("_update_metadata", state)
        curr_metadata = state.get('metadata')
        if curr_metadata:
            metadata.columns = curr_metadata.columns + metadata.columns


    def _next_column_batch(self, state):
        self._print_state("_next_column_batch", state)
        dataset_columns = set(get_column_names(state['table_name']))
        # print(f"dataset_columns: {dataset_columns}")
        if not state.get('columns'):
            columns = dataset_columns
        else:
            columns = state['columns']
        # print(f"columns: {columns}")
        
        processed_columns = state.get('processed_columns')
        if not processed_columns:
            processed_columns = set()
        # print(f"processed_columns: {processed_columns}")
        
        columns_to_process = columns.difference(processed_columns)
        # print(f"columns_to_process: {columns_to_process}")
        sotrted_columns_to_process = sorted(list(columns_to_process))
        # print(f"sotrted_columns_to_process: {sotrted_columns_to_process}")
        columns_per_batch = state['columns_per_batch']
        next_column_batch = sotrted_columns_to_process[:columns_per_batch]
        # print(f"next_column_batch: {next_column_batch}")
        return next_column_batch
        
        
    def _parse(self, state: AgentState) -> Dict[str, Any]:
        """Parses the generated metadata from the LLM response."""
        self._print_state("_parse", state)
        last_message = state['messages'][-1]
        print(f"message.content:\n{last_message.content}")
        json_text = self._extract_json_content(last_message.content)
        print(f"json_text:\n{json_text}")
        if not json_text:
            raise ValueError("Json text is empty")
        try:
            obj = DatasetMetadata(**json.loads(json_text))
            state['processed_columns'].update([column.name for column in obj.columns])
            next_column_batch = self._next_column_batch(state)
            self._update_metadata(obj, state)
        except Exception as e:
            raise ValueError("unable to extract json content from the response")
        if next_column_batch: 
            message = HumanMessage(f"Process these columns next: {next_column_batch}. Foramt your output as follows:{self.parser.get_format_instructions()}.")
            return {
                'messages': [message], 
                'metadata': obj, 'next_column_batch': next_column_batch
            }
        else:
            return {'metadata': obj, 'next_column_batch': next_column_batch}


    def _should_execute_tools(self, state: AgentState) -> str:
        """Determines whether to continue with tool execution or parse the output"""
        self._print_state("_should_execute_tools", state)
        message = state['messages'][-1]
        if len(message.tool_calls) > 0:
            return "yes"
        return "no"


    def _should_continue_generation(self, state: AgentState) -> str:
        """Determines whether to continue with tool execution or parse the output"""
        self._print_state("_should_continue_generation", state)
        next_column_batch = state.get('next_column_batch')
        if next_column_batch:
            return "yes"
        return "no"


    def generate_metadata(self, table_name: str, model_name: str) -> Dict[str, Any]:
        """Generates metadata for the given table using the specified LLM model."""
        input = {
            "table_name": table_name,
            "model_name": model_name,
            "columns_per_batch": 20
        }
        response = self.wf.invoke(input)
        return response
    