from fastapi import APIRouter, UploadFile, HTTPException, File
from typing import List, Dict, Any

from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger("Doc_Scan")

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


@router.post("/doc-scan")
async def doc_scan(
    file: UploadFile = File(...),
):
    """
    파일 업로드 후 RAG -> Vector DB 저장
    """

    try:
        if not file:
            raise HTTPException(status_code=400, detail="파일이 업로드되지 않았습니다.")

        # 파일 크기 제한 (예: 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
        file_size = 0
        contents = await file.read()
        file_size = len(contents)
        await file.seek(0)  # 파일 포인터를 다시 처음으로

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, detail="파일 크기가 10MB를 초과합니다."
            )

        # 문서 파일 검증
        if not validate_doc(file):
            raise HTTPException(
                status_code=400,
                detail="허용되지 않는 문서 파일 형식입니다. pdf, docx, doc 파일만 업로드 가능합니다.",
            )

        logger.info(f"문서 파일 업로드 성공: {file.filename}")

    except Exception as e:
        logger.error(f"문서 스캔 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"문서 처리 중 오류가 발생했습니다: {str(e)}"
        )
    finally:
        await file.close()
