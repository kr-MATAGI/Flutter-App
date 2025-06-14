import chromadb
import os
import tempfile
import faiss
import numpy as np
from  enum import Enum
from typing import Any
from fastapi import APIRouter, status, HTTPException, Form, File, UploadFile


from langchain_ollama import OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS
from langchain_qdrant import Qdrant
from langchain_core.documents import Document

from qdrant_client import QdrantClient # 벡터 검색 엔진과 통신
from qdrant_client.http.models import models # Qdrant HTTP API의 요청, 응답 스키마

from app.utils.logger import setup_logger

logger = setup_logger("SampleRouter")

router = APIRouter()

ALLOWED_DOC_TYPES = {"pdf"}

class VectorDBType(Enum):
    FAISS = "faiss"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"
    CHROMA = "chroma"

class OllamaModelType(Enum):
    LLAMA3_1 = "llama3.1"
    GEMMA3 = "gemma3:12b"

class PdfReaderType(Enum):
    PyPDF = "pypdf"
    PyMuPDF = "pymupdf"
    UnstructuredPDFLoader = "unstructured_pdf_loader"

def validate_doc(file: UploadFile) -> bool:
    """
    업로드된 파일이 허용된 문서 형식인지 검증합니다.
    """
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_DOC_TYPES:
        logger.warning(f"허용되지 않는 문서 파일 형식: {file.filename}")
        return False

    return file_ext in ALLOWED_DOC_TYPES

