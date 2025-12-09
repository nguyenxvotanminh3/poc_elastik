#!/usr/bin/env python3
"""
Test deduplication logic locally with the exact texts
"""
import sys
sys.path.insert(0, '.')

from services.deduplicator import deduplicate_sentences, is_duplicate

# Exact texts from API response
text1 = 'Zechariah declares, "came again, and waked me, as a man that is waked out of his sleep, and said unto me, What seest thou.\n'
text2 = 'Zechariah declares, "came again, and waked me, as a man that is wakened out of his sleep, and said unto me, What seest thou.\n'

# Test 1: Direct is_duplicate check
print("=" * 80)
print("TEST 1: Direct is_duplicate() check")
print("=" * 80)

seen = set()
print(f"\nFirst text:")
print(f"  {text1[:80]}...")
result1 = is_duplicate(text1, seen, similarity_threshold=0.95)
print(f"  is_duplicate result: {result1}")
seen.add(text1)

print(f"\nSecond text:")
print(f"  {text2[:80]}...")
result2 = is_duplicate(text2, seen, similarity_threshold=0.95)
print(f"  is_duplicate result: {result2}")
print(f"  Expected: True (should be detected as duplicate)")

# Test 2: deduplicate_sentences function
print("\n" + "=" * 80)
print("TEST 2: deduplicate_sentences() function")
print("=" * 80)

sentences = [
    {"text": text1, "level": 1},
    {"text": text2, "level": 1},
]

print(f"\nInput: {len(sentences)} sentences")
result, seen_final = deduplicate_sentences(sentences, existing_texts=set(), similarity_threshold=0.95)
print(f"Output: {len(result)} sentences")
print(f"Expected: 1 sentence (duplicate removed)")

if len(result) == 1:
    print("✓ TEST PASSED")
else:
    print("✗ TEST FAILED - Both sentences still in output!")
    for i, s in enumerate(result):
        print(f"  #{i}: {s['text'][:80]}...")
