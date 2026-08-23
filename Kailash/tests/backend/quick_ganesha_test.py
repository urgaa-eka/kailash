#!/usr/bin/env python3
"""
Quick test for GANESHA external query with longer timeout
"""

import requests
import json

BACKEND_URL = "https://ganesha-v2-api.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "kailash_code": "<REDACTED_kailash_code>",
    "password": "<REDACTED_PASSWORD>"
}

def test_ganesha_external_with_longer_timeout():
    # Login first
    response = requests.post(f"{BACKEND_URL}/auth/login", json=TEST_CREDENTIALS, timeout=15)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    auth_token = response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Test external query with 60 second timeout
    payload = {
        "message": "How is URGAA charger utilization?",
        "model": "auto",
        "include_level2": True
    }
    
    print("Testing GANESHA external query with 60s timeout...")
    try:
        response = requests.post(f"{BACKEND_URL}/ganesha/query", 
                               json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Query routed to {data['routed_to']}")
            print(f"   Scope: {data['scope']}")
            print(f"   Source Product: {data.get('source_product')}")
            print(f"   Level: {data.get('level')}")
            print(f"   Models Used: {data['models_used']}")
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_ganesha_external_with_longer_timeout()