# services/prompt_builder.py
from typing import List, Dict
from openai import OpenAI
from config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_question_variants(user_query: str) -> str:
    """
    Tạo 3–4 phiên bản câu hỏi khác nhau.
    """
    prompt = (
        "Rewrite the following question in 3-4 different ways, "
        "each on a new line:\n\n"
        f"{user_query}"
    )
    resp = client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content.strip()


def extract_keywords(user_query: str) -> str:
    """
    Extract keywords / meaning mô tả.
    """
    prompt = (
        "Extract the main keywords and briefly explain their meaning "
        "from this question. Answer in 2-3 short sentences:\n\n"
        f"{user_query}"
    )
    resp = client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content.strip()


def build_final_prompt(
    user_query: str,
    question_variants: str,
    keyword_meaning: str,
    source_sentences: List[Dict]
) -> str:
    src_lines = []
    current_level = None
    for s in source_sentences:
        lvl = s["level"]
        if current_level != lvl:
            current_level = lvl
            src_lines.append(f"\n[Level {lvl} sentences]")
        src_lines.append(f"- {s['text']}")

    src_block = "\n".join(src_lines)

    final_prompt = f"""
User original question:
{user_query}

Question variations:
{question_variants}

Keyword meaning:
{keyword_meaning}

Source sentences (grouped by level):
{src_block}

Instructions:
- Use ONLY the information in the source sentences to answer.
- If you cannot find the answer, say you don't have enough information.
- Answer clearly and concisely.
"""
    return final_prompt.strip()


def call_llm(prompt: str) -> str:
    resp = client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content.strip()
