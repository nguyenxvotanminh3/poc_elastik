
import sys
import os

# Add project root to path
sys.path.insert(0, '/Users/minknguyen/Desktop/Working/POC/poc_elastik_new')

from services.prompt_builder import build_final_prompt

def test_prompt_building():
    # Mock data
    user_query = "The faith of the Canaanite woman"
    question_variants = "Variant 1\nVariant 2"
    keyword_meaning = "Meaning of faith..."
    source_sentences = [
        {"text": "Sentence 1...", "is_primary_source": True},
        {"text": "Sentence 2...", "is_primary_source": False},
    ]
    
    # Default prompt from streamlit_app.py (simplified for test)
    default_prompt = """You are a sermon-writing assistant.
    
GREETING RULE
If {name_type} is not provided, use neutral versions:
"Hello! Let's explore this together."

INPUT FORMAT
{
"name_type": "... or null",
"question": "...",
"meaning": "..."
}
"""

    print("="*60)
    print("TESTING PROMPT GENERATION (Tell Me More / Continue)")
    print("="*60)
    
    prompt = build_final_prompt(
        user_query=user_query,
        question_variants=question_variants,
        keyword_meaning=keyword_meaning,
        source_sentences=source_sentences,
        continue_mode=True,
        continue_count=1,
        custom_prompt=default_prompt
    )
    
    print(prompt)
    print("="*60)

if __name__ == "__main__":
    test_prompt_building()
