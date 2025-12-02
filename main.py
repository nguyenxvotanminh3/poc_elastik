# main.py
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from vector.elastic_client import init_index
from services.splitter import split_into_sentences
from services.retriever import index_sentences, get_top_unique_sentences_grouped
from services.prompt_builder import (
    generate_question_variants,
    extract_keywords,
    build_final_prompt,
    call_llm,
)
from models.request_models import AskRequest, AskResponse

app = FastAPI(title="AI Vector Search Demo (Elasticsearch)")

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


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload file .txt, đọc nội dung, tách câu và index vào Elasticsearch.
    """
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported in this demo")

    content_bytes = await file.read()
    try:
        text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = content_bytes.decode("latin-1")

    sentences = split_into_sentences(text)
    if not sentences:
        raise HTTPException(status_code=400, detail="No valid sentences found in file")

    index_sentences(sentences)

    return {
        "filename": file.filename,
        "total_sentences": len(sentences),
        "message": "File processed and sentences indexed successfully"
    }


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    """
    Nhận câu hỏi từ user, search vector, build prompt, gọi LLM và trả lời.
    """
    # 1. Lấy câu nguồn từ Elasticsearch
    source_sentences = get_top_unique_sentences_grouped(req.query, limit=15)
    if not source_sentences:
        raise HTTPException(status_code=404, detail="No source sentences found. Please upload a file first.")

    # 2. Tạo biến thể câu hỏi + giải nghĩa keyword
    question_variants = generate_question_variants(req.query)
    keyword_meaning = extract_keywords(req.query)

    # 3. Build final prompt
    prompt = build_final_prompt(
        user_query=req.query,
        question_variants=question_variants,
        keyword_meaning=keyword_meaning,
        source_sentences=source_sentences
    )

    # 4. Gọi LLM
    answer = call_llm(prompt)

    return AskResponse(
        answer=answer,
        prompt_used=prompt,
        source_sentences=source_sentences,
    )


@app.get("/")
async def root():
    return {
        "message": "AI Vector Search Demo with Elasticsearch",
        "docs": "/docs",
        "endpoints": ["/upload", "/ask"]
    }
