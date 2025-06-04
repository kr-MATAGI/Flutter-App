import os
from enum import Enum
from typing import Optional, Dict

from app.utils.logger import setup_logger
from app.routers.controller.persona.supervisor_prompt import get_supervisor_prompt

# from langchain_core import PydanticOutputParser, PromptTemplate
from langchain_community.llms import Ollama

from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph

logger = setup_logger("ai_ctl")


### LLM 종류
class LLMType(Enum):
    CHAT_GPT = "gpt4o"  # GPT-4o
    CLAUDE = "claude3.5"  # Claude 3.5 Sonnet
    GEMINI = "gemini2.0"  # Gemini 2.0 Flash

    # Open Source
    LLAMA = "llama3.1"  # Llama 3.1 8B
    GEMMA = "gemma3"  # Gemma 3 12B


### AI Response Controller (by LangGraph)
class LLM_Controller:
    _instance: Optional["LLM_Controller"] = None
    _instances: Dict[str, "LLM_Controller"] = {}
    _initialized: bool = False

    def __new__(cls, model_name: str = "llama") -> "LLM_Controller":
        # 모델별로 다른 인스턴스를 생성
        if model_name not in cls._instances:
            cls._instances[model_name] = super(LLM_Controller, cls).__new__(cls)
        return cls._instances[model_name]

    def __init__(self, model_name: str = "llama"):
        # 이미 초기화된 인스턴스는 다시 초기화하지 않음
        if not hasattr(self, "_initialized") or not self._initialized:
            self.model_name = model_name
            self.model_type = None
            self.llm = None

            if "chatgpt" == model_name:
                self.model_type = LLMType.CHAT_GPT
                self.llm = ChatOpenAI(model=self.model_type.value)
            elif "claude" == model_name:
                self.model_type = LLMType.CLAUDE
            elif "gemini" == model_name:
                self.model_type = LLMType.GEMINI
            elif "gemma" == model_name:
                self.model_type = LLMType.GEMMA
            else:
                # llama
                self.model_type = LLMType.LLAMA
                self.llm = Ollama(model=self.model_type.value)

            logger.info(
                f"Initialized AI Response Controller with model: {self.model_type}"
            )
            self._initialized = True

    async def ainvoke(self, message: str):
        return await self.llm.ainvoke(message)

    def get_model_type(self) -> LLMType:
        """현재 설정된 모델 타입을 반환합니다."""
        return self.model_type

    def __str__(self) -> str:
        return f"AiRespController(model_type={self.model_type}, model_name={self.model_name})"

    @classmethod
    def get_instance(cls, model_name: str = "llama") -> "LLM_Controller":
        """
        지정된 모델의 AiRespController 인스턴스를 반환합니다.
        이미 존재하는 경우 기존 인스턴스를 반환하고, 없는 경우 새로 생성합니다.

        Args:
            model_name (str): 사용할 AI 모델 이름

        Returns:
            AiRespController: 해당 모델의 컨트롤러 인스턴스
        """
        return cls(model_name)

    @classmethod
    def get_all_instances(cls) -> Dict[str, "LLM_Controller"]:
        """
        현재 생성된 모든 AI 컨트롤러 인스턴스를 반환합니다.

        Returns:
            Dict[str, AiRespController]: 모델 이름을 키로 하는 컨트롤러 인스턴스 딕셔너리
        """
        return cls._instances

    @classmethod
    async def get_simple_response(cls, model_name: str, message: str) -> str:
        """
        간단한 AI 응답을 생성합니다.

        Args:
            model_name (str): 사용할 AI 모델 이름
            message (str): 사용자 메시지

        Returns:
            str: AI의 응답 메시지
        """
        target_llm = cls.get_instance(model_name)
        response = await target_llm.ainvoke(message)

        return response

    # @classmethod
    # async def get_menu_info(
    #     cls,
    # ) -> str:
    #     target_llm = cls.get_instance(model_name)
    #     response = await target_llm.ainvoke(message)
    #     return response
