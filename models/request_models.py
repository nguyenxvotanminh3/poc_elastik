# models/request_models.py
from pydantic import BaseModel


class AskRequest(BaseModel):
    query: str


class AskResponse(BaseModel):
    answer: str
    prompt_used: str
    source_sentences: list[dict]
