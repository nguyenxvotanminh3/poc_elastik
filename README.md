# AI Vector Search Demo (Elasticsearch)

Demo backend sử dụng FastAPI + OpenAI + Elasticsearch cho vector search.

## Kiến trúc

```
ai-vector-elastic-demo/
│── main.py                 # FastAPI app + endpoints
│── config.py               # Load environment variables
│── requirements.txt        # Dependencies
│── .env                    # Environment variables (cần cấu hình)
│── services/
│     ├── splitter.py       # Tách văn bản thành câu
│     ├── embedder.py       # OpenAI embeddings
│     ├── retriever.py      # Index & search Elasticsearch
│     ├── prompt_builder.py # Build prompt cho LLM
│── vector/
│     ├── elastic_client.py # Elasticsearch client
│── models/
│     ├── request_models.py # Pydantic schemas
│── uploads/                # Thư mục lưu file tạm
```

## Flow

1. **Upload file .txt** → đọc nội dung → tách câu
2. Mỗi câu:
   - Tính embedding (OpenAI)
   - Gán level (mỗi 5 câu = 1 level)
   - Index vào Elasticsearch
3. **User hỏi**:
   - Tạo embedding cho câu hỏi
   - Query Elasticsearch bằng `script_score` (cosineSimilarity)
   - Lấy ~15 câu, group theo level
   - Sinh biến thể câu hỏi, giải nghĩa keyword
   - Build prompt → gửi LLM → trả lời

## Setup

### 1. Tạo virtualenv và cài dependencies

```bash
cd ai-vector-elastic-demo

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Download NLTK punkt (chạy 1 lần)
python -m nltk.downloader punkt
```

### 2. Chạy Elasticsearch bằng Docker (local)

```bash
docker run -d --name es-demo \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.15.0
```

> **Lưu ý**: Demo này tắt security cho nhanh. Khi lên production thì bật lại.

Host local: `http://localhost:9200`

### 3. Cấu hình `.env`

Sửa file `.env` với API key của bạn:

```env
OPENAI_API_KEY=your_openai_api_key_here

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

## Test nhanh

### Swagger UI
Mở trình duyệt: http://localhost:8000/docs

### 1. Upload file

**POST /upload**
- Chọn file `.txt` (tiếng Anh) để upload
- Response: `{"filename": "...", "total_sentences": 25, "message": "..."}`

### 2. Hỏi đáp

**POST /ask**
```json
{
  "query": "Explain the main concept mentioned in the document."
}
```

**Response:**
```json
{
  "answer": "Câu trả lời của AI...",
  "prompt_used": "Full prompt gửi cho LLM...",
  "source_sentences": [
    {"text": "...", "level": 0, "score": 1.85},
    ...
  ]
}
```

## Khi deploy lên server

1. Cài Elasticsearch server (hoặc dùng sẵn có)
2. Chỉnh `.env`:
   - `ES_HOST`, `ES_USERNAME`, `ES_PASSWORD`
   - `OPENAI_API_KEY`
3. Deploy FastAPI (Docker, Railway, Render, v.v.)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /        | Thông tin API |
| POST   | /upload  | Upload file .txt để index |
| POST   | /ask     | Hỏi đáp với AI |

## Tính năng chính

- ✅ Upload file → tách câu → embed → lưu Elasticsearch (dense_vector)
- ✅ Query → vector search → lấy 15 câu → group by level
- ✅ Build prompt với:
  - Original question
  - Question variations
  - Keyword meaning
  - Source sentences (Level 0/1/2…)
- ✅ Gọi LLM, trả kết quả + log prompt + source
