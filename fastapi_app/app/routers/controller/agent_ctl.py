import os
import io
import networkx as nx
import matplotlib.pyplot as plt
from enum import Enum
from typing import Optional, Dict, Any
from PIL import Image

from app.utils.logger import setup_logger
from app.core.config import settings
from app.routers.controller.persona.supervisor_prompt import get_supervisor_prompt
from app.models.graph_state import GraphNode, GraphBaseState, AgentResponse
from app.prompts.prompt_loader import load_prompt

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.graph import MermaidDrawMethod
from langchain_community.llms import Ollama

from langgraph.graph import START, END, StateGraph

logger = setup_logger("AgentController")


### LLM 종류
class LLMType(Enum):
    CHAT_GPT = "gpt4o"  # GPT-4o
    CLAUDE = "claude3.5"  # Claude 3.5 Sonnet
    GEMINI = "gemini2.0"  # Gemini 2.0 Flash

    # Open Source
    LLAMA = "llama3.1"  # Llama 3.1 8B
    GEMMA = "gemma3"  # Gemma 3 12B


### AI Response Controller (by LangGraph)
class AgentController:
    _instance: Optional["AgentController"] = None

    # AI Model
    GRAPH_NODE_MAPPING = {}
    MODEL_PROMPTS = {}

    _base_model: Ollama = None
    _base_model_name: str = ""

    _paid_model: Any = None
    _paid_model_name: str = ""

    # LangGraph 그래프 초기화
    _graph: StateGraph = None
    _parser: PydanticOutputParser = None

    def __new__(
        cls,
        base_model_name: str = "llama3.1",
        paid_model_name: str = "gpt-4o",
    ) -> "AgentController":
        if not cls._instance:
            logger.info(f"Creating new AgentController instance")
            cls._instance = super(AgentController, cls).__new__(cls)
            cls._instance._base_model_name = base_model_name
            cls._instance._paid_model_name = paid_model_name
            cls._instance._initialized = False

        return cls._instance

    def __init__(
        self, base_model_name: str = "llama3.1", paid_model_name: str = "gpt-4o"
    ):
        # 이미 초기화된 인스턴스는 다시 초기화하지 않음
        if not self._initialized:
            # Base Model (Free)
            try:
                self._base_model_name = base_model_name
                if "llama" in self._base_model_name:
                    self._base_model = Ollama(model=self._base_model_name)
                elif self._base_model_name == "gpt-4o":
                    self._base_model = ChatOpenAI(model=self._base_model_name)
                else:
                    # 예외 처리
                    self._base_model = Ollama(model=self._base_model_name)
            except Exception as e:
                logger.error(f"Error initializing base model: {e}")
                raise e

            logger.info(f"Initialized Base Model: {self._base_model_name}")

            # Paid Model
            try:
                self._paid_model_name = paid_model_name
                if self._paid_model_name == "gpt-4o":
                    self._paid_model = ChatOpenAI(model=self._paid_model_name)
                elif self._paid_model_name == "claude":
                    # @TODO: 클로드 모델 추가
                    pass
                elif self._paid_model_name == "gemini":
                    # @TODO: Gemini 모델 추가
                    pass
                else:
                    # 예외 처리
                    self._paid_model = ChatOpenAI(model=self._paid_model_name)
            except Exception as e:
                logger.error(f"Error initializing paid model: {e}")
                raise e

            logger.info(f"Initialized Paid Model: {self._paid_model_name}")

            self.GRAPH_NODE_MAPPING = {
                GraphNode.MAIN_MODEL: self._main_model_node,
                GraphNode.DB_QUERY_NODE: self._db_search_node,
                GraphNode.EVAL_NODE: self._eval_node,
            }

            self.MODEL_PROMPTS = {
                GraphNode.MAIN_MODEL: load_prompt("main_model"),
                GraphNode.DB_QUERY_NODE: load_prompt("db_query"),
            }

            self._parser = PydanticOutputParser(pydantic_object=AgentResponse)
            self._initialized = True

    def get_model_info(self) -> str:
        return {
            "base_model": self._base_model_name,
            "paid_model": self._paid_model_name,
        }

    def __str__(self) -> str:
        return f"AgentController(base_model={self._base_model_name}, paid_model={self._paid_model_name})"

    async def ainvoke(self, message: str, use_paid_model: bool = False):
        if not use_paid_model:
            return await self._base_model.ainvoke(message)
        else:
            return await self._paid_model.ainvoke(message)

    async def call_agent(self, message: str, use_paid_model: bool = False):
        # 초기 상태 생성
        initial_state = GraphBaseState(
            question=message,
            next_node=GraphNode.MAIN_MODEL.value,
            history=[],
        )

        # 그래프 실행
        result = await self._graph.ainvoke(initial_state)
        return result

    async def show_graph(self):
        logger.info(f"Showing graph for model")

        if not self._graph:
            logger.warning("Graph not initialized")
            return None

        try:
            image = io.BytesIO(
                self._graph.get_graph().draw_mermaid_png(
                    draw_method=MermaidDrawMethod.API
                )
            )

            return image.getvalue()

        except Exception as e:
            logger.error(f"Error generating graph visualization: {e}")
            return None

    async def build_graph(self):
        logger.info(f"Building graph for model")

        if self._graph:
            logger.info(f"Graph already exists")

        # Init
        self._graph = StateGraph(GraphBaseState)

        # Make graph nodes
        await self.make_graph_node()

        # Make graph edges
        await self.make_graph_edges()

        # Compile
        self._graph = self._graph.compile()

    async def make_graph_node(self):
        logger.info(
            f"Making graph nodes for model: {[x.value for x in self.GRAPH_NODE_MAPPING.keys()]}"
        )

        for node, node_func in self.GRAPH_NODE_MAPPING.items():
            self._graph.add_node(node.value, node_func)
            logger.info(f"Added node: {node.value}, {str(node_func.__name__)}")

    async def make_graph_edges(self):
        logger.info(f"Making graph edges for model")

        # START
        self._graph.add_edge(START, GraphNode.MAIN_MODEL.value)

        # 조건부 라우팅 함수 정의
        def route_by_node(state: GraphBaseState) -> GraphBaseState:
            # state의 next_node 값을 바로 반환하거나 END 반환
            return (
                state["next_node"]
                if state["next_node"]
                in (GraphNode.DB_QUERY_NODE.value, GraphNode.EVAL_NODE.value)
                else END
            )

        # 조건부 엣지 추가
        self._graph.add_conditional_edges(
            GraphNode.MAIN_MODEL.value,
            route_by_node,
            {
                GraphNode.DB_QUERY_NODE: GraphNode.DB_QUERY_NODE.value,
                GraphNode.EVAL_NODE: GraphNode.EVAL_NODE.value,
            },
        )

        # DB 쿼리 노드에서 메인 모델로 돌아가는 엣지
        self._graph.add_edge(GraphNode.DB_QUERY_NODE.value, GraphNode.EVAL_NODE.value)

    async def _main_model_node(
        self,
        state: GraphBaseState,
    ) -> GraphBaseState:
        try:
            # 프롬프트 템플릿 생성
            prompt = PromptTemplate(
                template=self.MODEL_PROMPTS[GraphNode.MAIN_MODEL],
                input_variables=[
                    "question",
                ],
                partial_variables={"format": self._parser.get_format_instructions()},
            )

            # 입력 데이터 준비
            input_data = {"question": state["question"]}

            # Chain 실행
            chain = prompt | self._base_model | self._parser
            response: AgentResponse = await chain.ainvoke(input_data)

            # GraphBaseState 타입에 맞게 필드 추가
            return GraphBaseState(
                question=state["question"],
                next_node=response.next_node,
                answer=response.answer,
                confidence_score=response.confidence_score,
                reasoning=response.reasoning,
                history=state["history"]
                + [{"role": "assistant", "content": response.answer}],
            )

        except ConnectionError as e:
            logger.error(f"Connection error to LLM service: {e}")
            return GraphBaseState(
                question=state["question"],
                next_node=END,
                answer="죄송합니다. 현재 AI 서비스에 연결할 수 없습니다.",
                confidence_score=0.0,
                reasoning="연결 오류",
                history=state["history"]
                + [
                    {
                        "role": "system",
                        "content": "LLM 서비스 연결 오류가 발생했습니다.",
                    }
                ],
            )
        except Exception as e:
            logger.error(f"Unexpected error in main model node: {e}")
            return GraphBaseState(
                question=state["question"],
                next_node=END,
                answer="죄송합니다. 처리 중 오류가 발생했습니다.",
                confidence_score=0.0,
                reasoning="처리 오류",
                history=state["history"]
                + [{"role": "system", "content": f"오류 발생: {str(e)}"}],
            )

    async def _db_search_node(
        self,
        state: GraphBaseState,
    ) -> GraphBaseState:
        prompt: PromptTemplate = PromptTemplate.from_template(
            self.MODEL_PROMPTS[GraphNode.DB_QUERY_NODE]
        )

        # 입력 데이터 준비
        input_data = {
            "question": state["question"],
            "history": state["history"],
            "format": self._parser.get_format_instructions(),
        }

        # Chain 실행
        chain = prompt | self._base_model | self._parser
        response: AgentResponse = await chain.ainvoke(input_data)

        return GraphBaseState(
            question=state["question"],
            next_node=response.next_node,
            answer=response.answer,
            confidence_score=0.0,
            reasoning=response.reasoning,
            history=state["history"]
            + [{"role": "assistant", "content": response.answer}],
        )

    async def _eval_node(
        self,
        state: GraphBaseState,
    ) -> GraphBaseState:
        return GraphBaseState(
            question=state["question"],
            next_node=GraphNode.MAIN_MODEL.value,
            answer=state["answer"],
            confidence_score=0.0,
            reasoning="평가 완료",
            history=state["history"] + [{"role": "system", "content": "평가 완료"}],
        )
