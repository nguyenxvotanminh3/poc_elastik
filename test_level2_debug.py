#!/usr/bin/env python3
"""
Debug test specifically for Level 2 (Synonym Combinations)
"""
import sys
from services.multi_level_retriever import MultiLevelRetriever, get_next_batch
from services.keyword_extractor import generate_synonyms

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")

def test_synonym_generation():
    """Test that synonyms are generated correctly"""
    print_header("TEST 1: Synonym Generation")
    
    test_keywords = ["faith", "crumbs", "grace", "freedom"]
    
    for keyword in test_keywords:
        synonyms = generate_synonyms(keyword)
        print(f"\n  Keyword: '{keyword}'")
        print(f"  Synonyms: {synonyms}")
        print(f"  Count: {len(synonyms)}")

def test_level2_direct():
    """Test Level 2 method directly"""
    print_header("TEST 2: Level 2 Direct Method Call")
    
    keywords = ["faith", "crumbs"]
    retriever = MultiLevelRetriever(keywords)
    
    print(f"\n  Keywords: {keywords}")
    
    # Generate synonyms
    print(f"\n  Generating synonyms...")
    synonym_terms = retriever._get_all_synonym_terms()
    print(f"  All synonym terms: {synonym_terms}")
    print(f"  Total terms: {len(synonym_terms)}")
    
    # Fetch Level 2
    print(f"\n  Fetching Level 2 sentences...")
    used_texts = set()
    sentences, offset, exhausted = retriever.fetch_level2_synonym_combinations(
        offset=0,
        limit=10,
        used_texts=used_texts
    )
    
    print(f"\n  Results:")
    print(f"  - Found: {len(sentences)} sentences")
    print(f"  - Offset: {offset}")
    print(f"  - Exhausted: {exhausted}")
    
    if sentences:
        print(f"\n  Sample results:")
        for i, s in enumerate(sentences[:5], 1):
            combo = s.get('synonym_combo', 'N/A')
            print(f"\n  {i}. Combo: {combo}")
            print(f"     Score: {s.get('score', 0):.2f}")
            print(f"     Text: {s['text'][:100]}...")
    else:
        print(f"\n  ⚠️  No results found!")
    
    return len(sentences) > 0

def test_level2_via_batch():
    """Test Level 2 through get_next_batch (forcing to Level 2)"""
    print_header("TEST 3: Level 2 via get_next_batch")
    
    keywords = ["faith", "grace"]
    
    # Start directly at Level 2
    session_state = {
        "current_level": 2,  # Force start at Level 2
        "level_offsets": {"0": 999, "1": 999, "2": 0, "3": 0, "4": 0},
        "used_sentence_ids": []
    }
    
    print(f"\n  Keywords: {keywords}")
    print(f"  Starting at Level 2 (skipping 0 and 1)")
    
    sentences, updated_state, level_used = get_next_batch(
        session_state=session_state,
        keywords=keywords,
        batch_size=10,
        enabled_levels=[2]  # Only Level 2
    )
    
    print(f"\n  Results:")
    print(f"  - Level used: {level_used}")
    print(f"  - Found: {len(sentences)} sentences")
    print(f"  - Current level after: {updated_state['current_level']}")
    
    if sentences:
        print(f"\n  Sample results:")
        for i, s in enumerate(sentences[:5], 1):
            combo = s.get('synonym_combo', 'N/A')
            print(f"\n  {i}. Level: {s.get('level')}, Combo: {combo}")
            print(f"     Score: {s.get('score', 0):.2f}")
            print(f"     Text: {s['text'][:100]}...")
    else:
        print(f"\n  ⚠️  No results found at Level 2!")
    
    return level_used == 2 and len(sentences) > 0

def test_level2_offset_state():
    """Test that Level 2 offset tracking works correctly"""
    print_header("TEST 4: Level 2 Offset State Tracking")
    
    keywords = ["faith", "grace"]
    session_state = {
        "current_level": 2,
        "level_offsets": {"0": 999, "1": 999, "2": 0, "3": 0, "4": 0},
        "used_sentence_ids": []
    }
    
    print(f"\n  Getting multiple batches from Level 2...")
    
    all_texts = []
    for batch_num in range(1, 4):
        sentences, session_state, level_used = get_next_batch(
            session_state=session_state,
            keywords=keywords,
            batch_size=3,
            enabled_levels=[2]
        )
        
        print(f"\n  Batch {batch_num}:")
        print(f"  - Level: {level_used}")
        print(f"  - Sentences: {len(sentences)}")
        print(f"  - Offset after: {session_state['level_offsets'].get('2', 'N/A')}")
        
        if not sentences:
            print(f"  - Exhausted!")
            break
        
        # Check for duplicates
        for s in sentences:
            if s['text'] in all_texts:
                print(f"  ⚠️  DUPLICATE: {s['text'][:50]}...")
                return False
            all_texts.append(s['text'])
    
    print(f"\n  ✓ No duplicates found across {len(all_texts)} results")
    return True

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  LEVEL 2 (SYNONYM COMBINATIONS) DEBUG TEST")
    print("="*70)
    
    results = []
    
    try:
        test_synonym_generation()
    except Exception as e:
        print(f"\n❌ ERROR in synonym generation: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        results.append(("Level 2 direct method", test_level2_direct()))
    except Exception as e:
        print(f"\n❌ ERROR in Level 2 direct: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Level 2 direct method", False))
    
    try:
        results.append(("Level 2 via batch", test_level2_via_batch()))
    except Exception as e:
        print(f"\n❌ ERROR in Level 2 via batch: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Level 2 via batch", False))
    
    try:
        results.append(("Level 2 offset tracking", test_level2_offset_state()))
    except Exception as e:
        print(f"\n❌ ERROR in Level 2 offset: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Level 2 offset tracking", False))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 Level 2 is working correctly!")
        sys.exit(0)
    else:
        print("\n  ⚠️  Level 2 has issues. Check errors above.")
        sys.exit(1)
