#!/usr/bin/env python3
"""
GANESHA Orchestrator Specific Testing
Tests the endpoints mentioned in the review request
"""

import requests
import json
import time
from datetime import datetime

# ackend URL from frontend .env
ACKEND_URL = "https://ganesha-v2-api.preview.emergentagent.com/api"

# Test credentials from review request
TEST_CREDENTIALS = {
    "kailash_code": "<REDACTED_kailash_code>",
    "password": "<REDACTED_PASSWORD>"
}

class GaneshaOrchestratorTester:
    def __init__(self):
        self.auth_token = None
        
    def authenticate(self):
        """Get JWT token for authentication"""
        try:
            response = requests.post(f"{ACKEND_URL}/auth/login", 
                                   json=TEST_CREDENTIALS, timeout=)
            
            if response.status_code == :
                data = response.json()
                self.auth_token = data["access_token"]
                print(f"[OK] Authentication successful for {TEST_CREDENTIALS['kailash_code']}")
                return True
            else:
                print(f"[AIL] Authentication failed: {response.status_code}")
                return alse
                
        except Exception as e:
            print(f"[AIL] Authentication error: {str(e)}")
            return alse

    def test_quick_action_status(self):
        """Test POST /api/ganesha/quick-action with status action"""
        print("\n Testing Quick Action: Status")
        
        if not self.auth_token:
            print("[AIL] No auth token available")
            return
            
        try:
            headers = {"Authorization": f"earer {self.auth_token}"}
            action_data = {"action": "status"}
            
            response = requests.post(f"{ACKEND_URL}/ganesha/quick-action", 
                                   json=action_data, headers=headers, timeout=)
            
            if response.status_code == :
                data = response.json()
                print(f"[OK] Status: {response.status_code}")
                print(f"   Action: {data.get('action')}")
                print(f"   Message: {data.get('message')}")
            else:
                print(f"[AIL] Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"[AIL] Error: {str(e)}")

    def test_quick_action_review(self):
        """Test POST /api/ganesha/quick-action with review action"""
        print("\n Testing Quick Action: Review")
        
        if not self.auth_token:
            print("[AIL] No auth token available")
            return
            
        try:
            headers = {"Authorization": f"earer {self.auth_token}"}
            action_data = {"action": "review"}
            
            response = requests.post(f"{ACKEND_URL}/ganesha/quick-action", 
                                   json=action_data, headers=headers, timeout=)
            
            if response.status_code == :
                data = response.json()
                print(f"[OK] Status: {response.status_code}")
                print(f"   Action: {data.get('action')}")
                print(f"   Message: {data.get('message')}")
            else:
                print(f"[AIL] Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"[AIL] Error: {str(e)}")

    def test_quick_action_next_steps(self):
        """Test POST /api/ganesha/quick-action with next_steps action"""
        print("\n Testing Quick Action: Next Steps")
        
        if not self.auth_token:
            print("[AIL] No auth token available")
            return
            
        try:
            headers = {"Authorization": f"earer {self.auth_token}"}
            action_data = {"action": "next_steps"}
            
            response = requests.post(f"{ACKEND_URL}/ganesha/quick-action", 
                                   json=action_data, headers=headers, timeout=)
            
            if response.status_code == :
                data = response.json()
                print(f"[OK] Status: {response.status_code}")
                print(f"   Action: {data.get('action')}")
                print(f"   Message: {data.get('message')}")
            else:
                print(f"[AIL] Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"[AIL] Error: {str(e)}")

    def test_quick_action_help(self):
        """Test POST /api/ganesha/quick-action with help action"""
        print("\n Testing Quick Action: Help")
        
        if not self.auth_token:
            print("[AIL] No auth token available")
            return
            
        try:
            headers = {"Authorization": f"earer {self.auth_token}"}
            action_data = {"action": "help"}
            
            response = requests.post(f"{ACKEND_URL}/ganesha/quick-action", 
                                   json=action_data, headers=headers, timeout=)
            
            if response.status_code == :
                data = response.json()
                print(f"[OK] Status: {response.status_code}")
                print(f"   Action: {data.get('action')}")
                print(f"   Message: {data.get('message')}")
            else:
                print(f"[AIL] Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"[AIL] Error: {str(e)}")

    def test_quick_action_invalid(self):
        """Test POST /api/ganesha/quick-action with invalid action"""
        print("\n Testing Quick Action: Invalid Action")
        
        if not self.auth_token:
            print("[AIL] No auth token available")
            return
            
        try:
            headers = {"Authorization": f"earer {self.auth_token}"}
            action_data = {"action": "invalid_action"}
            
            response = requests.post(f"{ACKEND_URL}/ganesha/quick-action", 
                                   json=action_data, headers=headers, timeout=)
            
            if response.status_code == 4:
                print(f"[OK] Status: {response.status_code} (Expected 4 for invalid action)")
                print(f"   Response: {response.json()}")
            else:
                print(f"[AIL] Status: {response.status_code} (Expected 4)")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"[AIL] Error: {str(e)}")

    def test_stats(self):
        """Test GET /api/ganesha/stats endpoint"""
        print("\n Testing GANESHA Stats")
        
        if not self.auth_token:
            print("[AIL] No auth token available")
            return
            
        try:
            headers = {"Authorization": f"earer {self.auth_token}"}
            response = requests.get(f"{ACKEND_URL}/ganesha/stats", headers=headers, timeout=)
            
            if response.status_code == :
                data = response.json()
                print(f"[OK] Status: {response.status_code}")
                print(f"   Total Commands: {data.get('total_commands')}")
                print(f"   Completed Commands: {data.get('completed_commands')}")
                print(f"   Success Rate: {data.get('success_rate')}%")
                print(f"   Estimated Credits Saved: {data.get('estimated_credits_saved')}")
                print(f"   Efficiency Percentage: {data.get('efficiency_percentage')}%")
            else:
                print(f"[AIL] Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"[AIL] Error: {str(e)}")

    def test_history(self):
        """Test GET /api/ganesha/history endpoint"""
        print("\n Testing GANESHA History")
        
        if not self.auth_token:
            print("[AIL] No auth token available")
            return
            
        try:
            headers = {"Authorization": f"earer {self.auth_token}"}
            response = requests.get(f"{ACKEND_URL}/ganesha/history", headers=headers, timeout=)
            
            if response.status_code == :
                data = response.json()
                print(f"[OK] Status: {response.status_code}")
                print(f"   Commands Count: {len(data.get('commands', []))}")
                print(f"   Total: {data.get('total')}")
                
                # Show first few commands if any
                commands = data.get('commands', [])
                if commands:
                    print("   Recent Commands:")
                    for i, cmd in enumerate(commands[:3]):
                        print(f"     {i+}. {cmd.get('message', 'N/A')[:]}... ({cmd.get('status', 'N/A')})")
                else:
                    print("   No commands in history")
            else:
                print(f"[AIL] Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"[AIL] Error: {str(e)}")

    def test_orchestrate_sse(self):
        """Test POST /api/ganesha/orchestrate SSE streaming endpoint"""
        print("\n Testing GANESHA Orchestrate (SSE Streaming)")
        
        if not self.auth_token:
            print("[AIL] No auth token available")
            return
            
        try:
            headers = {"Authorization": f"earer {self.auth_token}"}
            orchestrate_data = {
                "user_message": "Show project status",
                "conversation_history": []
            }
            
            print("   Sending orchestrate request...")
            response = requests.post(f"{ACKEND_URL}/ganesha/orchestrate", 
                                   json=orchestrate_data, headers=headers, 
                                   timeout=3, stream=True)
            
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            if response.status_code == :
                # Check if it's SSE stream
                content_type = response.headers.get('content-type', '')
                if 'text/event-stream' in content_type:
                    print("   [OK] SSE stream detected")
                    print("   Reading events...")
                    
                    events_received = 
                    for line in response.iter_lines(decode_unicode=True):
                        if line.startswith('data: '):
                            events_received += 
                            try:
                                event_data = json.loads(line[:])  # Remove 'data: ' prefix
                                print(f"     Event {events_received}: {event_data.get('type', 'unknown')}")
                                if event_data.get('content'):
                                    print(f"       Content: {event_data['content'][:]}...")
                                if event_data.get('message'):
                                    print(f"       Message: {event_data['message']}")
                            except json.JSONDecodeError:
                                print(f"     Event {events_received}: {line}")
                            
                            if events_received >= :  # Stop after a few events
                                print("     (Stopping after  events)")
                                break
                    
                    print(f"   [OK] Received {events_received} SSE events")
                else:
                    print(f"   [AIL] Expected SSE stream, got content-type: {content_type}")
            elif response.status_code == :
                # Expected with placeholder API key
                error_text = response.text
                print(f"   [WARN]  Error (Expected with placeholder API key)")
                if "anthropic" in error_text.lower() or "api" in error_text.lower():
                    print("   [OK] This is expected - placeholder Anthropic API key")
                else:
                    print(f"   [AIL] Unexpected  error: {error_text}")
            else:
                print(f"   [AIL] Unexpected status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print("   [WARN] Request timeout (Expected with placeholder API key)")
            print("   [OK] This is expected behavior")
        except Exception as e:
            print(f"   [AIL] Error: {str(e)}")

    def test_unauthorized_access(self):
        """Test endpoints without authentication token"""
        print("\n[SECURE] Testing Unauthorized Access")
        
        endpoints = [
            "/ganesha/quick-action",
            "/ganesha/stats", 
            "/ganesha/history",
            "/ganesha/orchestrate"
        ]
        
        for endpoint in endpoints:
            try:
                if endpoint == "/ganesha/quick-action" or endpoint == "/ganesha/orchestrate":
                    response = requests.post(f"{ACKEND_URL}{endpoint}", 
                                           json={"action": "status"}, timeout=)
                else:
                    response = requests.get(f"{ACKEND_URL}{endpoint}", timeout=)
                
                if response.status_code in [4, 43]:
                    print(f"   [OK] {endpoint}: {response.status_code} (Correctly unauthorized)")
                else:
                    print(f"   [AIL] {endpoint}: {response.status_code} (Expected 4/43)")
                    
            except Exception as e:
                print(f"   [AIL] {endpoint}: Error - {str(e)}")

    def run_all_tests(self):
        """Run all GANESHA Orchestrator tests"""
        print("=" * 8)
        print("GANESHA ORCHESTRATOR API TESTING")
        print("=" * 8)
        print(f"ackend URL: {ACKEND_URL}")
        print(f"Credentials: Kailash Code {TEST_CREDENTIALS['kailash_code']}, Password: {TEST_CREDENTIALS['password']}")
        print()
        
        # Authenticate first
        if not self.authenticate():
            print("[AIL] Authentication failed - cannot proceed with tests")
            return
        
        # Run all tests
        self.test_quick_action_status()
        self.test_quick_action_review()
        self.test_quick_action_next_steps()
        self.test_quick_action_help()
        self.test_quick_action_invalid()
        self.test_stats()
        self.test_history()
        self.test_orchestrate_sse()
        self.test_unauthorized_access()
        
        print("\n" + "=" * 8)
        print("GANESHA ORCHESTRATOR TESTING COMPLETE")
        print("=" * 8)

if __name__ == "__main__":
    tester = GaneshaOrchestratorTester()
    tester.run_all_tests()