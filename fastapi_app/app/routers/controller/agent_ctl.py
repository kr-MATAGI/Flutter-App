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
from app.models.graph_state import (
    BasicState,
    GraphNode,
    DB_AgentResponse,
    MainAgentResponse,
)
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
        result = await self._graph.abatch([BasicState(message=message)])
        return result[0]

    async def show_graph(self):
        logger.info(f"Showing graph for model")

        # 그래프 생성
        G = nx.DiGraph()

        # 노드 추가
        nodes = [START, END] + [node.value for node in self.GRAPH_NODE_MAPPING.keys()]
        G.add_nodes_from(nodes)

        # 엣지 추가
        G.add_edge(START, GraphNode.MAIN_MODEL.value)
        G.add_edge(GraphNode.MAIN_MODEL.value, END)

        # 그래프 레이아웃 설정
        pos = nx.spring_layout(G)

        # 그래프 그리기
        plt.figure(figsize=(10, 8))
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color="lightblue",
            node_size=2000,
            font_size=10,
            font_weight="bold",
            arrows=True,
            edge_color="gray",
        )

        # 이미지로 저장
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        buf.seek(0)

        return buf.getvalue()

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

        # Compile
        self._graph.compile()

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
        # self._graph.add_edge(GraphNode.DB_QUERY_NODE.value, GraphNode.MAIN_MODEL.value)

        # END
        self._graph.add_edge(GraphNode.MAIN_MODEL.value, END)

    async def _main_model_node(
        self,
        state: BasicState,
    ) -> BasicState:
        prompt: PromptTemplate = PromptTemplate.from_template(
            self.MODEL_PROMPTS[GraphNode.MAIN_MODEL]
        )
        prompt_template = prompt.format(
            question=state.message, format=MainAgentResponse
        )
        chain = (
            prompt
            | self._base_model
            | PydanticOutputParser(pydantic_object=MainAgentResponse)
        )
        agent_response = await chain.ainvoke(prompt_template)
        print(agent_response)

        return agent_response

    async def _db_search_node(
        self,
        state: BasicState,
    ) -> BasicState:
        prompt: PromptTemplate = PromptTemplate.from_template(
            self.MODEL_PROMPTS[GraphNode.DB_QUERY_NODE]
        )
        prompt_template = prompt.format(question=state.message, format=DB_AgentResponse)
        chain = (
            prompt
            | self._base_model
            | PydanticOutputParser(pydantic_object=DB_AgentResponse)
        )
        agent_response = await chain.ainvoke(prompt_template)

        print(agent_response)

        return agent_response

    async def _eval_node(
        self,
        state: BasicState,
    ) -> BasicState:
        pass
