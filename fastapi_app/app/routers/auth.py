from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
from app.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    사용자 로그인 및 액세스 토큰 발급
    """
    # TODO: 사용자 인증 및 토큰 발급 구현
    return {"access_token": "dummy_token", "token_type": "bearer"}


@router.post("/register")
async def register(username: str, password: str):
    """
    새로운 사용자 등록
    """
    # TODO: 사용자 등록 구현
    return {"message": "사용자 등록이 완료되었습니다."}
