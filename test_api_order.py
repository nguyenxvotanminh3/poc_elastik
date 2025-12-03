"""
Test thực sự qua API để xác nhận thứ tự.
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_via_api():
    """Test qua API để xác nhận thứ tự magic words."""
    
    query = "where is heaven"
    
    print("=" * 80)
    print(f"Testing via API: '{query}'")
    print("=" * 80)
    
    # Call /ask endpoint
    payload = {
        "query": query,
        "limit": 15,
        "buffer_percentage": 15
    }
    
    print("\nCalling POST /ask...")
    response = requests.post(f"{API_URL}/ask", json=payload, timeout=60)
    
    if response.status_code != 200:
        print(f"ERROR: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    sources = result.get("source_sentences", [])
    
    print(f"\nReceived {len(sources)} source sentences\n")
    print("Results in ORDER:")
    print("=" * 80)
    
    for i, src in enumerate(sources, 1):
        magic = src.get("magic_word", "NONE")
        level = src.get("level", 0)
        score = src.get("score", 0)
        text = src["text"][:70] + "..." if len(src["text"]) > 70 else src["text"]
        print(f"{i:2d}. [Magic: {magic:8s}] Level {level} (Score: {score:.2f})")
        print(f"    {text}\n")
    
    # Group by magic word
    print("\n" + "=" * 80)
    print("VERIFICATION: Grouping by magic word order")
    print("=" * 80)
    
    magic_order = []
    for src in sources:
        magic = src.get("magic_word", "NONE")
        if magic not in [m[0] for m in magic_order]:
            magic_order.append((magic, 1))
        else:
            # Increment count
            for idx, (m, count) in enumerate(magic_order):
                if m == magic:
                    magic_order[idx] = (m, count + 1)
    
    print("\nMagic word order:")
    for magic, count in magic_order:
        print(f"  {magic}: {count} sentences")
   
    # Check if first is "is"
    if magic_order and magic_order[0][0] == "is":
        print("\n✅ PASS: First magic word is 'is'")
    else:
        print(f"\n❌ FAIL: First magic word is '{magic_order[0][0]}' not 'is'")
    
    # Check expected order
    expected = ["is", "are", "was", "were", "be"]
    actual = [m for m, _ in magic_order]
    
    print(f"\n expected: {expected}")
    print(f"Actual: {actual[:len(expected)]}")

if __name__ == "__main__":
    test_via_api()
