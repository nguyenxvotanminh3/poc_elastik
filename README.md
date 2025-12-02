# AI Vector Search Demo (Elasticsearch)

**Full-featured Q&A system** với multi-level retrieval, structured prompt builder, và "Tell me more" functionality.

## 🎯 Mục tiêu dự án

Demo AI Q&A engine với:
- **Multi-level retrieval** (Level 0, 1, 2...) - đào sâu dần vào tài liệu
- **Structured prompt builder** - prompt có cấu trúc rõ ràng
- **"Tell me more"** - cho phép user đào sâu thêm thông tin
- **Source transparency** - luôn show các câu nguồn AI đang dùng

## 📁 Kiến trúc

```
ai-vector-elastic-demo/
│── main.py                     # FastAPI app + all endpoints
│── config.py                   # Load environment variables
│── requirements.txt            # Dependencies
│── .env                        # Environment variables (cần cấu hình)
│── services/
│     ├── splitter.py           # Tách văn bản thành câu
│     ├── embedder.py           # OpenAI embeddings
│     ├── retriever.py          # Multi-level retrieval từ ES
│     ├── prompt_builder.py     # Build structured prompt
│     ├── session_manager.py    # Quản lý conversation sessions
│── vector/
│     ├── elastic_client.py     # Elasticsearch client
│── models/
│     ├── request_models.py     # Pydantic schemas
│── uploads/                    # Thư mục lưu file tạm
```

## 🔄 Flow hoạt động

### 1. Upload file
```
User upload file.txt 
    → Đọc nội dung 
    → Tách thành câu (sentence-level)
    → Gán level (mỗi 5 câu = 1 level)
    → Tạo embedding (OpenAI)
    → Lưu vào Elasticsearch
```

### 2. Ask question (Lần đầu)
```
User hỏi câu hỏi
    → Tạo embedding cho câu hỏi
    → Vector search trong Elasticsearch
    → Lấy 15 câu, deduplicate, group theo Level
    → Tạo 3-4 biến thể câu hỏi
    → Extract & giải nghĩa keywords
    → Build structured prompt
    → Gọi LLM → Trả lời
    → Trả về session_id để tiếp tục
```

### 3. Tell me more (Continue)
```
User bấm "Tell me more" với session_id
    → Tăng level (đi sâu hơn)
    → Lấy câu nguồn MỚI từ level sâu hơn
    → Exclude các câu đã dùng
    → Tạo biến thể câu hỏi MỚI (không lặp)
    → Update keyword meaning
    → Build prompt mới → Gọi LLM
    → Trả lời mở rộng với thông tin mới
```

## 🛠 Setup

### 1. Tạo virtualenv và cài dependencies

```bash
cd ai-vector-elastic-demo

python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Download NLTK punkt (chạy 1 lần)
python -m nltk.downloader punkt punkt_tab
```

### 2. Chạy Elasticsearch bằng Docker (local)

```bash
docker run -d --name es-demo \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.15.0
```

### 3. Cấu hình `.env`

Tạo file `.env`:

```env
OPENAI_API_KEY=sk-your-api-key-here

ES_HOST=http://localhost:9200
ES_USERNAME=
ES_PASSWORD=
ES_INDEX_NAME=demo_documents

APP_PORT=8000
```

### 4. Chạy FastAPI

```bash
uvicorn main:app --reload --port 8000
```

## 📚 API Endpoints

### File Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload file .txt mới |
| POST | `/replace` | Thay thế toàn bộ data bằng file mới |
| DELETE | `/documents` | Xóa tất cả documents |
| GET | `/documents/count` | Đếm số documents & max level |

### Q&A

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ask` | Hỏi câu hỏi → nhận session_id |
| POST | `/continue` | "Tell me more" - đào sâu level tiếp |

### Info

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Thông tin API |
| GET | `/health` | Health check |

## 📝 API Usage Examples

### 1. Upload file

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@school_rules.txt"
```

Response:
```json
{
  "file_id": "abc-123",
  "filename": "school_rules.txt",
  "total_sentences": 220,
  "max_level": 43,
  "message": "File processed successfully. 220 sentences indexed across 44 levels."
}
```

### 2. Ask question

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the duties of a class teacher?"}'
```

Response:
```json
{
  "session_id": "uuid-here",
  "answer": "The class teacher is responsible for...",
  "question_variants": "1. What responsibilities...\n2. Can you explain...",
  "keyword_meaning": "Class teacher refers to...",
  "source_sentences": [
    {"text": "The class teacher must...", "level": 0, "score": 1.85},
    {"text": "Teachers are expected to...", "level": 1, "score": 1.72}
  ],
  "current_level": 1,
  "max_level": 43,
  "prompt_used": "[Full prompt here...]",
  "can_continue": true
}
```

### 3. Tell me more

```bash
curl -X POST "http://localhost:8000/continue" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uuid-from-ask-response"}'
```

Response:
```json
{
  "session_id": "uuid-here",
  "answer": "Additionally, teachers should...",
  "question_variants": "1. What else...\n2. Are there more details...",
  "keyword_meaning": "Further aspects include...",
  "source_sentences": [
    {"text": "In addition to...", "level": 2, "score": 1.68}
  ],
  "current_level": 2,
  "max_level": 43,
  "prompt_used": "[Full prompt here...]",
  "can_continue": true
}
```

## ✅ Checklist theo yêu cầu khách

### Module 1 - Upload & Quản lý file
- [x] Upload file .txt
- [x] Tách thành câu (sentence-level)
- [x] Gán metadata (level, thứ tự)
- [x] Thay thế file (POST /replace)
- [x] Xóa file (DELETE /documents)

### Module 2 - Embeddings & Elasticsearch
- [x] Convert mỗi câu thành embedding (OpenAI)
- [x] Lưu vào Elasticsearch với dense_vector
- [x] Mapping: text, level, embedding

### Module 3 - Xử lý câu hỏi
- [x] Extract keywords + giải nghĩa
- [x] Tìm câu nguồn theo level (Level 0 → Level N)
- [x] Target 15-18 câu nguồn

### Module 4 - Deduplicate
- [x] Loại bỏ câu trùng lặp
- [x] Giữ unique sentences

### Module 5 - Build Prompt
- [x] User Questions - 3-4 biến thể
- [x] Extracted Keyword Meaning
- [x] 15 Unique Source Sentences (group theo Level)
- [x] Prompt Instructions

### Module 6 - Sinh câu trả lời
- [x] Gọi LLM với structured prompt
- [x] Trả về answer + source_sentences + question_variants + prompt_used

### Module 7 - "Tell me more"
- [x] Đi sâu vào level tiếp theo
- [x] Exclude câu đã dùng
- [x] Tạo biến thể câu hỏi MỚI
- [x] Update keyword meaning
- [x] Build prompt mới → LLM trả lời mở rộng

## 🚀 Deploy

Khi lên server:
1. Cài Elasticsearch server
2. Chỉnh `.env` với credentials thật
3. Deploy FastAPI (Docker, Railway, Render, etc.)

## 📄 License

MIT
