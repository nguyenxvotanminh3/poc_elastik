import os
import sys
import requests
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load file .env
print("--- LOADING ENV ---")
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
es_host = os.getenv("ES_HOST", "http://localhost:9200")

# Kiểm tra xem đã load được key chưa
if not api_key:
    print("❌ ERROR: OPENAI_API_KEY is missing in .env file!")
    sys.exit(1)
else:
    print(f"✅ Found OpenAI Key: {api_key[:5]}...{api_key[-4:]}")

print(f"✅ Found ES Host: {es_host}")

# 2. Test kết nối Elasticsearch
print("\n--- TEST 1: CONNECTING TO ELASTICSEARCH ---")
try:
    r = requests.get(es_host, timeout=5)
    if r.status_code == 200:
        print(f"✅ Elasticsearch is ALIVE! Version: {r.json()['version']['number']}")
    else:
        print(f"❌ Elasticsearch responded with code: {r.status_code}")
        print(r.text)
except Exception as e:
    print(f"❌ Elasticsearch CONNECTION FAILED: {str(e)}")

# 3. Test kết nối OpenAI (Tạo thử 1 vector)
print("\n--- TEST 2: CONNECTING TO OPENAI ---")
try:
    client = OpenAI(api_key=api_key)
    print("Sending request to OpenAI...")
    resp = client.embeddings.create(
        input="Test connection",
        model="text-embedding-3-small"
    )
    print("✅ OpenAI is WORKING! Vector created successfully.")
except Exception as e:
    print(f"❌ OpenAI FAILED. Error details:\n{str(e)}")