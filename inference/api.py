import os
from typing import List, Tuple

from groq import Groq
from dotenv import load_dotenv

load_dotenv("D:\Programming\portfolio_projects\llm_router\.env")


def execute_api(prompt: str, context: List[str]) -> Tuple[str, int, int, float]:
    api_key = os.environ.get("GROQ_API_KEY")
    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    client = Groq(api_key=api_key)

    messages = [{"role": "user", "content": prompt}]
    for ctx in context:
        messages.append({"role": "system", "content": ctx})

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False,
        )
    except Exception as e:
        raise RuntimeError(f"Groq API execution failed: {e}")

    choice = completion.choices[0]
    response_text = choice.message.content or ""

    usage = completion.usage
    input_tokens = usage.prompt_tokens if usage else 0
    output_tokens = usage.completion_tokens if usage else 0

    # Rough cost estimate (acceptable per spec)
    estimated_cost = (input_tokens + output_tokens) * 0.0000005

    return response_text, input_tokens, output_tokens, estimated_cost