@router.post("/rag-test-insert")
async def rag_sample(
    collection_name: str = Form(...),
    vector_db_type: VectorDBType = Form(...),
    pdf_reader_type: PdfReaderType = Form(...),
    upload_file: UploadFile = File(...),
):
    """
    PDF 파일을 업로드하여 RAG 시스템에 저장하는 엔드포인트
    """

    def insert_chroma_db(
        collection_name: str,
        embeddings: OllamaEmbeddings,
        persist_dir: str,
    ):
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_dir
        )

        # 문서 저장
        vectorstore.add_documents(chunks)

    def insert_faiss_db(
        collection_name: str,
        chunks: Any,
        embeddings: OllamaEmbeddings,
        persist_dir: str,
    ):
        # FAISS 인덱스 생성
        vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=embeddings,
        )

        # FASISS 인덱스 저장
        save_path = os.path.join(persist_dir, f"{collection_name}.faiss")
        vector_store = vectorstore.save_local(save_path)

    def insert_qdrant_db(
        collection_name: str,
        chunks: Any,
        embeddings: OllamaEmbeddings,
        persist_dir: str,
        host: str = "localhost",
        port: int = 6333,
    ):
        # Qdrant 클라이언트 초기화 (Docker 환경)
        client = QdrantClient(
            host=host,
            port=port
        )

        # collection 존재 여부 확인
        collections = client.get_collections().collections
        collection_names = [collection.name for collection in collections]

        # collection 생성
        if collection_name not in collection_names:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=4096, # 임베딩 차원
                    distance=models.Distance.COSINE,
                )
            )
            logger.info(f"Qdrant 컬렉션이 생성되었습니다: {collection_name}")

        # Qdrant 벡터 스토어 생성
        vectorstore = Qdrant(
            client=client,
            collection_name=collection_name,
            embeddings=embeddings,
        )

        # 문서 저장
        vectorstore.add_documents(chunks)
    

    temp_file_path = None
    try:
        logger.info("-" * 20)
        logger.info("RAG 테스트 시작")

        # 파일 검증
        if not validate_doc(upload_file):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="허용되지 않는 파일 형식입니다."
            )

        # 임시 파일로 저장
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, upload_file.filename)
        with open(temp_file_path, "wb") as buffer:
            content = await upload_file.read()
            buffer.write(content)

        # PDF 로더 초기화
        loader = PyPDFLoader(temp_file_path)
        pages = loader.load()
        
        # 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_documents(pages)

        # 임베딩 모델 초기화
        embed_model = OllamaEmbeddings(model="llama3.1")
        
        # Vector DB 설정
        persist_dir = os.path.join(os.getcwd(), "rag", f"test_{vector_db_type.value}")
        os.makedirs(persist_dir, exist_ok=True)  # 디렉토리가 없으면 생성
        
        logger.info(f"Vector DB 저장 경로: {persist_dir}")
        
        # Vector Store 정의
        if VectorDBType.CHROMA == vector_db_type:
            insert_chroma_db(collection_name, embed_model, persist_dir)
        elif VectorDBType.FAISS == vector_db_type:
            insert_faiss_db(collection_name, chunks, embed_model, persist_dir)
        elif VectorDBType.QDRANT == vector_db_type:
            insert_qdrant_db(collection_name, chunks, embed_model, persist_dir)
        elif VectorDBType.WEAVIATE == vector_db_type:
            pass
        else:
            logger.error(f"지원하지 않는 Vector DB 타입: {vector_db_type}")
        
        logger.info(f"문서가 성공적으로 저장되었습니다. 청크 수: {len(chunks)}")
        logger.info("-" * 20)

        return {
            "status": "success",
            "message": "문서가 성공적으로 저장되었습니다.",
            "chunks_count": len(chunks)
        }

    except Exception as e:
        logger.error(f"RAG 처리 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    finally:
        # 임시 파일 삭제
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.get("/rag-test-query")
async def rag_query(
    collection_name: str,
    query: str,
    vector_db_type: VectorDBType,
    k: int = 3
):
    """
    RAG 시스템에서 문서를 검색하는 엔드포인트
    """
    def query_chroma_db(
        persist_dr: str,
        collection_name: str,
        query: str,
        k: int
    ):
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_dir
        )

        # 유사 문서 검색
        docs = vectorstore.similarity_search(query, k=k)
        return docs


    def query_faiss_db(
        persist_dir: str,
        collection_name: str,
        query: str,
        k: int
    ):
        vectorstore = FAISS.load_local(
            os.path.join(os.getcwd(), "rag", persist_dir, f"{collection_name}.faiss"),
            embeddings,
            allow_dangerous_deserialization=True  # 신뢰할 수 있는 로컬 파일이므로 True로 설정
        )
        docs = vectorstore.similarity_search(query, k=k)
        return docs

    def query_qdrant_db(
        persist_dir: str,
        collection_name: str,
        query: str,
        k: int,
        host: str = "localhost",
        port: int = 6333,
    ):
        client = QdrantClient(
            host=host,
            port=port
        )

        # collection 존재 여부 확인
        collections = client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        if collection_name not in collection_names:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Qdrant 컬렉션이 존재하지 않습니다: {collection_name}"
            )

        vectorstore = Qdrant(
            client=client,
            collection_name=collection_name,
            embeddings=embeddings,
        )

        docs = vectorstore.similarity_search(query, k=k)
        return docs

    try:
        # 임베딩 모델 초기화
        embeddings = OllamaEmbeddings(model="llama3.1")
        
        # Vector DB 설정
        persist_dir = os.path.join(os.getcwd(), "rag", f"test_{vector_db_type.value}")
        if not os.path.exists(persist_dir):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vector DB가 초기화되지 않았습니다. 먼저 문서를 업로드해주세요."
            )
            
        docs = None
        query_functions = {
            VectorDBType.CHROMA: query_chroma_db,
            VectorDBType.FAISS: query_faiss_db,
            VectorDBType.QDRANT: query_qdrant_db,
        }
        
        if vector_db_type in query_functions:
            docs = query_functions[vector_db_type](persist_dir, collection_name, query, k)
        
        # 결과 포맷팅
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })

        return {
            "status": "success",
            "results": results
        }

    except Exception as e:
        logger.error(f"RAG 검색 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
