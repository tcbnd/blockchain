#!/usr/bin/env python3
"""Test HKBU GenAI API connection"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv('API_URL')
API_KEY = os.getenv('API_KEY')

print("=" * 60)
print("Testing HKBU GenAI API Connection")
print("=" * 60)
print(f"API URL: {API_URL[:80]}...")
print(f"API KEY: {API_KEY[:20]}...")
print()

# Test request
headers = {
    'Content-Type': 'application/json',
    'api-key': API_KEY
}

payload = {
    "messages": [
        {
            "role": "user",
            "content": "Say 'Hello' in one word"
        }
    ],
    "temperature": 0.1,
    "max_tokens": 50
}

print("Sending test request...")
print()

try:
    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=15
    )
    
    print(f"✅ Response Status: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API Connection Successful!")
        print()
        print("Response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ API Error: {response.status_code}")
        print()
        print("Error Response:")
        print(response.text[:500])
        
except requests.exceptions.Timeout:
    print("❌ Request Timeout - API took too long to respond")
    print("   This could mean:")
    print("   - API server is slow")
    print("   - Network connection is poor")
    print("   - API endpoint is down")
    
except requests.exceptions.ConnectionError as e:
    print("❌ Connection Error - Cannot reach API server")
    print(f"   Error: {e}")
    print("   This could mean:")
    print("   - API URL is incorrect")
    print("   - Network is blocked")
    print("   - Server is down")
    
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
