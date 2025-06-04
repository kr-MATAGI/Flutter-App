import os
import base64
from typing import Optional
from fastapi import UploadFile
from langchain_openai import ChatOpenAI

from app.core.config import settings


class OCR_Controller:
    _instance: Optional["OCR_Controller"] = None

    def __new__(cls) -> "OCR_Controller":
        if cls._instance is None:
            cls._instance = super(OCR_Controller, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_name: str = "gpt-4o"):
        if not hasattr(self, "_initialized"):
            self.model_name = model_name
            self.llm = ChatOpenAI(
                model=self.model_name,
                api_key=settings.OPENAI_API_KEY,
            )
            self._initialized = True

    async def _encode_image_to_base64(self, file: UploadFile):
        contents = await file.read()
        base64_encoded = base64.b64encode(contents).decode("utf-8")
        await file.seek(0)  # 파일 포인터를 처음으로 되돌림
        return base64_encoded

    async def extract_menu_info(
        self,
        image_data: str,
        prompt: str,
    ):
        # API 요청 생성
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": '이 이미지는 메뉴판 사진입니다. 이미지에서 메뉴 이름과 가격을 추출해주세요. 가격은 천원 단위로 변환하여 표시해주세요(예: 8.0 -> 8000). 메뉴 이름과 가격을 다음 형식으로 반환해주세요:\n[\n    {"menu": "메뉴이름", "price": int},\n    ...\n]',
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    },
                ],
            }
        ]

        response = await self.llm.ainvoke(messages)
        return response.content
