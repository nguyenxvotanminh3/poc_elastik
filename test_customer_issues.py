#!/usr/bin/env python3
"""
Test script to verify fixes for customer issues:
1. Short/duplicate sentences (e.g., "Lord.", "faith.")
2. Missing primary sources on "Tell me more"
3. Strange level numbers (showing sentence_index instead of level)

Run this script after starting the API server:
    python main.py

Then run:
    python test_customer_issues.py
"""
import requests
import json
from typing import List, Dict, Any

API_BASE_URL = "http://localhost:8000"

def print_header(title: str):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_sentence(idx: int, sent: Dict[str, Any]):
    text = sent.get("text", "")[:80] + ("..." if len(sent.get("text", "")) > 80 else "")
    level = sent.get("level", "?")
    source_type = sent.get("source_type", "Unknown")
    is_primary = sent.get("is_primary_source", False)
    score = sent.get("score", 0)
    
    primary_tag = "🟢 PRIMARY" if is_primary else "🔵 SECONDARY"
    print(f"  {idx}. [{primary_tag}] Level: {level} | Score: {score:.2f}")
    print(f"      Source: {source_type}")
    print(f"      Text: {text}")
    print()

def check_health():
    """Check if API is running"""
    try:
        resp = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ API is healthy: {data.get('status')}")
            print(f"   Documents: {data.get('documents_indexed', 0)}")
            return data.get('documents_indexed', 0) > 0
    except Exception as e:
        print(f"❌ API is not running: {e}")
    return False

def test_short_sentence_filter():
    """Test that short sentences are filtered out"""
    print_header("TEST 1: Short Sentence Filter")
    
    # Test the is_valid_sentence function directly
    from services.multi_level_retriever import is_valid_sentence
    
    test_cases = [
        ("Lord.", False),
        ("faith.", False),
        ("The Lord.", False),
        ("This is faith.", False),
        ("Lord give me faith", False),  # Only 4 words but less than 20 chars
        ("Lord give me the faith of the woman who asked for crumbs from the Master's table.", True),
        ("The Lord will greatly bless those who work in faith.", True),
        ("When you ask God for your daily bread, he looks right into your heart.", True),
    ]
    
    all_passed = True
    for text, expected in test_cases:
        result = is_valid_sentence(text)
        status = "✅" if result == expected else "❌"
        if result != expected:
            all_passed = False
        print(f"  {status} '{text[:50]}...' → {result} (expected: {expected})")
    
    return all_passed

def test_ask_endpoint():
    """Test /ask endpoint with customer's query"""
    print_header("TEST 2: /ask Endpoint - Check for Short Sentences")
    
    query = "Lord give me the faith of the woman who asked for crumbs from the Master's table."
    
    payload = {
        "query": query,
        "limit": 15,
        "buffer_percentage": 15
    }
    
    try:
        resp = requests.post(f"{API_BASE_URL}/ask", json=payload, timeout=120)
        if resp.status_code != 200:
            print(f"❌ Error: {resp.status_code} - {resp.text[:200]}")
            return None, False
        
        data = resp.json()
        session_id = data.get("session_id")
        source_sentences = data.get("source_sentences", [])
        
        print(f"  Session ID: {session_id}")
        print(f"  Total sentences: {len(source_sentences)}")
        
        # Check for short sentences
        short_sentences = []
        primary_count = 0
        secondary_count = 0
        
        for sent in source_sentences:
            text = sent.get("text", "")
            if len(text) < 20 or len(text.split()) < 4:
                short_sentences.append(text)
            if sent.get("is_primary_source"):
                primary_count += 1
            else:
                secondary_count += 1
        
        print(f"\n  📊 Summary:")
        print(f"     Primary sources: {primary_count}")
        print(f"     Secondary sources: {secondary_count}")
        print(f"     Short sentences found: {len(short_sentences)}")
        
        if short_sentences:
            print(f"\n  ❌ SHORT SENTENCES FOUND (BUG!):")
            for s in short_sentences[:5]:
                print(f"     - '{s}'")
        else:
            print(f"\n  ✅ No short sentences! Filter is working.")
        
        # Show first few sentences
        print(f"\n  📄 First 5 sentences:")
        for i, sent in enumerate(source_sentences[:5], 1):
            print_sentence(i, sent)
        
        return session_id, len(short_sentences) == 0 and primary_count > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, False

