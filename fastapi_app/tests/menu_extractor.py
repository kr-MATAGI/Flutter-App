import cv2
import numpy as np
import easyocr
import os
from PIL import Image

class MenuExtractor:
    def __init__(self):
        self.reader = easyocr.Reader(['ko', 'en'])
        
    def extract_menu_items(self, image_path):
        # 이미지 읽기
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("이미지를 불러올 수 없습니다.")
            
        # 이미지 크기 가져오기
        height, width = image.shape[:2]
        min_area = (width * height) * 0.01  # 전체 이미지 면적의 1%를 최소 크기로 설정
            
        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 이미지 이진화
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 윤곽선 찾기
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 결과 저장할 디렉토리 생성
        output_dir = os.path.join(os.path.dirname(image_path), 'extracted_menus')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 각 메뉴 항목 처리
        valid_contours = []
        for contour in contours:
            # 작은 영역 무시
            if cv2.contourArea(contour) < min_area:
                continue
            valid_contours.append(contour)
            
        # 윤곽선을 y 좌표 기준으로 정렬 (위에서 아래로)
        valid_contours.sort(key=lambda c: cv2.boundingRect(c)[1])
            
        for idx, contour in enumerate(valid_contours):
            # 바운딩 박스 얻기
            x, y, w, h = cv2.boundingRect(contour)
            
            # 메뉴 항목 이미지 추출
            menu_item = image[y:y+h, x:x+w]
            
            # OCR로 텍스트 추출
            result = self.reader.readtext(menu_item)
            text = ' '.join([t[1] for t in result])
            
            # 이미지 저장
            cv2.imwrite(os.path.join(output_dir, f'menu_{idx}.jpg'), menu_item)
            
            # 텍스트 파일 저장
            with open(os.path.join(output_dir, f'menu_{idx}.txt'), 'w', encoding='utf-8') as f:
                f.write(text)
                
        return len(valid_contours)

if __name__ == '__main__':
    extractor = MenuExtractor()
    image_path = '/Users/matagi/Desktop/LLM Projects/Flutter-App/fastapi_app/tests/images/콩불.jpg'
    num_items = extractor.extract_menu_items(image_path)
    print(f'추출된 메뉴 항목 수: {num_items}') 