from app.utils.logger import setup_logger

import chromadb
import os
import tempfile
from fastapi import APIRouter, status, HTTPException, Form, File, UploadFile
from langchain_ollama import OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

logger = setup_logger("SampleRouter")

router = APIRouter()

ALLOWED_DOC_TYPES = {"pdf", "docx", "doc"}

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
    upload_file: UploadFile = File(...),
):
    """
    PDF 파일을 업로드하여 RAG 시스템에 저장하는 엔드포인트
    """
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
        embeddings = OllamaEmbeddings(model="llama3.1")
        
        # Chroma DB 설정
        persist_dir = os.path.join(os.getcwd(), "rag", "test_chroma_db")
        os.makedirs(persist_dir, exist_ok=True)  # 디렉토리가 없으면 생성
        
        logger.info(f"Chroma DB 저장 경로: {persist_dir}")
        
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_dir
        )

        # 문서 저장
        vectorstore.add_documents(chunks)

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
    k: int = 3
):
    """
    RAG 시스템에서 문서를 검색하는 엔드포인트
    """
    try:
        # 임베딩 모델 초기화
        embeddings = OllamaEmbeddings(model="llama3.1")
        
        # Chroma DB 설정
        persist_dir = os.path.join(os.getcwd(), "rag", "test_chroma_db")
        if not os.path.exists(persist_dir):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chroma DB가 초기화되지 않았습니다. 먼저 문서를 업로드해주세요."
            )
            
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_dir
        )

        # 유사 문서 검색
        docs = vectorstore.similarity_search(query, k=k)
        
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