def test_continue_endpoint(session_id: str):
    """Test /continue endpoint - check primary sources still appear"""
    print_header("TEST 3: /continue Endpoint - Check Primary Sources")
    
    if not session_id:
        print("  ⚠️ No session_id, skipping test")
        return False
    
    all_passed = True
    
    for i in range(3):  # Test 3 "Tell me more" calls
        print(f"\n  --- Tell me more #{i+1} ---")
        
        payload = {
            "session_id": session_id,
            "limit": 15,
            "buffer_percentage": 15
        }
        
        try:
            resp = requests.post(f"{API_BASE_URL}/continue", json=payload, timeout=120)
            if resp.status_code != 200:
                print(f"  ⚠️ Continue #{i+1} returned: {resp.status_code}")
                break
            
            data = resp.json()
            source_sentences = data.get("source_sentences", [])
            can_continue = data.get("can_continue", False)
            current_level = data.get("current_level", "?")
            
            # Count sources
            primary_count = sum(1 for s in source_sentences if s.get("is_primary_source"))
            secondary_count = len(source_sentences) - primary_count
            
            # Check for short sentences
            short_sentences = [s.get("text") for s in source_sentences 
                             if len(s.get("text", "")) < 20 or len(s.get("text", "").split()) < 4]
            
            print(f"  Current Level: {current_level}")
            print(f"  Sentences: {len(source_sentences)} (Primary: {primary_count}, Secondary: {secondary_count})")
            print(f"  Can continue: {can_continue}")
            print(f"  Short sentences: {len(short_sentences)}")
            
            if primary_count == 0:
                print(f"  ❌ NO PRIMARY SOURCES! This is a bug.")
                all_passed = False
            else:
                print(f"  ✅ Primary sources present")
            
            if short_sentences:
                print(f"  ❌ Short sentences found: {short_sentences[:3]}")
                all_passed = False
            else:
                print(f"  ✅ No short sentences")
            
            if not can_continue:
                print(f"  📍 Reached end of exploration")
                break
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            all_passed = False
            break
    
    return all_passed

def test_level_display():
    """Test that level numbers are correct (not sentence_index)"""
    print_header("TEST 4: Level Display Check")
    
    query = "faith"
    
    payload = {
        "query": query,
        "limit": 15
    }
    
    try:
        resp = requests.post(f"{API_BASE_URL}/ask", json=payload, timeout=120)
        if resp.status_code != 200:
            print(f"❌ Error: {resp.status_code}")
            return False
        
        data = resp.json()
        source_sentences = data.get("source_sentences", [])
        
        # Check for strange level numbers (> 10 usually means it's sentence_index)
        strange_levels = []
        for sent in source_sentences:
            level = sent.get("level")
            # Level should be 0-4, "Semantic", or similar. Not large numbers
            if isinstance(level, int) and level > 10:
                strange_levels.append((level, sent.get("text", "")[:50]))
        
        print(f"  Total sentences: {len(source_sentences)}")
        print(f"  Strange levels (>10): {len(strange_levels)}")
        
        if strange_levels:
            print(f"\n  ❌ STRANGE LEVELS FOUND (sentence_index leak?):")
            for lvl, text in strange_levels[:5]:
                print(f"     Level {lvl}: '{text}...'")
            return False
        else:
            print(f"  ✅ All levels are valid (0-4 or 'Semantic')")
            
            # Show level distribution
            levels = {}
            for sent in source_sentences:
                lvl = str(sent.get("level", "?"))
                levels[lvl] = levels.get(lvl, 0) + 1
            print(f"\n  Level distribution: {levels}")
            
            return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "🔍 "*20)
    print("  CUSTOMER ISSUE TEST SUITE")
    print("🔍 "*20)
    
    # Check API health
    if not check_health():
        print("\n❌ API not running or no documents. Please start the server first:")
        print("   python main.py")
        return
    
    results = {}
    
    # Test 1: Short sentence filter
    results["short_filter"] = test_short_sentence_filter()
    
    # Test 2: /ask endpoint
    session_id, ask_passed = test_ask_endpoint()
    results["ask_endpoint"] = ask_passed
    
    # Test 3: /continue endpoint
    if session_id:
        results["continue_endpoint"] = test_continue_endpoint(session_id)
    
    # Test 4: Level display
    results["level_display"] = test_level_display()
    
    # Summary
    print_header("TEST SUMMARY")
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("  🎉 ALL TESTS PASSED! Fixes are working correctly.")
    else:
        print("  ⚠️ SOME TESTS FAILED. Please review the output above.")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
