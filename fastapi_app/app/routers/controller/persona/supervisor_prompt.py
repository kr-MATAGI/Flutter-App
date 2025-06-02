from typing import Dict
import yaml
from pathlib import Path

PERSONA_TEMPLATE = """당신은 채팅 관리자입니다.

{role_description}

톤과 스타일:
- {tone}
- {style}
- 사용 언어: {language}
- 방언: {dialect}

대화 지침:
1. 항상 정중하고 전문적으로 응답합니다.
2. 사용자의 질문이나 요청을 주의 깊게 듣고 적절한 답변을 제공합니다.
3. 불명확한 부분이 있다면 명확히 하기 위한 질문을 합니다.
4. 대화의 맥락을 유지하며 일관된 태도를 보입니다.
5. 필요한 경우 대화를 적절히 방향 지어 주제에서 벗어나지 않도록 합니다.

사용자의 메시지: {user_message}

위의 지침을 따라 응답해 주세요."""


def load_persona_config() -> Dict:
    """페르소나 설정 파일을 로드합니다."""
    config_path = Path(__file__).parent / "supervisor.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_supervisor_prompt(user_message: str) -> str:
    """채팅 관리자 프롬프트를 생성합니다."""
    config = load_persona_config()

    return PERSONA_TEMPLATE.format(
        role_description=config["description"],
        tone=config["tone"],
        style=config["style"],
        language=config["language"],
        dialect=config["dialect"],
        user_message=user_message,
    )
