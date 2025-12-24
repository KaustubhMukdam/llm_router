import os
import requests
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv("D:\Programming\portfolio_projects\llm_router\.env")


def execute_small(prompt: str, context: List[str]) -> Tuple[str, int, int, float]:
    base_url = os.environ.get("OLLAMA_BASE_URL")
    model_name = os.environ.get("OLLAMA_SMALL_MODEL")

    if not base_url or not model_name:
        raise RuntimeError("OLLAMA_BASE_URL or OLLAMA_SMALL_MODEL not set")

    full_prompt = prompt
    if context:
        full_prompt += "\n\n" + "\n".join(context)

    try:
        resp = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "num_predict": 150
                }
            },
            timeout=240,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        raise RuntimeError(f"Ollama small model execution failed: {e}")

    return (
        data.get("response", ""),
        data.get("prompt_eval_count", 0),
        data.get("eval_count", 0),
        0.0,
    )
