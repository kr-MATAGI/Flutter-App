import os
import io
from enum import Enum
from typing import Optional, Dict, Any
from PIL import Image

from app.utils.logger import setup_logger
from app.core.config import settings
from app.routers.controller.persona.supervisor_prompt import get_supervisor_prompt
from app.models.graph_state import BasicState, GraphNode
from app.prompts.prompt_loader import load_prompt

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.graph import MermaidDrawMethod
from langchain_community.llms import Ollama

from langgraph.graph import START, END, StateGraph

logger = setup_logger("AgentController")

GRAPH_NODES = [
    GraphNode.MAIN_MODEL,
    GraphNode.DB_QUERY_NODE,
    GraphNode.EVAL_NODE,
]


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
    _base_model: Ollama = None
    _base_model_name: str = ""

    _paid_model: Any = None
    _paid_model_name: str = ""

    # LangGraph 그래프 초기화
    _graph: StateGraph = None

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

            logger.info(
                f"Initialized Base Model: {self._base_model_name} ({self._base_model})"
            )

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

            logger.info(
                f"Initialized Paid Model: {self._paid_model_name} ({self._paid_model})"
            )

            self._initialized = True

    async def ainvoke(self, message: str, use_paid_model: bool = False):
        if not use_paid_model:
            return await self._base_model.ainvoke(message)
        else:
            return await self._paid_model.ainvoke(message)

    def get_model_info(self) -> str:
        return {
            "base_model": self._base_model_name,
            "paid_model": self._paid_model_name,
        }

    def __str__(self) -> str:
        return f"AgentController(base_model={self._base_model_name}, paid_model={self._paid_model_name})"

    async def get_simple_response(
        self, message: str, use_paid_model: bool = False
    ) -> str:
        """
        간단한 AI 응답을 생성합니다.

        Args:
            model_name (str): 사용할 AI 모델 이름
            message (str): 사용자 메시지

        Returns:
            str: AI의 응답 메시지
        """
        if not use_paid_model:
            response = await self._base_model.ainvoke(message)
        else:
            response = await self._paid_model.ainvoke(message)

        return response

    async def show_graph(self):
        logger.info(f"Showing graph for model")

        graph_image = Image.open(
            io.BytesIO(self._graph.draw_mermaid_png(draw_method=MermaidDrawMethod.API))
        )
        return graph_image

    async def build_graph(self):
        logger.info(f"Building graph for model")

        if self._graph:
            logger.info(f"Graph already exists")

        # Init
        self._graph = StateGraph(BasicState)

        # Make graph nodes
        await self.make_graph_node()

        # Make graph edges
        await self.make_graph_edges()

    async def make_graph_node(self):
        logger.info(f"Making graph nodes for model: {GRAPH_NODES}")

        for node in GRAPH_NODES:
            pass

    async def make_graph_edges(self):
        logger.info(f"Making graph edges for model: {GRAPH_NODES}")

        # START
        self._graph.add_edge(START, GraphNode.MAIN_MODEL.value)

        # END
        self._graph.add_edge(GraphNode.MAIN_MODEL.value, END)

        # Compile
        self._graph.compile()

    async def _manage_flow_node(
        self,
        state: BasicState,
    ) -> BasicState:
        pass

    async def _db_search_node(
        self,
        state: BasicState,
    ) -> BasicState:
        prompt: PromptTemplate = PromptTemplate.from_template(load_prompt("db_query"))
        chain = prompt | self._base_model

        # chain_response = await chain.ainvoke(state)

        # @TODO: 데이터베이스 조회 결과 반환
