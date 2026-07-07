from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.services.gemini import ask_gemini
from backend.app.services.network_context import build_context

router = APIRouter()


class Question(BaseModel):
    question: str


@router.post("/ai")
def ask(data: Question):

    context = build_context()

    prompt = f"""
    You are an expert Cybersecurity Analyst.

    Analyze the network traffic like a SOC analyst.

    Rules:
    - Use ONLY the network data provided.
    - Mention percentages when useful.
    - Explain whether the traffic appears normal or suspicious.
    - Suggest possible reasons.
    - Give recommendations if necessary.
    - Keep answers under 200 words.

    {context}

    User Question:
    {data.question}
    """

    answer = ask_gemini(prompt)

    return {
        "answer": answer
    }