import json
import imghdr
from fastapi import APIRouter, UploadFile, HTTPException
from typing import List, Dict, Any


from app.utils.logger import setup_logger
from app.models.menu_base import MenuInfo
from app.routers.controller.ocr_ctl import OCR_Controller
from app.routers.controller.db_ctl import DBController

router = APIRouter()
logger = setup_logger("Image_Scan")
ocr_controller = OCR_Controller()
db_controller = DBController()

ALLOWED_IMAGE_TYPES = {"jpg", "jpeg", "png"}


def validate_image(file: UploadFile) -> bool:
    """
    업로드된 파일이 허용된 이미지 형식인지 검증합니다.
    """
    # 파일 확장자 검사
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_IMAGE_TYPES:
        return False

    # 파일 내용 검사
    contents = file.file.read(1024)  # 처음 1024바이트만 읽음
    file.file.seek(0)  # 파일 포인터를 다시 처음으로

    image_type = imghdr.what(None, contents)
    return image_type in ALLOWED_IMAGE_TYPES


@router.post("/image-scan")
async def image_scan(user_id: str, file: UploadFile):
    """
    이미지 파일을 업로드받아 처리하는 엔드포인트
    """

    def convert_json_to_menu_info(
        user_id: str, file_name: str, source: str
    ) -> List[MenuInfo]:
        try:
            ret_values: List[MenuInfo] = []

            # OCR 결과 로깅
            logger.info(f"OCR 결과: {source}")

            # 문자열 전처리
            source = source.strip()
            chars_to_remove = [
                "```json",
                "```",
                "\n",
                # " ",
                "\t",
                "\r",
                "\f",
                "\v",
                "\b",
            ]
            for char in chars_to_remove:
                source = source.replace(char, "")

            if not source:
                raise ValueError("OCR 결과가 비어있습니다.")

            # JSON 형식 검증
            if not (source.startswith("[") and source.endswith("]")):
                raise ValueError("OCR 결과가 유효한 JSON 배열 형식이 아닙니다.")

            menu_info_json: List[Dict[str, Any]] = json.loads(source)

            # 변환된 JSON 로깅
            logger.info(f"파싱된 JSON: {menu_info_json}")

            for idx, item in enumerate(menu_info_json):
                if (
                    not isinstance(item, dict)
                    or "menu" not in item
                    or "price" not in item
                ):
                    raise ValueError(
                        f"메뉴 항목 {idx+1}의 형식이 올바르지 않습니다: {item}"
                    )

                menu_info = MenuInfo(
                    user_id=user_id,
                    file_name=file_name,
                    menu_name=item["menu"],
                    cost=item["price"],
                )
                ret_values.append(menu_info)

            return ret_values

        except json.JSONDecodeError as e:
            logger.error(f"JSON 디코딩 오류: {str(e)}, 원본 데이터: {source}")
            raise HTTPException(
                status_code=500, detail=f"JSON 형식이 올바르지 않습니다: {str(e)}"
            )
        except ValueError as e:
            logger.error(f"데이터 검증 오류: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"JSON 변환 중 오류 발생: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"JSON 변환 중 오류가 발생했습니다: {str(e)}"
            )

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

        # 이미지 파일 검증
        if not validate_image(file):
            raise HTTPException(
                status_code=400,
                detail="허용되지 않는 파일 형식입니다. jpg, jpeg, png 파일만 업로드 가능합니다.",
            )

        logger.info(f"이미지 파일 업로드 성공: {file.filename}")

        # 이미지 처리
        image_data = await ocr_controller._encode_image_to_base64(file)
        menu_info = await ocr_controller.extract_menu_info(
            image_data,
            '이 이미지는 메뉴판 사진입니다. 이미지에서 메뉴 이름과 가격을 추출해주세요. 가격은 천원 단위로 변환하여 표시해주세요(예: 8.0 -> 8000). 메뉴 이름과 가격을 다음 형식으로 반환해주세요:\n[\n    {"menu": "메뉴이름", "price": int},\n    ...\n]',
        )

        # JSON 가공
        menu_info_list: List[MenuInfo] = convert_json_to_menu_info(
            user_id=user_id,
            file_name=file.filename,
            source=menu_info,
        )

        for idx, item in enumerate(menu_info_list):
            try:
                await db_controller.insert_menu_info(item)
            except:
                raise HTTPException(
                    status_code=500,
                    detail=f"DB에 저장 중 오류 발생: [{idx+1}] - {item}",
                )

        return {
            "status": "success",
            "data": menu_info_list,
        }

    except Exception as e:
        logger.error(f"이미지 스캔 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"이미지 처리 중 오류가 발생했습니다: {str(e)}"
        )
    finally:
        await file.close()
