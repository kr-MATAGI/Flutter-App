import os
import base64
from PIL import Image
import numpy as np
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_menu_info(image_path):
    # 환경 변수 로드
    load_dotenv()
    
    # ChatOpenAI 초기화
    chat = ChatOpenAI(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # 이미지를 base64로 인코딩
    base64_image = encode_image_to_base64(image_path)
    
    # API 요청 생성
    messages = [
        {
            "role": "user", 
            "content": [
                {
                    "type": "text",
                    "text": "이 이미지는 메뉴판 사진입니다. 이미지에서 메뉴 이름과 가격을 추출해주세요. 가격은 천원 단위로 변환하여 표시해주세요(예: 8.0 -> 8000). 메뉴 이름과 가격을 다음 형식으로 반환해주세요:\n[\n    {\"menu\": \"메뉴이름\", \"price\": int},\n    ...\n]"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
    
    response = chat.invoke(messages)
    return response.content

if __name__ == "__main__":
    # 테스트 이미지 경로
    test_image = "tests/images/콩불.jpg"
    
    # 메뉴 정보 추출
    menu_info = extract_menu_info(test_image)
    print("추출된 메뉴 정보:")
    print(menu_info)
