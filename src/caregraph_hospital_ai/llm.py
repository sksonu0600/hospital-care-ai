
from langchain_openai import ChatOpenAI

from caregraph_hospital_ai.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


def get_llm() -> ChatOpenAI:
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to your .env file."
        )

    return ChatOpenAI(
        model=OPENAI_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0,
        timeout=30,
        max_retries=2,
    )
