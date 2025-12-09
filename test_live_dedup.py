#!/usr/bin/env python3
"""
Test script để verify deduplication fix trên live server
Chạy sau khi deploy code mới
"""
import requests
import json
import sys

LIVE_API = "http://18.189.170.169:8000/ask"
LOCAL_API = "http://localhost:8000/ask"

def test_deduplication(api_url, name="Server"):
    """Test deduplication trên một API endpoint"""
    print(f"\n{'='*80}")
    print(f"Testing {name}: {api_url}")
    print(f"{'='*80}")
    
    payload = {"query": "Zechariah and the baby Jesus", "limit": 15}
    
    try:
        response = requests.post(api_url, json=payload, timeout=120)
        
        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.text[:200]}")
            return False
        
        data = response.json()
        sources = data.get("source_sentences", [])
        
        print(f"✅ Got {len(sources)} source sentences\n")
        
        # Check for "waked" variations
        waked_sentences = []
        for i, sent in enumerate(sources):
            text = sent.get("text", "").lower()
            if "waked" in text or "wakened" in text:
                waked_sentences.append((i, sent.get("text", "")))
        
        print(f"Sentences with 'waked'/'wakened': {len(waked_sentences)}")
        
        if waked_sentences:
            print("\nDetails:")
            for idx, text in waked_sentences:
                # Highlight the difference
                if "wakened" in text.lower():
                    highlight = "**wakened**"
                else:
                    highlight = "**waked**"
                print(f"  [{idx}] ...is {highlight} out of his sleep...")
        
        # Check for exact duplicates
        seen_texts = set()
        duplicates = []
        for sent in sources:
            text = sent.get("text", "")
            if text in seen_texts:
                duplicates.append(text)
            else:
                seen_texts.add(text)
        
        if duplicates:
            print(f"\n❌ Found {len(duplicates)} EXACT DUPLICATES")
            return False
        else:
            print(f"\n✅ No exact duplicates")
        
        # SUCCESS criteria
        if len(waked_sentences) <= 1:
            print(f"\n✅ PASS: Found {len(waked_sentences)} 'waked'/'wakened' sentence(s)")
            print("   (Expected max 1 - deduplication is working)")
            return True
        else:
            print(f"\n❌ FAIL: Found {len(waked_sentences)} 'waked'/'wakened' sentences")
            print("   (Expected max 1 - deduplication not working yet)")
            return False
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    # Test both servers
    local_pass = test_deduplication(LOCAL_API, "LOCAL Server (localhost:8000)")
    live_pass = test_deduplication(LIVE_API, "LIVE Server (AWS)")
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Local: {'✅ PASS' if local_pass else '❌ FAIL'}")
    print(f"Live:  {'✅ PASS' if live_pass else '❌ FAIL'}")
    print(f"{'='*80}\n")
    
    sys.exit(0 if live_pass else 1)
