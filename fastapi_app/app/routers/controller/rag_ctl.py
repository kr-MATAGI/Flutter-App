import os
from typing import Optional

from app.utils.logger import setup_logger

import chromadb
from llama_index import (
    VectorStoreIndex,  # 임베딩된 문서를 벡터 DB로 연결하고, 검색할 수 있게 만드는 클래스
    ServiceContext,  # LLM, 임베딩 모델, 프롬프트 전략 등 공통 설정을 관리
    Document,  # 텍스트 한 조각(문단/문서)을 표현
    StorageContext,  # 인덱스를 저장하거나 불러올 때 사용하는 저장소
    load_index_from_storage,  # 이전에 저장된 인덱스를 다시 불러옴
)
from llama_index.vector_stores import ChromaVectorStore

logger = setup_logger("RAGController")


class RAGController:
    _instance: Optional["RAGController"] = None

    def __new__(
        cls,
        persist_dir="/app/rag/chroma_db",
        base_collection_name="doc_collection",
    ):
        if cls._instance is None:
            cls._instance = super(RAGController, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        persist_dir="/app/rag/chroma_db",
        base_collection_name="doc_collection",
    ):
        if not self._initialized:
            try:
                self.persist_dir = persist_dir

                # 추후 다른 프레임워크로 변경 필요 (로컬 DB라 제한적)
                self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)

                # Collection: 동일한 목적을 가진 벡터 문서의 묶음
                self.collection_name = base_collection_name
                self.collection = self.chroma_client.get_or_create_collection(
                    name=self.collection_name
                )

                self._initialized = True
            except Exception as e:
                logger.error(f"Error initializing RAGController: {e}")
                raise e

            logger.info(f"RAGController initialized")

    def create_or_load_index(self):
        """
        저장된 인덱스를 불러오거나 새로 생성
        """

        vector_store = ChromaVectorStore(chroma_collection=self.collection)
        store_context = StorageContext.from_defaults(vector_store=vector_store)

        if os.path.exists(self.persist_dir):
            # 기존 인덱스 정보 불러오기
            index = load_index_from_storage(
                storage_context=store_context,
                service_context=self.service_context,
            )
        else:
            index = VectorStoreIndex(
                [],  # 인덱싱할 문서 리스트
                storage_context=store_context,  # 인덱스 저장할 경로
                service_context=self.service_context,  # 정책 설정
            )

        return index

    def get_rag_response(self, query: str, top_k: int = 3):
        """
        문서 검색 결과를 반환
        """
        index = self.create_or_load_index()
        query_engine = index.as_query_engine()

        response = query_engine.query(query)

        logger.info(f"RAG query: {query}, response: {response}")

        return response
