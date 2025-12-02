# services/retriever.py
"""
Retriever Module - Multi-level retrieval cho Q&A
Hỗ trợ:
- Level-based retrieval (Level 0, 1, 2...)
- Exclude các câu đã dùng
- Deduplicate
"""
from typing import List, Dict, Any, Set, Optional
from vector.elastic_client import es
from config import settings
from services.embedder import get_embedding

INDEX = settings.ES_INDEX_NAME


def index_sentences(sentences: List[str], file_id: str = None) -> int:
    """
    Index danh sách câu vào Elasticsearch, auto gán level.
    Mỗi 5 câu = 1 level (có thể customize).
    
    Returns: max_level được tạo
    """
    actions = []
    max_level = 0
    
    for i, sent in enumerate(sentences):
        level = i // 5  # Mỗi 5 câu = 1 level
        max_level = max(max_level, level)
        emb = get_embedding(sent)

        doc = {
            "text": sent,
            "level": level,
            "embedding": emb,
            "sentence_index": i,  # Thứ tự câu trong file
        }
        
        if file_id:
            doc["file_id"] = file_id

        actions.append({"index": {"_index": INDEX}})
        actions.append(doc)

    if actions:
        es.bulk(body=actions, refresh=True)
    
    return max_level


def get_max_level() -> int:
    """Lấy level cao nhất có trong index"""
    try:
        body = {
            "size": 0,
            "aggs": {
                "max_level": {"max": {"field": "level"}}
            }
        }
        resp = es.search(index=INDEX, body=body)
        max_val = resp["aggregations"]["max_level"]["value"]
        return int(max_val) if max_val else 0
    except Exception:
        return 0


def knn_search(
    query: str, 
    top_k: int = 30,
    target_levels: List[int] = None,
    exclude_texts: Set[str] = None
) -> List[Dict[str, Any]]:
    """
    Tìm các câu gần nhất bằng cosineSimilarity.
    
    Args:
        query: Câu hỏi của user
        top_k: Số kết quả tối đa
        target_levels: Chỉ lấy từ các level này (None = tất cả)
        exclude_texts: Các câu đã dùng, cần loại bỏ
    
    Returns: list [{text, level, score}, ...]
    """
    query_vec = get_embedding(query)
    
    # Build query với filter nếu cần
    must_clauses = []
    must_not_clauses = []
    
    if target_levels is not None:
        must_clauses.append({
            "terms": {"level": target_levels}
        })
    
    if exclude_texts:
        for text in exclude_texts:
            must_not_clauses.append({
                "match_phrase": {"text": text}
            })
    
    # Build bool query
    if must_clauses or must_not_clauses:
        bool_query = {"bool": {}}
        if must_clauses:
            bool_query["bool"]["must"] = must_clauses
        if must_not_clauses:
            bool_query["bool"]["must_not"] = must_not_clauses
        inner_query = bool_query
    else:
        inner_query = {"match_all": {}}

    body = {
        "size": top_k,
        "query": {
            "script_score": {
                "query": inner_query,
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_vec}
                }
            }
        }
    }

    resp = es.search(index=INDEX, body=body)

    results = []
    for hit in resp["hits"]["hits"]:
        src = hit["_source"]
        results.append({
            "text": src["text"],
            "level": src.get("level", 0),
            "score": hit["_score"],
            "sentence_index": src.get("sentence_index", 0)
        })
    return results


def get_sentences_by_level(
    query: str,
    start_level: int = 0,
    end_level: int = None,
    limit: int = 15,
    exclude_texts: Set[str] = None
) -> List[Dict[str, Any]]:
    """
    Lấy câu nguồn từ các level cụ thể.
    Dùng cho "Tell me more" - đi sâu vào level tiếp theo.
    
    Args:
        query: Câu hỏi
        start_level: Level bắt đầu
        end_level: Level kết thúc (None = tất cả từ start_level trở đi)
        limit: Số câu tối đa
        exclude_texts: Các câu đã dùng
    
    Returns: Danh sách câu đã dedupe, group theo level
    """
    max_level = get_max_level()
    
    if end_level is None:
        end_level = max_level
    
    # Tạo list các level cần query
    target_levels = list(range(start_level, end_level + 1))
    
    if not target_levels:
        return []
    
    # Search
    hits = knn_search(
        query=query,
        top_k=limit * 3,  # Lấy nhiều hơn để đủ sau khi dedupe
        target_levels=target_levels,
        exclude_texts=exclude_texts
    )
    
    # Deduplicate
    seen = set()
    unique = []
    for h in hits:
        t = h["text"]
        if t not in seen and (exclude_texts is None or t not in exclude_texts):
            seen.add(t)
            unique.append(h)
        if len(unique) >= limit:
            break
    
    # Sort theo level, rồi score giảm dần
    unique.sort(key=lambda x: (x["level"], -x["score"]))
    
    return unique


def get_top_unique_sentences_grouped(
    query: str, 
    limit: int = 15,
    exclude_texts: Set[str] = None
) -> List[Dict[str, Any]]:
    """
    Lấy câu nguồn cho câu hỏi đầu tiên (Level 0 là chính).
    1. Search theo embedding
    2. Lấy unique text
    3. Cắt còn `limit`
    4. Group theo level, sort theo level rồi score
    """
    return get_sentences_by_level(
        query=query,
        start_level=0,
        end_level=None,  # Lấy từ tất cả level nhưng ưu tiên level thấp
        limit=limit,
        exclude_texts=exclude_texts
    )


def delete_all_documents():
    """Xóa tất cả documents trong index"""
    try:
        es.delete_by_query(
            index=INDEX,
            body={"query": {"match_all": {}}}
        )
        return True
    except Exception:
        return False


def delete_documents_by_file(file_id: str):
    """Xóa documents theo file_id"""
    try:
        es.delete_by_query(
            index=INDEX,
            body={"query": {"term": {"file_id": file_id}}}
        )
        return True
    except Exception:
        return False


def get_document_count() -> int:
    """Đếm số documents trong index"""
    try:
        resp = es.count(index=INDEX)
        return resp["count"]
    except Exception:
        return 0
