#!/usr/bin/env python3
"""
GANESHA ORCHESTRATOR TESTING SUITE
Tests the real Anthropic API key integration as requested in review
"""

import requests
import json
import time
import sys
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
        self.test_results = []
        self.failed_tests = []
        self.auth_token = None
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        status = "[OK] PASS" if success else "[AIL] AIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "response_data": response_data
        }
        self.test_results.append(result)
        if not success:
            self.failed_tests.append(result)
        print(f"{status}: {test_name} - {message}")
        if response_data and isinstance(response_data, dict):
            # Don't print sensitive data like tokens
            safe_data = {k: v for k, v in response_data.items() if k not in ['access_token', 'hashed_password']}
            if safe_data:
                print(f"   Response: {safe_data}")
        elif response_data and not isinstance(response_data, dict):
            print(f"   Response: {response_data}")
        print()

    def authenticate(self):
        """Step : Authenticate and get JWT token"""
        print(" STEP : AUTHENTICATION")
        print("=" * )
        
        try:
            response = requests.post(f"{ACKEND_URL}/auth/login", 
                                   json=TEST_CREDENTIALS, timeout=)
            
            if response.status_code == :
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    user_data = data["user"]
                    
                    self.log_test("Authentication", True, 
                                f"Successfully authenticated with Kailash Code {TEST_CREDENTIALS['kailash_code']}", 
                                {"user": user_data, "token_received": True})
                    return True
                else:
                    self.log_test("Authentication", alse, 
                                f"Missing required fields in response", data)
            else:
                self.log_test("Authentication", alse, 
                            f"Status {response.status_code}, expected . Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Authentication", alse, f"Request failed: {str(e)}")
        
        return alse

    def test_orchestrate_simple_question(self):
        """Step : Test orchestrate endpoint with simple question"""
        print(" STEP : ORCHESTRATE ENDPOINT - SIMPLE QUESTION")
        print("=" * )
        
        if not self.auth_token:
            self.log_test("Orchestrate Simple Question", alse, "No auth token available")
            return alse
            
        try:
            headers = {"Authorization": f"earer {self.auth_token}"}
            orchestrate_data = {
                "user_message": "Hello GANESHA, what can you help me with?",
                "conversation_history": []
            }
            
            print(f"Sending request to: {ACKEND_URL}/ganesha/orchestrate")
            print(f"Request body: {json.dumps(orchestrate_data, indent=)}")
            print("Waiting for SSE stream response...")
            
            response = requests.post(f"{ACKEND_URL}/ganesha/orchestrate", 
                                   json=orchestrate_data, headers=headers, 
                                   timeout=, stream=True)
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == :
                # Check if it's SSE stream
                content_type = response.headers.get('content-type', '')
                if 'text/event-stream' in content_type:
                    print("[OK] SSE stream detected, reading events...")
                    
                    events_received = 
                    ganesha_thinking_events = 
                    claude_responses = []
                    
                    try:
                        for line in response.iter_lines(decode_unicode=True, chunk_size=):
                            if line and line.startswith('data: '):
                                events_received += 
                                data_str = line[:]  # Remove 'data: ' prefix
                                
                                try:
                                    event_data = json.loads(data_str)
                                    event_type = event_data.get('type', 'unknown')
                                    
                                    print(f"Event {events_received}: {event_type}")
                                    
                                    if event_type == 'ganesha_thinking':
                                        ganesha_thinking_events += 
                                        content = event_data.get('content', '')
                                        claude_responses.append(content)
                                        print(f"  Content: {content[:]}...")
                                    elif event_type == 'error':
                                        print(f"  Error: {event_data.get('message', 'Unknown error')}")
                                        break
                                    elif event_type == 'task_complete':
                                        print(f"  Summary: {event_data.get('summary', 'Task completed')}")
                                        break
                                        
                                except json.JSONDecodeError:
                                    print(f"  Raw data: {data_str[:]}...")
                                
                                # Stop after reasonable number of events or timeout
                                if events_received >= :
                                    print("Stopping after  events...")
                                    break
                                    
                    except requests.exceptions.ReadTimeout:
                        print("Stream read timeout - this is normal for SSE streams")
                    
                    # Evaluate results
                    full_response = ''.join(claude_responses)
                    
                    if ganesha_thinking_events >  and len(full_response) > :
                        # Check if response contains actual AI content (not placeholder)
                        if any(keyword in full_response.lower() for keyword in ['ganesha', 'help', 'assist', 'can', 'i am', 'namaste']):
                            self.log_test("Orchestrate Simple Question", True, 
                                        f"[OK] Real Claude API working! Received {ganesha_thinking_events} thinking events with intelligent response", 
                                        {"events_received": events_received, "thinking_events": ganesha_thinking_events, "response_length": len(full_response)})
                            return True
                        else:
                            self.log_test("Orchestrate Simple Question", alse, 
                                        f"Response seems like placeholder/simulation mode", 
                                        {"response_preview": full_response[:]})
                    else:
                        self.log_test("Orchestrate Simple Question", alse, 
                                    f"No meaningful ganesha_thinking events received", 
                                    {"events_received": events_received, "thinking_events": ganesha_thinking_events})
                else:
                    self.log_test("Orchestrate Simple Question", alse, 
                                f"Expected SSE stream, got content-type: {content_type}")
            elif response.status_code == 4:
                error_text = response.text
                if "anthropic" in error_text.lower() or "api" in error_text.lower():
                    self.log_test("Orchestrate Simple Question", alse, 
                                f"[AIL] Anthropic API authentication failed - check API key", 
                                {"error": error_text})
                else:
                    self.log_test("Orchestrate Simple Question", alse, 
                                f"Authentication error: {error_text}")
            elif response.status_code == :
                error_text = response.text
                self.log_test("Orchestrate Simple Question", alse, 
                            f"Server error - possible API integration issue: {error_text}")
            else:
                self.log_test("Orchestrate Simple Question", alse, 
                            f"Status {response.status_code}, expected . Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Orchestrate Simple Question", alse, f"Request failed: {str(e)}")
        
        return alse

    def test_orchestrate_kailash_status(self):
        """Step 3: Test another command about KAILASH project status"""
        print(" STEP 3: ORCHESTRATE ENDPOINT - KAILASH STATUS QUESTION")
        print("=" * )
        
        if not self.auth_token:
            self.log_test("Orchestrate KAILASH Status", alse, "No auth token available")
            return alse
            
        try:
            headers = {"Authorization": f"earer {self.auth_token}"}
            orchestrate_data = {
                "user_message": "What is the current status of the KAILASH project?",
                "conversation_history": []
            }
            
            print(f"Sending request to: {ACKEND_URL}/ganesha/orchestrate")
            print(f"Request body: {json.dumps(orchestrate_data, indent=)}")
            print("Waiting for SSE stream response...")
            
            response = requests.post(f"{ACKEND_URL}/ganesha/orchestrate", 
                                   json=orchestrate_data, headers=headers, 
                                   timeout=, stream=True)
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == :
                content_type = response.headers.get('content-type', '')
                if 'text/event-stream' in content_type:
                    print("[OK] SSE stream detected, reading events...")
                    
                    events_received = 
                    ganesha_thinking_events = 
                    claude_responses = []
                    
                    try:
                        for line in response.iter_lines(decode_unicode=True, chunk_size=):
                            if line and line.startswith('data: '):
                                events_received += 
                                data_str = line[:]
                                
                                try:
                                    event_data = json.loads(data_str)
                                    event_type = event_data.get('type', 'unknown')
                                    
                                    if event_type == 'ganesha_thinking':
                                        ganesha_thinking_events += 
                                        content = event_data.get('content', '')
                                        claude_responses.append(content)
                                        if ganesha_thinking_events <= 3:  # Show first few
                                            print(f"  Thinking {ganesha_thinking_events}: {content[:]}...")
                                    elif event_type == 'error':
                                        print(f"  Error: {event_data.get('message', 'Unknown error')}")
                                        break
                                    elif event_type == 'task_complete':
                                        print(f"  Summary: {event_data.get('summary', 'Task completed')}")
                                        break
                                        
                                except json.JSONDecodeError:
                                    pass
                                
                                if events_received >= :
                                    break
                                    
                    except requests.exceptions.ReadTimeout:
                        print("Stream read timeout - normal for SSE")
                    
                    # Evaluate results
                    full_response = ''.join(claude_responses)
                    
                    if ganesha_thinking_events >  and len(full_response) > :
                        # Check if response is contextual and intelligent
                        kailash_keywords = ['kailash', 'project', 'status', 'phase', 'development', 'production', 'Kailash']
                        if any(keyword in full_response.lower() for keyword in kailash_keywords):
                            self.log_test("Orchestrate KAILASH Status", True, 
                                        f"[OK] Claude responded intelligently about KAILASH project", 
                                        {"events_received": events_received, "thinking_events": ganesha_thinking_events, "contextual": True})
                            return True
                        else:
                            self.log_test("Orchestrate KAILASH Status", alse, 
                                        f"Response not contextual to KAILASH project", 
                                        {"response_preview": full_response[:]})
                    else:
                        self.log_test("Orchestrate KAILASH Status", alse, 
                                    f"Insufficient response from Claude", 
                                    {"events_received": events_received, "thinking_events": ganesha_thinking_events})
                else:
                    self.log_test("Orchestrate KAILASH Status", alse, 
                                f"Expected SSE stream, got content-type: {content_type}")
            else:
                self.log_test("Orchestrate KAILASH Status", alse, 
                            f"Status {response.status_code}, expected . Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Orchestrate KAILASH Status", alse, f"Request failed: {str(e)}")
        
        return alse

    def test_quick_actions(self):
        """Test quick action endpoints"""
        print("⚡ STEP 4: QUICK ACTION ENDPOINTS")
        print("=" * )
        
        if not self.auth_token:
            self.log_test("Quick Actions", alse, "No auth token available")
            return
            
        headers = {"Authorization": f"earer {self.auth_token}"}
        actions = ['status', 'review', 'next_steps', 'help']
        
        for action in actions:
            try:
                action_data = {"action": action}
                response = requests.post(f"{ACKEND_URL}/ganesha/quick-action", 
                                       json=action_data, headers=headers, timeout=)
                
                if response.status_code == :
                    data = response.json()
                    if data.get("action") == action and "message" in data:
                        self.log_test(f"Quick Action ({action})", True, 
                                    f"Action returned message: {data.get('message')[:]}...")
                    else:
                        self.log_test(f"Quick Action ({action})", alse, 
                                    f"Invalid response structure", data)
                else:
                    self.log_test(f"Quick Action ({action})", alse, 
                                f"Status {response.status_code}, expected ")
                    
            except requests.exceptions.RequestException as e:
                self.log_test(f"Quick Action ({action})", alse, f"Request failed: {str(e)}")

    def test_stats_and_history(self):
        """Test stats and history endpoints"""
        print(" STEP : STATS AND HISTORY ENDPOINTS")
        print("=" * )
        
        if not self.auth_token:
            self.log_test("Stats and History", alse, "No auth token available")
            return
            
        headers = {"Authorization": f"earer {self.auth_token}"}
        
        # Test stats
        try:
            response = requests.get(f"{ACKEND_URL}/ganesha/stats", headers=headers, timeout=)
            
            if response.status_code == :
                data = response.json()
                required_fields = ["total_commands", "completed_commands", "success_rate", 
                                 "estimated_credits_saved", "efficiency_percentage"]
                
                if all(field in data for field in required_fields):
                    self.log_test("GANESHA Stats", True, 
                                f"Stats retrieved successfully", 
                                {k: data[k] for k in required_fields})
                else:
                    self.log_test("GANESHA Stats", alse, 
                                f"Missing required fields")
            else:
                self.log_test("GANESHA Stats", alse, 
                            f"Status {response.status_code}, expected ")
                
        except requests.exceptions.RequestException as e:
            self.log_test("GANESHA Stats", alse, f"Request failed: {str(e)}")
        
        # Test history
        try:
            response = requests.get(f"{ACKEND_URL}/ganesha/history", headers=headers, timeout=)
            
            if response.status_code == :
                data = response.json()
                if "commands" in data and "total" in data:
                    self.log_test("GANESHA History", True, 
                                f"History retrieved successfully", 
                                {"commands_count": len(data.get("commands", [])), "total": data.get("total", )})
                else:
                    self.log_test("GANESHA History", alse, 
                                f"Missing required fields")
            else:
                self.log_test("GANESHA History", alse, 
                            f"Status {response.status_code}, expected ")
                
        except requests.exceptions.RequestException as e:
            self.log_test("GANESHA History", alse, f"Request failed: {str(e)}")

    def run_comprehensive_test(self):
        """Run the comprehensive GANESHA Orchestrator test as per review request"""
        print("=" * 8)
        print(" GANESHA ORCHESTRATOR COMPREHENSIVE TEST")
        print("Testing Real Anthropic API Key Integration")
        print("=" * 8)
        print(f"ackend URL: {ACKEND_URL}")
        print(f"Test Credentials: Kailash Code {TEST_CREDENTIALS['kailash_code']}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        # Step : Authentication
        if not self.authenticate():
            print("[AIL] AUTHENTICATION AILED - Cannot proceed with tests")
            return
        
        print()
        
        # Step : Test orchestrate with simple question
        simple_success = self.test_orchestrate_simple_question()
        print()
        
        # Step 3: Test orchestrate with KAILASH status question
        kailash_success = self.test_orchestrate_kailash_status()
        print()
        
        # Step 4: Test quick actions
        self.test_quick_actions()
        print()
        
        # Step : Test stats and history
        self.test_stats_and_history()
        print()
        
        # inal Summary
        print("=" * 8)
        print(" INAL TEST SUMMARY")
        print("=" * 8)
        
        total_tests = len(self.test_results)
        passed_tests = total_tests - len(self.failed_tests)
        
        print(f"Total Tests Executed: {total_tests}")
        print(f"[OK] Passed: {passed_tests}")
        print(f"[AIL] ailed: {len(self.failed_tests)}")
        print(f" Success Rate: {(passed_tests/total_tests)*:.f}%")
        print()
        
        # Key Results
        print(" KEY RESULTS:")
        if simple_success and kailash_success:
            print("[OK] Anthropic API key is working correctly")
            print("[OK] Claude AI responses are intelligent and contextual")
            print("[OK] SSE streaming is functional")
            print("[OK] No more placeholder/simulation mode")
        elif simple_success or kailash_success:
            print("[WARN] Partial success - some Claude responses working")
            print("[WARN] May need further investigation")
        else:
            print("[AIL] Anthropic API integration issues detected")
            print("[AIL] May still be in placeholder/simulation mode")
        
        print()
        
        if self.failed_tests:
            print("[AIL] AILED TESTS:")
            for test in self.failed_tests:
                print(f"   • {test['test']}: {test['message']}")
        
        print()
        print("=" * 8)

if __name__ == "__main__":
    tester = GaneshaOrchestratorTester()
    tester.run_comprehensive_test()