from typing import Annotated, TypedDict, List
from langgraph.graph.message import add_messages

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
