# models/request_models.py
from pydantic import BaseModel
from typing import Optional


class AskRequest(BaseModel):
    query: str


class ContinueRequest(BaseModel):
    """Request để tiếp tục đào sâu câu trả lời (Tell me more)"""
    session_id: str


class AskResponse(BaseModel):
    """Response đầy đủ theo yêu cầu khách hàng"""
    session_id: str  # ID session để dùng cho Continue
    answer: str
    question_variants: str  # 3-4 biến thể câu hỏi
    keyword_meaning: str  # Giải nghĩa keywords
    source_sentences: list[dict]  # Các câu nguồn theo level
    current_level: int  # Level hiện tại đang dùng
    max_level: int  # Level cao nhất có thể đi sâu
    prompt_used: str  # Full prompt gửi cho LLM
    can_continue: bool  # Có thể bấm "Tell me more" không


class ContinueResponse(BaseModel):
    """Response khi user bấm Tell me more"""
    session_id: str
    answer: str
    question_variants: str  # Câu hỏi biến thể MỚI (không lặp)
    keyword_meaning: str  # Keyword meaning MỚI
    source_sentences: list[dict]  # Câu nguồn từ level sâu hơn
    current_level: int
    max_level: int
    prompt_used: str
    can_continue: bool  # Còn level để đi sâu không


class FileInfo(BaseModel):
    """Thông tin file đã upload"""
    file_id: str
    filename: str
    total_sentences: int
    max_level: int
    created_at: str
