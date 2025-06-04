from typing import Annotated, TypedDict, List
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from enum import StrEnum


class BasicState(TypedDict):
    messages: Annotated[list, add_messages]
    query: Annotated[str, "Query (Question)"]
    response: Annotated[str, "Response"]
    state: Annotated[str, "Current State"]
    next_state: Annotated[str, "Next State"]
    error: Annotated[str, "Error"]


class GraphNode(StrEnum):
    MAIN_MODEL = "main_model"
    DB_QUERY_NODE = "db_query_node"
    EVAL_NODE = "eval_node"  # 만들어진 답변/도구 평가 노드


### Main Model
class MainAgentResponse(BaseModel):
    question: str = Field(description="The question to be answered")
    answer: str = Field(description="The answer to the question")
    next_node: str = Field(description="The next node to be executed")


### DB
class DB_AgentResponse(BaseModel):
    question: str = Field(description="The question to be answered")
    query: str = Field(description="The SQL query to be executed")
