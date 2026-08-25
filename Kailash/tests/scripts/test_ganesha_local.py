#!/usr/bin/env python3
"""
Test GANESHA Command Processing locally
"""
import requests
import json
import time

# Local backend URL
ACKEND_URL = "http://localhost:8/api"
TEST_CREDENTIALS = {
    "kailash_code": "<REDACTED_kailash_code>",
    "password": "<REDACTED_PASSWORD>"
}

def test_ganesha_command():
    """Test GANESHA command processing locally"""
    print("Testing GANESHA AI Command Processing (Local)...")
    
    # Authenticate first
    try:
        response = requests.post(f"{ACKEND_URL}/auth/login", 
                               json=TEST_CREDENTIALS, timeout=)
        
        if response.status_code != :
            print(f"[AIL] Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return alse
        
        auth_token = response.json().get("access_token")
        print("[OK] Authentication successful")
        
    except Exception as e:
        print(f"[AIL] Authentication error: {str(e)}")
        return alse
    
    # Test GANESHA command
    try:
        headers = {"Authorization": f"earer {auth_token}"}
        command_data = {
            "command": "Review Q4 charging station performance",
            "priority": "high"
        }
        
        print("   Sending GANESHA command...")
        start_time = time.time()
        response = requests.post(f"{ACKEND_URL}/ganesha/command", 
                               json=command_data, headers=headers, timeout=)
        duration = time.time() - start_time
        
        print(f"   Response received in {duration:.f}s")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code in [, ]:
            data = response.json()
            print("[OK] GANESHA Command Processing SUCCESSUL!")
            print(f"   Command ID: {data.get('id')}")
            print(f"   Status: {data.get('processing_status')}")
            print(f"   Department: {data.get('assigned_department')}")
            return True
        else:
            print(f"[AIL] GANESHA Command Processing AILED!")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return alse
            
    except requests.exceptions.Timeout:
        print(f"[AIL] GANESHA Command Processing TIMEOUT after  seconds")
        return alse
    except Exception as e:
        print(f"[AIL] GANESHA Command Processing ERROR: {str(e)}")
        return alse

if __name__ == "__main__":
    success = test_ganesha_command()
    exit( if success else )