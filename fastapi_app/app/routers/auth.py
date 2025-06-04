from fastapi import APIRouter, Depends, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.auth_base import UserCreate, Token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    사용자 로그인 및 액세스 토큰 발급

    Parameters:
    - form_data: username과 password를 포함한 폼 데이터

    Returns:
    - Token: 액세스 토큰 정보

    Raises:
    - HTTPException(401): 인증 실패
    """
    # TODO: 실제 사용자 인증 로직 구현
    return Token(access_token="dummy_token", token_type="bearer")


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=Token)
async def register(
    user: UserCreate = Body(..., description="등록할 사용자 정보")
) -> Token:
    """
    새로운 사용자 등록

    Parameters:
    - user: 사용자 등록 정보 (이메일, 사용자명, 비밀번호)

    Returns:
    - Token: 등록 후 발급되는 액세스 토큰

    Raises:
    - HTTPException(400): 이미 존재하는 사용자
    """
    # TODO: 사용자 등록 로직 구현
    return Token(access_token="dummy_token", token_type="bearer")
