# main.py
"""
AI Vector Search Demo (Elasticsearch)
=====================================
Full-featured Q&A system với:
- Multi-level retrieval (Level 0, 1, 2...)
- Structured prompt builder
- "Tell me more" functionality
- File management (upload, replace, delete)
"""
import os
import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from vector.elastic_client import init_index, es
from services.splitter import split_into_sentences
from services.retriever import (
    index_sentences, 
    get_top_unique_sentences_grouped,
    get_sentences_by_level,
    get_max_level,
    delete_all_documents,
    get_document_count
)
from services.prompt_builder import (
    generate_question_variants,
    extract_keywords,
    build_final_prompt,
    call_llm,
)
from services.session_manager import session_manager
from models.request_models import (
    AskRequest, 
    AskResponse, 
    ContinueRequest, 
    ContinueResponse,
    FileInfo
)

app = FastAPI(
    title="AI Vector Search Demo (Elasticsearch)",
    description="""
    ## Hệ thống Q&A với Multi-level Retrieval
    
    ### Features:
    - **Upload file** → tách câu → embedding → lưu Elasticsearch
    - **Ask question** → vector search → structured prompt → LLM answer
    - **Tell me more** → đi sâu vào các level tiếp theo
    - **File management** → upload, replace, delete files
    
    ### Flow:
    1. POST /upload - Upload file .txt
    2. POST /ask - Hỏi câu hỏi → nhận session_id
    3. POST /continue - Dùng session_id để đào sâu thêm
    """,
    version="1.0.0"
)

# CORS cho dễ test từ frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Khởi tạo index khi app start
@app.on_event("startup")
def startup_event():
    init_index()


# ============================================================
# MODULE 1: File Management
# ============================================================

@app.post("/upload", tags=["File Management"])
async def upload_file(file: UploadFile = File(...)):
    """
    Upload file .txt, đọc nội dung, tách câu và index vào Elasticsearch.
    
    - Đọc file
    - Tách thành câu (sentence-level)
    - Gán level (mỗi 5 câu = 1 level)
    - Tạo embedding và lưu vào Elasticsearch
    """
    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=400, 
            detail="Only .txt files are supported in this demo"
        )

    content_bytes = await file.read()
    try:
        text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = content_bytes.decode("latin-1")

    sentences = split_into_sentences(text)
    if not sentences:
        raise HTTPException(
            status_code=400, 
            detail="No valid sentences found in file"
        )

    # Index sentences và lấy max_level
    file_id = str(uuid.uuid4())
    max_level = index_sentences(sentences, file_id=file_id)

    return {
        "file_id": file_id,
        "filename": file.filename,
        "total_sentences": len(sentences),
        "max_level": max_level,
        "message": f"File processed successfully. {len(sentences)} sentences indexed across {max_level + 1} levels."
    }


@app.post("/replace", tags=["File Management"])
async def replace_file(file: UploadFile = File(...)):
    """
    Thay thế toàn bộ dữ liệu bằng file mới.
    
    - Xóa tất cả documents cũ
    - Upload và index file mới
    """
    # Xóa dữ liệu cũ
    delete_all_documents()
    
    # Upload file mới
    return await upload_file(file)


@app.delete("/documents", tags=["File Management"])
async def delete_all():
    """
    Xóa tất cả documents trong Elasticsearch.
    """
    success = delete_all_documents()
    if success:
        return {"message": "All documents deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete documents")


@app.get("/documents/count", tags=["File Management"])
async def get_count():
    """
    Lấy số lượng documents hiện có.
    """
    count = get_document_count()
    max_level = get_max_level()
    return {
        "total_documents": count,
        "max_level": max_level,
        "ready": count > 0
    }


# ============================================================
# MODULE 2-6: Ask Question (First Query)
# ============================================================

@app.post("/ask", response_model=AskResponse, tags=["Q&A"])
async def ask(req: AskRequest):
    """
    Nhận câu hỏi từ user, thực hiện full flow:
    
    1. **Vector Search** - Tìm 15-18 câu nguồn liên quan
    2. **Deduplicate** - Loại bỏ câu trùng lặp
    3. **Generate Variants** - Tạo 3-4 biến thể câu hỏi
    4. **Extract Keywords** - Giải nghĩa keywords
    5. **Build Prompt** - Xây dựng prompt có cấu trúc
    6. **Call LLM** - Sinh câu trả lời
    
    Returns session_id để dùng cho /continue (Tell me more)
    """
    # Kiểm tra có data không
    if get_document_count() == 0:
        raise HTTPException(
            status_code=404, 
            detail="No documents found. Please upload a file first."
        )
    
    # 1. Lấy câu nguồn từ Elasticsearch (bắt đầu từ Level 0)
    source_sentences = get_top_unique_sentences_grouped(req.query, limit=15)
    if not source_sentences:
        raise HTTPException(
            status_code=404, 
            detail="No source sentences found matching your query."
        )

    # 2. Tạo biến thể câu hỏi + giải nghĩa keyword
    question_variants = generate_question_variants(req.query)
    keyword_meaning = extract_keywords(req.query)

    # 3. Build final prompt
    prompt = build_final_prompt(
        user_query=req.query,
        question_variants=question_variants,
        keyword_meaning=keyword_meaning,
        source_sentences=source_sentences,
        continue_mode=False
    )

    # 4. Gọi LLM
    answer = call_llm(prompt)
    
    # 5. Tạo session để track conversation
    max_level = get_max_level()
    session = session_manager.create_session(req.query, max_level)
    
    # Cập nhật session với các câu đã dùng
    used_texts = [s["text"] for s in source_sentences]
    session_manager.update_session(
        session.session_id,
        used_sentences=used_texts,
        question_variants=question_variants,
        keywords=keyword_meaning
    )
    
    # Tính current_level từ source sentences
    current_level = max(s["level"] for s in source_sentences) if source_sentences else 0

    return AskResponse(
        session_id=session.session_id,
        answer=answer,
        question_variants=question_variants,
        keyword_meaning=keyword_meaning,
        source_sentences=source_sentences,
        current_level=current_level,
        max_level=max_level,
        prompt_used=prompt,
        can_continue=current_level < max_level
    )


