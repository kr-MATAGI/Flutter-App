import os
import yaml
from pathlib import Path


def load_prompt(prompt_name: str) -> str:
    """
    YAML 파일에서 프롬프트를 로드합니다.

    Args:
        prompt_name: 프롬프트 파일 이름 (확장자 제외)

    Returns:
        str: 프롬프트 내용
    """
    prompts_dir = Path(__file__).parent.parent / "prompts"
    prompt_path = prompts_dir / f"{prompt_name}.yaml"

    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_data = yaml.safe_load(f)
        return prompt_data[prompt_name]["content"]
