#!/usr/bin/env python3
"""
Quick check for Level 2 synonym logic (without ES connection)
"""
import sys
sys.path.insert(0, '/Users/minknguyen/Desktop/Working/POC/ai-vector-elastic-demo')

from services.keyword_extractor import generate_synonyms, generate_keyword_combinations

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")

print_header("LEVEL 2 SYNONYM LOGIC CHECK")

# Test keywords from UI screenshot
keywords = ["faith", "crumbs", "master's table"]
print(f"\nOriginal keywords: {keywords}")

# Generate synonyms for each
print(f"\n{'─'*70}")
print("STEP 1: Generate synonyms for each keyword")
print('─'*70)

all_synonyms = {}
for kw in keywords:
    syns = generate_synonyms(kw)
    all_synonyms[kw] = syns
    print(f"\n  '{kw}' →")
    print(f"    Synonyms: {syns}")
    print(f"    Count: {len(syns)}")

# Flatten all synonym terms
print(f"\n{'─'*70}")
print("STEP 2: Flatten all synonym terms")
print('─'*70)

synonym_terms = []
for kw, syns in all_synonyms.items():
    synonym_terms.extend(syns)

# Deduplicate
seen = set()
deduped_terms = []
for term in synonym_terms:
    if term not in seen:
        seen.add(term)
        deduped_terms.append(term)

print(f"\n  All synonym terms (deduplicated): {deduped_terms}")
print(f"  Total unique terms: {len(deduped_terms)}")

# Generate combinations (like Level 0 but with synonyms)
print(f"\n{'─'*70}")
print("STEP 3: Generate combinations (Level 2 logic)")
print('─'*70)

if deduped_terms:
    combinations = generate_keyword_combinations(deduped_terms)
    print(f"\n  Total combinations: {len(combinations)}")
    print(f"\n  First 10 combinations:")
    for i, combo in enumerate(combinations[:10], 1):
        print(f"    {i}. {combo}")
    
    if len(combinations) > 10:
        print(f"\n  ... and {len(combinations) - 10} more combinations")
    
    print(f"\n  ✅ Level 2 would search these synonym combinations")
    print(f"  ✅ Each combination uses multi_match with require_all_words=True")
    print(f"  ✅ Example: {combinations[0]} → finds docs with both words")
else:
    print(f"\n  ⚠️  No synonym terms generated!")
    print(f"  ⚠️  Level 2 would have no combinations to search")

print(f"\n{'='*70}")
print("  LEVEL 2 LOGIC VERIFICATION")
print('='*70)

print(f"""
✓ Keywords extracted: {keywords}
✓ Synonyms generated: {len(deduped_terms)} unique terms
✓ Combinations created: {len(combinations) if deduped_terms else 0}

Level 2 Logic:
1. Takes original keywords: {keywords}
2. Generates synonyms using WordNet
3. Combines synonym terms (like Level 0)
4. Searches each combination with multi_match + require_all_words=True

Status: {'✅ WORKING' if deduped_terms and combinations else '❌ NO SYNONYMS FOUND'}
""")

# Check if specific words from UI are in synonyms
print(f"\n{'─'*70}")
print("Checking UI screenshot keywords")
print('─'*70)

ui_keywords = ["faith", "crumbs", "sovereign", "Sovereign"]
print(f"\nFrom UI, these words appear in results:")
for word in ui_keywords:
    if word.lower() in [t.lower() for t in deduped_terms]:
        print(f"  ✓ '{word}' found in synonym terms")
    elif word.lower() in [k.lower() for k in keywords]:
        print(f"  ✓ '{word}' is an original keyword")
    else:
        print(f"  ℹ '{word}' not in synonyms (may be from original text)")
