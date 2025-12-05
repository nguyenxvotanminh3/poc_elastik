import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

print("--- DIAGNOSING OPENAI 404 ---")
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ API Key missing")
    sys.exit(1)

# In ra key và base_url để kiểm tra
client = OpenAI(api_key=api_key)
print(f"🔑 Key prefix: {api_key[:8]}...")
print(f"🌐 Base URL: {client.base_url}")

# Thử model cũ hơn xem có chạy không
models_to_test = ["text-embedding-3-small", "text-embedding-ada-002"]

for model in models_to_test:
    print(f"\nTesting model: {model}...")
    try:
        client.embeddings.create(
            input="Test",
            model=model
        )
        print(f"✅ SUCCESS with {model}!")
        break # Nếu chạy được thì dừng
    except Exception as e:
        print(f"❌ FAILED with {model}")
        print(f"   Error Type: {type(e).__name__}")
        # In nội dung lỗi đầy đủ
        if hasattr(e, 'response'):
             print(f"   Response Code: {e.status_code}")
             print(f"   Full Message: {e.body}")
        else:
             print(f"   Error: {e}")