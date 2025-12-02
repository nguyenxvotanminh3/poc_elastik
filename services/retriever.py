# services/retriever.py
from typing import List, Dict, Any
from vector.elastic_client import es
from config import settings
from services.embedder import get_embedding

INDEX = settings.ES_INDEX_NAME


def index_sentences(sentences: List[str]):
    """
    Index danh sách câu vào Elasticsearch, auto gán level.
    Ví dụ: mỗi 5 câu = 1 level.
    """
    actions = []
    for i, sent in enumerate(sentences):
        level = i // 5  # tuỳ logic bạn muốn
        emb = get_embedding(sent)

        doc = {
            "text": sent,
            "level": level,
            "embedding": emb
        }

        actions.append({"index": {"_index": INDEX}})
        actions.append(doc)

    if actions:
        # bulk API
        es.bulk(body=actions, refresh=True)


def knn_search(query: str, top_k: int = 30) -> List[Dict[str, Any]]:
    """
    Tìm các câu gần nhất bằng cosineSimilarity.
    Trả về list [{text, level, score}, ...]
    """
    query_vec = get_embedding(query)

    body = {
        "size": top_k,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
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
            "score": hit["_score"]
        })
    return results


def get_top_unique_sentences_grouped(query: str, limit: int = 15):
    """
    1. Search theo embedding
    2. Lấy unique text
    3. Cắt còn `limit`
    4. Group theo level, sort theo level rồi score
    """
    hits = knn_search(query, top_k=50)

    # unique theo text
    seen = set()
    unique = []
    for h in hits:
        t = h["text"]
        if t not in seen:
            seen.add(t)
            unique.append(h)
        if len(unique) >= limit:
            break

    # sort theo level, rồi score giảm dần
    unique.sort(key=lambda x: (x["level"], -x["score"]))
    return unique
