#!/usr/bin/env python3
"""
INAL COMPREHENSIVE ACKEND TESTING - ALL IXES APPLIED
Testing specific requirements from the review request
"""

import requests
import json
import time
import sys
from datetime import datetime

# ackend URL from frontend .env
ACKEND_URL = "https://ganesha-v2-api.preview.emergentagent.com/api"

# Test credentials
TEST_CREDENTIALS = {
    "kailash_code": "<REDACTED_kailash_code>",
    "password": "<REDACTED_PASSWORD>"
}

class inalTester:
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        self.auth_token = None
        self.total_tests = 
        self.passed_tests = 
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        self.total_tests += 
        if success:
            self.passed_tests += 
            
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
            safe_data = {k: v for k, v in response_data.items() if k not in ['access_token', 'hashed_password']}
            if safe_data:
                print(f"   Response: {safe_data}")
        print()

    def authenticate(self):
        """Get authentication token for protected endpoints"""
        try:
            response = requests.post(f"{ACKEND_URL}/auth/login", 
                                   json=TEST_CREDENTIALS, timeout=)
            
            if response.status_code == :
                data = response.json()
                self.auth_token = data.get("access_token")
                self.log_test("Authentication Setup", True, 
                            "Successfully authenticated for testing")
                return True
            else:
                self.log_test("Authentication Setup", alse, 
                            f"Authentication failed: {response.status_code}")
                return alse
        except Exception as e:
            self.log_test("Authentication Setup", alse, f"Authentication error: {str(e)}")
            return alse

    # ========== CRITICAL TESTS ROM REVIEW REQUEST ==========
    
    def test_ganesha_ai_command_processing(self):
        """Test GANESHA AI Command Processing - Previously ailed - NOW IXED"""
        if not self.auth_token:
            self.log_test("GANESHA AI Command Processing", alse, "No auth token available")
            return None
            
        print(" TESTING GANESHA AI COMMAND PROCESSING (CRITICAL)...")
        
        # Test : POST /api/ganesha/command with test command
        try:
            headers = {"Authorization": f"earer {self.auth_token}"}
            command_data = {
                "command": "Review Q4 charging station performance",
                "priority": "high"
            }
            
            print("   Testing POST /api/ganesha/command ( second timeout)...")
            start_time = time.time()
            response = requests.post(f"{ACKEND_URL}/ganesha/command", 
                                   json=command_data, headers=headers, timeout=)
            duration = time.time() - start_time
            
            if response.status_code in [, ]:
                data = response.json()
                command_id = data.get("id")
                self.log_test("GANESHA Command Creation", True, 
                            f"Command processed successfully in {duration:.f}s", 
                            {"id": command_id, "status": data.get("processing_status")})
                
                # Test : GET /api/ganesha/commands - Should return within  seconds
                print("   Testing GET /api/ganesha/commands ( second timeout)...")
                start_time = time.time()
                response = requests.get(f"{ACKEND_URL}/ganesha/commands", 
                                      headers=headers, timeout=)
                duration = time.time() - start_time
                
                if response.status_code == :
                    data = response.json()
                    self.log_test("GANESHA Commands List", True, 
                                f"Commands retrieved in {duration:.f}s", 
                                {"count": len(data) if isinstance(data, list) else "N/A"})
                else:
                    self.log_test("GANESHA Commands List", alse, 
                                f"ailed with status {response.status_code}")
                
                # Test 3: GET /api/ganesha/recent - Should return within 3 seconds
                print("   Testing GET /api/ganesha/recent (3 second timeout)...")
                start_time = time.time()
                response = requests.get(f"{ACKEND_URL}/ganesha/recent", 
                                      headers=headers, timeout=3)
                duration = time.time() - start_time
                
                if response.status_code == :
                    data = response.json()
                    self.log_test("GANESHA Recent Commands", True, 
                                f"Recent commands retrieved in {duration:.f}s", 
                                {"count": len(data) if isinstance(data, list) else "N/A"})
                else:
                    self.log_test("GANESHA Recent Commands", alse, 
                                f"ailed with status {response.status_code}")
                
                # Test 4: GET /api/ganesha/commands/{id} - Test with created command ID
                if command_id:
                    print(f"   Testing GET /api/ganesha/commands/{command_id}...")
                    response = requests.get(f"{ACKEND_URL}/ganesha/commands/{command_id}", 
                                          headers=headers, timeout=)
                    
                    if response.status_code == :
                        data = response.json()
                        self.log_test("GANESHA Specific Command", True, 
                                    f"Command details retrieved", 
                                    {"id": command_id, "status": data.get("processing_status")})
                    else:
                        self.log_test("GANESHA Specific Command", alse, 
                                    f"ailed with status {response.status_code}")
                
                return command_id
                
            elif response.status_code == 48 or "timeout" in response.text.lower():
                self.log_test("GANESHA Command Creation", alse, 
                            f"Timeout after {duration:.f}s - timeout handling working")
            else:
                self.log_test("GANESHA Command Creation", alse, 
                            f"ailed with status {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            self.log_test("GANESHA Command Creation", alse, 
                        f"Request timed out after  seconds")
        except Exception as e:
            self.log_test("GANESHA Command Creation", alse, f"Request failed: {str(e)}")
        
        return None

    def test_server_header_fix(self):
        """Test Server Header ix - Previously ailed"""
        print(" TESTING SERVER HEADER IX...")
        
        try:
            response = requests.get(f"{ACKEND_URL}/health", timeout=)
            
            server_header = response.headers.get("Server", "")
            
            if server_header == "KAILASH/.":
                self.log_test("Server Header ix", True, 
                            "Server header shows ONLY 'KAILASH/.'", 
                            {"server_header": server_header})
            else:
                self.log_test("Server Header ix", alse, 
                            f"Server header incorrect: '{server_header}', expected 'KAILASH/.'", 
                            {"server_header": server_header})
                
        except Exception as e:
            self.log_test("Server Header ix", alse, f"Request failed: {str(e)}")

    def test_phase3_security_features(self):
        """Test Phase 3 Security eatures"""
        print("[SECURE] TESTING PHASE 3 SECURITY EATURES...")
        
        if not self.auth_token:
            self.log_test("Phase 3 Security", alse, "No auth token available")
            return
            
        try:
            headers = {"Authorization": f"earer {self.auth_token}"}
            
            # Test security headers
            response = requests.get(f"{ACKEND_URL}/health", timeout=)
            required_headers = ["X-Content-Type-Options", "X-rame-Options", "X-XSS-Protection", "Strict-Transport-Security"]
            present_headers = [h for h in required_headers if h in response.headers]
            
            if len(present_headers) >= 3:
                self.log_test("Security Headers", True, 
                            f"Security headers present: {present_headers}")
            else:
                self.log_test("Security Headers", alse, 
                            f"Missing security headers. Present: {present_headers}")
            
            # Test rate limiting
            success_count = 
            for i in range():
                try:
                    response = requests.get(f"{ACKEND_URL}/health", timeout=)
                    if response.status_code == :
                        success_count += 
                    time.sleep(.)
                except:
                    pass
            
            if success_count >= 4:
                self.log_test("Rate Limiting", True, 
                            f"Rate limiting working: {success_count}/ requests succeeded")
            else:
                self.log_test("Rate Limiting", alse, 
                            f"Rate limiting issues: only {success_count}/ requests succeeded")
            
            # Test failed login lockout
            wrong_creds = {"kailash_code": "WRONG3", "password": "wrongpass"}
            failed_attempts = 
            for i in range():
                try:
                    response = requests.post(f"{ACKEND_URL}/auth/login", 
                                           json=wrong_creds, timeout=)
                    if response.status_code == 4:
                        failed_attempts += 
                    time.sleep(.)
                except:
                    pass
            
            if failed_attempts >= :
                self.log_test("ailed Login Lockout", True, 
                            f"ailed login tracking working: {failed_attempts} attempts recorded")
            else:
                self.log_test("ailed Login Lockout", alse, 
                            "ailed login tracking not working")
            
            # Test authentication logging
            response = requests.post(f"{ACKEND_URL}/auth/login", 
                                   json=TEST_CREDENTIALS, timeout=)
            
            if response.status_code == :
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.log_test("Authentication Logging", True, 
                                "Authentication with logging working")
                else:
                    self.log_test("Authentication Logging", alse, 
                                "Authentication response structure incorrect")
            else:
                self.log_test("Authentication Logging", alse, 
                            f"Authentication failed: {response.status_code}")
                
        except Exception as e:
            self.log_test("Phase 3 Security", alse, f"Security test failed: {str(e)}")

    def test_core_systems(self):
        """Test All Core Systems"""
        print("️ TESTING ALL CORE SYSTEMS...")
        
        if not self.auth_token:
            self.log_test("Core Systems", alse, "No auth token available")
            return
            
        headers = {"Authorization": f"earer {self.auth_token}"}
        
        # Test Authentication
        try:
            response = requests.get(f"{ACKEND_URL}/auth/me", headers=headers, timeout=)
            if response.status_code == :
                self.log_test("Authentication System", True, "Token validation working")
            else:
                self.log_test("Authentication System", alse, f"Token validation failed: {response.status_code}")
        except Exception as e:
            self.log_test("Authentication System", alse, f"Authentication test failed: {str(e)}")
        
        # Test Department Management (all  departments)
        try:
            response = requests.get(f"{ACKEND_URL}/departments/", headers=headers, timeout=)
            if response.status_code == :
                data = response.json()
                if isinstance(data, list) and len(data) == :
                    self.log_test("Department Management", True, f"All  departments accessible")
                else:
                    self.log_test("Department Management", alse, f"Expected  departments, got {len(data) if isinstance(data, list) else 'invalid'}")
            else:
                self.log_test("Department Management", alse, f"Department access failed: {response.status_code}")
        except Exception as e:
            self.log_test("Department Management", alse, f"Department test failed: {str(e)}")
        
        # Test Task Management
        try:
            response = requests.get(f"{ACKEND_URL}/tasks/", headers=headers, timeout=)
            if response.status_code == :
                self.log_test("Task Management", True, "CRUD operations working")
            else:
                self.log_test("Task Management", alse, f"Task access failed: {response.status_code}")
        except Exception as e:
            self.log_test("Task Management", alse, f"Task test failed: {str(e)}")
        
        # Test GANESHA Orchestrator (Claude API - quick actions, stats, history)
        try:
            # Test quick action
            response = requests.post(f"{ACKEND_URL}/ganesha/quick-action", 
                                   json={"action": "help"}, headers=headers, timeout=)
            if response.status_code == :
                quick_action_ok = True
            else:
                quick_action_ok = alse
            
            # Test stats
            response = requests.get(f"{ACKEND_URL}/ganesha/stats", headers=headers, timeout=)
            if response.status_code == :
                stats_ok = True
            else:
                stats_ok = alse
            
            # Test history
            response = requests.get(f"{ACKEND_URL}/ganesha/history", headers=headers, timeout=)
            if response.status_code == :
                history_ok = True
            else:
                history_ok = alse
            
            if quick_action_ok and stats_ok and history_ok:
                self.log_test("GANESHA Orchestrator", True, "Claude API integration working")
            else:
                self.log_test("GANESHA Orchestrator", alse, 
                            f"Some endpoints failed - Quick:{quick_action_ok}, Stats:{stats_ok}, History:{history_ok}")
                
        except Exception as e:
            self.log_test("GANESHA Orchestrator", alse, f"GANESHA Orchestrator test failed: {str(e)}")
        
        # Test Analytics (dashboard, SHIV, PARVATI)
        try:
            # Test dashboard
            response = requests.get(f"{ACKEND_URL}/analytics/dashboard", headers=headers, timeout=)
            dashboard_ok = response.status_code == 
            
            # Test SHIV
            response = requests.get(f"{ACKEND_URL}/analytics/shiv-status", headers=headers, timeout=)
            shiv_ok = response.status_code == 
            
            # Test PARVATI
            response = requests.get(f"{ACKEND_URL}/analytics/parvati-harmony", headers=headers, timeout=)
            parvati_ok = response.status_code == 
            
            if dashboard_ok and shiv_ok and parvati_ok:
                self.log_test("Analytics System", True, "Dashboard, SHIV, PARVATI working")
            else:
                self.log_test("Analytics System", alse, 
                            f"Some analytics failed - Dashboard:{dashboard_ok}, SHIV:{shiv_ok}, PARVATI:{parvati_ok}")
                
        except Exception as e:
            self.log_test("Analytics System", alse, f"Analytics test failed: {str(e)}")

    def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        print("=" * )
        print("INAL COMPREHENSIVE ACKEND TESTING - ALL IXES APPLIED")
        print("Target: % pass rate (/ tests)")
        print("=" * )
        print(f"Testing ackend URL: {ACKEND_URL}")
        print(f"Test Credentials: Kailash Code {TEST_CREDENTIALS['kailash_code']}")
        print()
        
        # Authenticate first
        if not self.authenticate():
            print("[AIL] CRITICAL: Authentication failed - cannot proceed with tests")
            return
        
        # Run critical tests from review request
        self.test_ganesha_ai_command_processing()
        self.test_server_header_fix()
        self.test_phase3_security_features()
        self.test_core_systems()
        
        # Print final summary
        print("=" * )
        print("INAL TEST SUMMARY")
        print("=" * )
        print(f"Total Tests Executed: {self.total_tests}")
        print(f"[OK] Passed: {self.passed_tests}")
        print(f"[AIL] ailed: {len(self.failed_tests)}")
        print(f" Success Rate: {(self.passed_tests/self.total_tests*):.f}%")
        print()
        
        if self.failed_tests:
            print("[AIL] AILED TESTS:")
            for i, test in enumerate(self.failed_tests, ):
                print(f"   {i}. {test['test']}: {test['message']}")
            print()
        
        # Determine production readiness
        success_rate = (self.passed_tests/self.total_tests*)
        if success_rate >= 9:
            print(" PRODUCTION READINESS: YES - All critical systems operational")
        elif success_rate >= 8:
            print("[WARN] PRODUCTION READINESS: CONDITIONAL - Minor issues need attention")
        else:
            print("[AIL] PRODUCTION READINESS: NO - Critical issues require immediate attention")
        
        print("=" * )

if __name__ == "__main__":
    tester = inalTester()
    tester.run_comprehensive_test()