# ============================================================
# MODULE 7: Continue / Tell me more
# ============================================================

@app.post("/continue", response_model=ContinueResponse, tags=["Q&A"])
async def continue_conversation(req: ContinueRequest):
    """
    "Tell me more" - Đào sâu vào các level tiếp theo.
    
    Khi user bấm Continue:
    1. Lấy session từ session_id
    2. Tăng level lên (Level 1, 2, 3...)
    3. Lấy các câu nguồn MỚI từ level sâu hơn (exclude câu đã dùng)
    4. Tạo biến thể câu hỏi MỚI (không lặp)
    5. Update keyword meaning
    6. Build prompt mới → gọi LLM
    
    Returns câu trả lời mở rộng với thông tin mới từ level sâu hơn.
    """
    # Lấy session
    session = session_manager.get_session(req.session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Please ask a new question."
        )
    
    # Kiểm tra có thể continue không
    if session.current_level >= session.max_level_available:
        raise HTTPException(
            status_code=400,
            detail="No more levels available. All information has been explored."
        )
    
    # Tăng level
    next_level = session.current_level + 1
    
    # Lấy câu nguồn từ level mới (exclude các câu đã dùng)
    source_sentences = get_sentences_by_level(
        query=session.original_query,
        start_level=next_level,
        limit=15,
        exclude_texts=session.used_sentences
    )
    
    if not source_sentences:
        raise HTTPException(
            status_code=404,
            detail=f"No new sentences found at Level {next_level}."
        )
    
    # Tạo biến thể câu hỏi MỚI (không lặp với các lần trước)
    question_variants = generate_question_variants(
        session.original_query,
        previous_variants=session.used_variants,
        continue_mode=True
    )
    
    # Update keyword meaning (tìm keywords mới/sâu hơn)
    keyword_meaning = extract_keywords(
        session.original_query,
        previous_keywords=session.previous_keywords,
        continue_mode=True
    )
    
    # Build prompt mới
    prompt = build_final_prompt(
        user_query=session.original_query,
        question_variants=question_variants,
        keyword_meaning=keyword_meaning,
        source_sentences=source_sentences,
        continue_mode=True,
        continue_count=session.continue_count + 1
    )
    
    # Gọi LLM
    answer = call_llm(prompt)
    
    # Cập nhật session
    used_texts = [s["text"] for s in source_sentences]
    session_manager.update_session(
        session.session_id,
        used_sentences=used_texts,
        question_variants=question_variants,
        keywords=keyword_meaning,
        increment_level=True
    )
    
    # Tính current_level
    current_level = max(s["level"] for s in source_sentences) if source_sentences else next_level
    
    return ContinueResponse(
        session_id=session.session_id,
        answer=answer,
        question_variants=question_variants,
        keyword_meaning=keyword_meaning,
        source_sentences=source_sentences,
        current_level=current_level,
        max_level=session.max_level_available,
        prompt_used=prompt,
        can_continue=current_level < session.max_level_available
    )


# ============================================================
# Health & Info Endpoints
# ============================================================

@app.get("/", tags=["Info"])
async def root():
    """Thông tin API"""
    return {
        "message": "AI Vector Search Demo with Elasticsearch",
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "Multi-level retrieval (Level 0, 1, 2...)",
            "Structured prompt builder",
            "Tell me more functionality",
            "File management"
        ],
        "endpoints": {
            "file_management": ["/upload", "/replace", "/documents", "/documents/count"],
            "qa": ["/ask", "/continue"]
        }
    }


@app.get("/health", tags=["Info"])
async def health():
    """Health check endpoint"""
    try:
        # Check Elasticsearch
        es_health = es.cluster.health()
        es_status = es_health["status"]
    except Exception as e:
        es_status = f"error: {str(e)}"
    
    doc_count = get_document_count()
    
    return {
        "status": "healthy",
        "elasticsearch": es_status,
        "documents_indexed": doc_count,
        "ready": doc_count > 0
    }
