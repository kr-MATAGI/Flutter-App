from typing import List, Dict, Optional, Any, TypedDict, Annotated
from pydantic import BaseModel, Field
from enum import StrEnum


class GraphNode(StrEnum):
    MAIN_MODEL = "main_model"  # 고객의 상담을 관리하는 노드
    DB_QUERY_NODE = "db_query_node"  # 데이터베이스 조회 노드
    EVAL_NODE = "eval_node"  # 만들어진 답변/도구 평가 노드


### Graph Response
class GraphBaseState(TypedDict):
    question: Annotated[str, "The question to be answered"]
    answer: Annotated[str, "The answer to the question"]
    confidence_score: Annotated[float, "The confidence score of the answer"]
    next_node: Annotated[str, "The next node to be executed"]
    reasoning: Annotated[str, "Reason for node selection (0~1)"]
    history: Annotated[list[str], "The history of the conversation"]


class AgentResponse(BaseModel):
    answer: str = Field(description="The answer to the question")
    next_node: str = Field(description="The next node to be executed")
    confidence_score: float = Field(description="The confidence score of the answer")
    reasoning: str = Field(description="Reason for node selection (0~1)")
