#!/usr/bin/env python3
"""
Test STRICT deduplication - only 100% exact matches
"""
from services.deduplicator import is_duplicate, deduplicate_sentences

# Test case from user's screenshot
test_sentences = [
    {"text": 'Zechariah declares, "came again, and waked me, as a man that is waked out of his sleep, and said unto me, What seest thou.'},
    {"text": 'Zechariah declares, "came again, and wakened me, as a man that is wakened out of his sleep, and said unto me, What seest thou.'},
    {"text": 'Another completely different sentence about something else.'},
    {"text": 'Zechariah declares, "came again, and waked me, as a man that is waked out of his sleep, and said unto me, What seest thou.'},  # Exact duplicate of first
]

print("=" * 80)
print("STRICT DEDUPLICATION TEST")
print("=" * 80)
print()

print("Input sentences:")
for i, sent in enumerate(test_sentences, 1):
    print(f"{i}. {sent['text'][:80]}...")
print()

# Test deduplication
result = deduplicate_sentences(test_sentences)

print(f"After deduplication: {len(result)} unique sentences (from {len(test_sentences)} input)")
print()
print("Unique sentences:")
for i, sent in enumerate(result, 1):
    print(f"{i}. {sent['text'][:80]}...")
print()

# Test individual comparisons
sent1 = test_sentences[0]['text']
sent2 = test_sentences[1]['text']

print("=" * 80)
print("DETAILED COMPARISON")
print("=" * 80)
print()
print(f"Sentence 1: {sent1}")
print()
print(f"Sentence 2: {sent2}")
print()
print(f"Are they duplicates? {is_duplicate(sent2, {sent1})}")
print()
print("Differences:")
print(f"  - Length: {len(sent1)} vs {len(sent2)}")
print(f"  - First difference at character: ", end="")
for i, (c1, c2) in enumerate(zip(sent1, sent2)):
    if c1 != c2:
        print(f"{i} ('{c1}' vs '{c2}')")
        break
else:
    print("None - strings are identical!")
print()

# Test with case difference
test_case = [
    {"text": "Hello World"},
    {"text": "hello world"},  # Different case
    {"text": "Hello  World"},  # Extra space
]

print("=" * 80)
print("CASE & SPACE SENSITIVITY TEST")
print("=" * 80)
print()
for sent in test_case:
    print(f"  '{sent['text']}'")
result_case = deduplicate_sentences(test_case)
print(f"\nResult: {len(result_case)} unique (STRICT mode keeps all 3)")
for i, sent in enumerate(result_case, 1):
    print(f"{i}. '{sent['text']}'")
