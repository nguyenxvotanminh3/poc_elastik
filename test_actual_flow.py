"""
Test script to verify EXACT order of results from get_next_batch.
This simulates what Streamlit would get.
"""

import sys
sys.path.insert(0, '/Users/minknguyen/Desktop/Working/POC/ai-vector-elastic-demo')

from services.multi_level_retriever import get_next_batch
from services.keyword_extractor import extract_keywords

def test_actual_flow():
    """Simulate the exact flow from Streamlit."""
    
    query = "where is heaven"
    
    print("=" * 80)
    print(f"Query: '{query}'")
    print("=" * 80)
    
    # Extract keywords
    keywords = extract_keywords(query)
    print(f"\nExtracted keywords: {keywords}")
    print(f"Number of keywords: {len(keywords)}")
    
    # Initial state for single keyword
    initial_state = {
        "current_level": 1,  # Level 1 for single keyword
        "level_offsets": {"0": 0, "1": 0, "2": 0, "3": 0},
        "used_sentence_ids": []
    }
    
    print(f"\nInitial state: {initial_state}")
    
    # Get first batch
    print("\n" + "=" * 80)
    print("FIRST BATCH (Simulating /ask)")
    print("=" * 80)
    
    sentences, updated_state, level_used = get_next_batch(
        session_state=initial_state,
        keywords=keywords,
        batch_size=15
    )
    
    print(f"\nReturned {len(sentences)} sentences")
    print(f"Level used: {level_used}")
    print(f"Updated state: {updated_state}")
    
    # Display results with magic words
    print("\nResults (in order):")
    for i, sent in enumerate(sentences, 1):
        magic = sent.get("magic_word", "NONE")
        sub_level = sent.get("sub_level", "")
        text = sent["text"][:80] + "..." if len(sent["text"]) > 80 else sent["text"]
        print(f"{i:2d}. [Magic: {magic:8s}] {text}")
    
    # Group by magic word to verify order
    print("\n" + "=" * 80)
    print("VERIFICATION: Grouping by magic word")
    print("=" * 80)
    
    from collections import OrderedDict
    magic_groups = OrderedDict()
    for sent in sentences:
        magic = sent.get("magic_word", "NONE")
        if magic not in magic_groups:
            magic_groups[magic] = []
        magic_groups[magic].append(sent)
    
    for magic, sents in magic_groups.items():
        print(f"\nMagic word '{magic}': {len(sents)} sentences")
        for j, s in enumerate(sents[:2], 1):
            text = s["text"][:60] + "..."
            print(f"  {j}. {text}")
    
    # Check if order is correct
    print("\n" + "=" * 80)
    print("ORDER CHECK")
    print("=" * 80)
    
    magic_order = [s.get("magic_word") for s in sentences]
    unique_order = []
    for m in magic_order:
        if m not in unique_order:
            unique_order.append(m)
    
    print(f"Magic words appear in this order: {unique_order}")
    print(f"Expected order: ['is', 'are', 'was', 'were', 'be', ...]")
    
    if unique_order[0] == 'is':
        print("✅ First magic word is 'is' - CORRECT")
    else:
        print(f"❌ First magic word is '{unique_order[0]}' - WRONG!")
    
    # Test "Tell me more"
    print("\n" + "=" * 80)
    print("SECOND BATCH (Simulating Tell Me More)")
    print("=" * 80)
    
    sentences2, updated_state2, level_used2 = get_next_batch(
        session_state=updated_state,
        keywords=keywords,
        batch_size=15
    )
    
    print(f"\nReturned {len(sentences2)} sentences")
    print(f"Level used: {level_used2}")
    
    magic_order2 = [s.get("magic_word") for s in sentences2]
    unique_order2 = []
    for m in magic_order2:
        if m not in unique_order2:
            unique_order2.append(m)
    
    print(f"Magic words in 2nd batch: {unique_order2}")

if __name__ == "__main__":
    test_actual_flow()
