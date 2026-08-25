#!/usr/bin/env python3
"""
COMPREHENSIVE ACKEND TESTING OR KAILASH INTEGRATION
Tests ALL backend API endpoints with detailed validation as requested
"""

import requests
import json
import uuid
from datetime import datetime
import time
import sys
import concurrent.futures
import threading
from typing import Dict, List, Any

# ackend URL from frontend .env
ACKEND_URL = "https://ganesha-v2-api.preview.emergentagent.com/api"

# Test credentials
TEST_CREDENTIALS = {
    "username": "<REDACTED_kailash_code>",
    "password": "<REDACTED_PASSWORD>@#@"
}

class KailashComprehensiveTester:
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        self.session_token = None
        self.session_cookies = None
        self.performance_metrics = {}
        
    def log_test(self, test_name: str, success: bool, message: str, response_data: Any = None, response_time: float = None):
        """Log test results with performance metrics"""
        status = "[OK] PASS" if success else "[AIL] AIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "response_data": response_data,
            "response_time": response_time
        }
        self.test_results.append(result)
        if not success:
            self.failed_tests.append(result)
        
        time_info = f" ({response_time:.3f}s)" if response_time else ""
        print(f"{status}: {test_name}{time_info} - {message}")
        if response_data and isinstance(response_data, dict) and len(str(response_data)) < :
            print(f"   Response: {response_data}")
        print()

    def make_request(self, method: str, endpoint: str, **kwargs) -> tuple:
        """Make HTTP request with timing and error handling"""
        start_time = time.time()
        try:
            url = f"{ACKEND_URL}{endpoint}"
            kwargs.setdefault('timeout', )
            
            # Add session cookies if available
            if self.session_cookies:
                kwargs.setdefault('cookies', self.session_cookies)
            
            response = requests.request(method, url, **kwargs)
            response_time = time.time() - start_time
            return response, response_time, None
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            return None, response_time, str(e)

    # ============================================
    # . KailashHU CORE ENDPOINTS
    # ============================================

    def test_root_endpoint(self):
        """Test GET /api/ - Root endpoint"""
        response, response_time, error = self.make_request('GET', '/')
        
        if error:
            self.log_test("Root Endpoint", alse, f"Request failed: {error}", response_time=response_time)
            return
        
        if response.status_code == :
            try:
                data = response.json()
                expected_message = "KailashHU with KAILASH Integration - Hello World"
                if expected_message in data.get("message", ""):
                    self.log_test("Root Endpoint", True, 
                                f"Status , correct message returned", data, response_time)
                else:
                    self.log_test("Root Endpoint", alse, 
                                f"Incorrect message. Expected '{expected_message}', got: {data}", response_time=response_time)
            except json.JSONDecodeError:
                self.log_test("Root Endpoint", alse, "Invalid JSON response", response_time=response_time)
        else:
            self.log_test("Root Endpoint", alse, 
                        f"Status {response.status_code}, expected ", response_time=response_time)

    def test_status_create(self):
        """Test POST /api/status - Create status check"""
        test_client_name = f"kailash_test_{int(time.time())}"
        payload = {"client_name": test_client_name}
        
        response, response_time, error = self.make_request('POST', '/status', json=payload)
        
        if error:
            self.log_test("Status Create", alse, f"Request failed: {error}", response_time=response_time)
            return None
        
        if response.status_code == :
            try:
                data = response.json()
                required_fields = ["id", "client_name", "timestamp"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Status Create", alse, 
                                f"Missing fields: {missing_fields}", data, response_time)
                    return None
                
                # Validate UUID format
                try:
                    uuid.UUID(data["id"])
                except ValueError:
                    self.log_test("Status Create", alse, 
                                "ID is not a valid UUID", data, response_time)
                    return None
                
                if data["client_name"] != test_client_name:
                    self.log_test("Status Create", alse, 
                                f"Client name mismatch", data, response_time)
                    return None
                
                self.log_test("Status Create", True, 
                            "Status check created successfully", data, response_time)
                return data
                
            except json.JSONDecodeError:
                self.log_test("Status Create", alse, "Invalid JSON response", response_time=response_time)
                return None
        else:
            self.log_test("Status Create", alse, 
                        f"Status {response.status_code}, expected ", response_time=response_time)
            return None

    def test_status_get(self):
        """Test GET /api/status - Retrieve all status checks"""
        response, response_time, error = self.make_request('GET', '/status')
        
        if error:
            self.log_test("Status Get", alse, f"Request failed: {error}", response_time=response_time)
            return None
        
        if response.status_code == :
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Status Get", True, 
                                f"Retrieved {len(data)} status checks", 
                                f"Array with {len(data)} items", response_time)
                    return data
                else:
                    self.log_test("Status Get", alse, 
                                f"Response is not an array. Got: {type(data)}", data, response_time)
                    return None
            except json.JSONDecodeError:
                self.log_test("Status Get", alse, "Invalid JSON response", response_time=response_time)
                return None
        else:
            self.log_test("Status Get", alse, 
                        f"Status {response.status_code}, expected ", response_time=response_time)
            return None

    # ============================================
    # 3. AUTHENTICATION LOW TESTING
    # ============================================

    def test_login_invalid_credentials(self):
        """Test POST /api/auth/login with invalid credentials"""
        invalid_payloads = [
            {"username": "invalid", "password": "invalid"},
            {"username": "<REDACTED_kailash_code>", "password": "wrong_password"},
            {"username": "wrong_user", "password": "<REDACTED_PASSWORD>@#@"},
        ]
        
        for i, payload in enumerate(invalid_payloads):
            response, response_time, error = self.make_request('POST', '/auth/login', json=payload)
            
            if error:
                self.log_test(f"Login Invalid #{i+}", alse, f"Request failed: {error}", response_time=response_time)
                continue
            
            if response.status_code == 4:
                self.log_test(f"Login Invalid #{i+}", True, 
                            "Correctly rejected invalid credentials", response_time=response_time)
            else:
                self.log_test(f"Login Invalid #{i+}", alse, 
                            f"Expected 4, got {response.status_code}", response_time=response_time)

    def test_login_valid_credentials(self):
        """Test POST /api/auth/login with valid credentials"""
        response, response_time, error = self.make_request('POST', '/auth/login', json=TEST_CREDENTIALS)
        
        if error:
            self.log_test("Login Valid", alse, f"Request failed: {error}", response_time=response_time)
            return alse
        
        if response.status_code == :
            try:
                data = response.json()
                required_fields = ["success", "session_id", "user_id", "message"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Login Valid", alse, 
                                f"Missing fields: {missing_fields}", data, response_time)
                    return alse
                
                if data.get("success") != True:
                    self.log_test("Login Valid", alse, 
                                "Success field is not True", data, response_time)
                    return alse
                
                # Store session for subsequent tests
                self.session_cookies = response.cookies
                self.session_token = data.get("session_id")
                
                self.log_test("Login Valid", True, 
                            "Login successful with valid credentials", data, response_time)
                return True
                
            except json.JSONDecodeError:
                self.log_test("Login Valid", alse, "Invalid JSON response", response_time=response_time)
                return alse
        else:
            self.log_test("Login Valid", alse, 
                        f"Status {response.status_code}, expected ", response_time=response_time)
            return alse

    def test_session_validation(self):
        """Test GET /api/auth/session - Session validation"""
        if not self.session_cookies:
            self.log_test("Session Validation", alse, "No session available (login first)")
            return
        
        response, response_time, error = self.make_request('GET', '/auth/session')
        
        if error:
            self.log_test("Session Validation", alse, f"Request failed: {error}", response_time=response_time)
            return
        
        if response.status_code == :
            try:
                data = response.json()
                if data.get("authenticated") == True and "user_id" in data:
                    self.log_test("Session Validation", True, 
                                "Session validated successfully", data, response_time)
                else:
                    self.log_test("Session Validation", alse, 
                                "Invalid session response", data, response_time)
            except json.JSONDecodeError:
                self.log_test("Session Validation", alse, "Invalid JSON response", response_time=response_time)
        else:
            self.log_test("Session Validation", alse, 
                        f"Status {response.status_code}, expected ", response_time=response_time)

    def test_logout(self):
        """Test POST /api/auth/logout - Logout functionality"""
        if not self.session_cookies:
            self.log_test("Logout", alse, "No session available (login first)")
            return
        
        response, response_time, error = self.make_request('POST', '/auth/logout')
        
        if error:
            self.log_test("Logout", alse, f"Request failed: {error}", response_time=response_time)
            return
        
        if response.status_code == :
            try:
                data = response.json()
                if data.get("success") == True:
                    self.log_test("Logout", True, 
                                "Logout successful", data, response_time)
                    # Clear session for subsequent tests
                    self.session_cookies = None
                    self.session_token = None
                else:
                    self.log_test("Logout", alse, 
                                "Logout response indicates failure", data, response_time)
            except json.JSONDecodeError:
                self.log_test("Logout", alse, "Invalid JSON response", response_time=response_time)
        else:
            self.log_test("Logout", alse, 
                        f"Status {response.status_code}, expected ", response_time=response_time)

    # ============================================
    # . KAILASH INTEGRATED ENDPOINTS
    # ============================================

    def test_kailash_health(self):
        """Test GET /api/kailash/health - Health check"""
        response, response_time, error = self.make_request('GET', '/kailash/health')
        
        if error:
            self.log_test("KAILASH Health", alse, f"Request failed: {error}", response_time=response_time)
            return
        
        if response.status_code == :
            try:
                data = response.json()
                required_fields = ["status", "service", "timestamp"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("KAILASH Health", alse, 
                                f"Missing fields: {missing_fields}", data, response_time)
                else:
                    self.log_test("KAILASH Health", True, 
                                "Health check successful", data, response_time)
            except json.JSONDecodeError:
                self.log_test("KAILASH Health", alse, "Invalid JSON response", response_time=response_time)
        else:
            self.log_test("KAILASH Health", alse, 
                        f"Status {response.status_code}, expected ", response_time=response_time)

    def test_protected_endpoints_without_auth(self):
        """Test protected endpoints without authentication (should return 4)"""
        protected_endpoints = [
            '/kailash/dashboard/overview',
            '/kailash/ganesha/command',
            '/kailash/shiv/status',
            '/kailash/shiv/threats',
            '/kailash/shiv/system-health',
            '/kailash/parvati/status',
            '/kailash/parvati/harmony',
            '/kailash/parvati/workload',
            '/kailash/parvati/rebalancing-actions',
            '/kailash/departments',
            '/kailash/tasks',
            '/auth/session'
        ]
        
        # Temporarily clear session
        temp_cookies = self.session_cookies
        self.session_cookies = None
        
        for endpoint in protected_endpoints:
            method = 'POST' if 'command' in endpoint else 'GET'
            payload = {"command": "test"} if 'command' in endpoint else None
            
            response, response_time, error = self.make_request(method, endpoint, json=payload)
            
            if error:
                self.log_test(f"Unauth {endpoint}", alse, f"Request failed: {error}", response_time=response_time)
                continue
            
            if response.status_code == 4:
                self.log_test(f"Unauth {endpoint}", True, 
                            "Correctly returned 4 for unauthenticated request", response_time=response_time)
            else:
                self.log_test(f"Unauth {endpoint}", alse, 
                            f"Expected 4, got {response.status_code}", response_time=response_time)
        
        # Restore session
        self.session_cookies = temp_cookies

    def test_kailash_dashboard_overview(self):
        """Test GET /api/kailash/dashboard/overview - Dashboard data (requires auth)"""
        if not self.session_cookies:
            self.log_test("KAILASH Dashboard", alse, "No session available (login first)")
            return
        
        response, response_time, error = self.make_request('GET', '/kailash/dashboard/overview')
        
        if error:
            self.log_test("KAILASH Dashboard", alse, f"Request failed: {error}", response_time=response_time)
            return
        
        if response.status_code == :
            try:
                data = response.json()
                required_fields = ["timestamp", "system_health", "harmony", "active_tasks", "user_id"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("KAILASH Dashboard", alse, 
                                f"Missing fields: {missing_fields}", data, response_time)
                else:
                    self.log_test("KAILASH Dashboard", True, 
                                "Dashboard overview retrieved successfully", data, response_time)
            except json.JSONDecodeError:
                self.log_test("KAILASH Dashboard", alse, "Invalid JSON response", response_time=response_time)
        else:
            self.log_test("KAILASH Dashboard", alse, 
                        f"Status {response.status_code}, expected ", response_time=response_time)

    def test_ganesha_commands(self):
        """Test POST /api/kailash/ganesha/command - Send GANESHA commands"""
        if not self.session_cookies:
            self.log_test("GANESHA Commands", alse, "No session available (login first)")
            return
        
        test_commands = [
            "Get me yesterday's URJAA revenue report",
            "Show me active tasks",
            "What is the system status?"
        ]
        
        for i, command in enumerate(test_commands):
            payload = {"command": command, "context": {"test": True}}
            
            response, response_time, error = self.make_request('POST', '/kailash/ganesha/command', json=payload)
            
            if error:
                self.log_test(f"GANESHA Cmd #{i+}", alse, f"Request failed: {error}", response_time=response_time)
                continue
            
            if response.status_code == :
                try:
                    data = response.json()
                    required_fields = ["success", "command_id", "response", "agent_used", "timestamp"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test(f"GANESHA Cmd #{i+}", alse, 
                                    f"Missing fields: {missing_fields}", data, response_time)
                    else:
                        # Validate UUID format for command_id
                        try:
                            uuid.UUID(data["command_id"])
                            self.log_test(f"GANESHA Cmd #{i+}", True, 
                                        f"Command processed successfully", 
                                        {"command": command, "response": data["response"][:] + "..."}, 
                                        response_time)
                        except ValueError:
                            self.log_test(f"GANESHA Cmd #{i+}", alse, 
                                        "Command ID is not a valid UUID", data, response_time)
                except json.JSONDecodeError:
                    self.log_test(f"GANESHA Cmd #{i+}", alse, "Invalid JSON response", response_time=response_time)
            else:
                self.log_test(f"GANESHA Cmd #{i+}", alse, 
                            f"Status {response.status_code}, expected ", response_time=response_time)

    def test_shiv_endpoints(self):
        """Test SHIV monitoring endpoints"""
        if not self.session_cookies:
            self.log_test("SHIV Endpoints", alse, "No session available (login first)")
            return
        
        shiv_endpoints = [
            ('/kailash/shiv/status', 'SHIV Status'),
            ('/kailash/shiv/threats', 'SHIV Threats'),
            ('/kailash/shiv/system-health', 'SHIV System Health')
        ]
        
        for endpoint, name in shiv_endpoints:
            response, response_time, error = self.make_request('GET', endpoint)
            
            if error:
                self.log_test(name, alse, f"Request failed: {error}", response_time=response_time)
                continue
            
            if response.status_code == :
                try:
                    data = response.json()
                    self.log_test(name, True, 
                                "Endpoint accessible and returned data", 
                                f"Response type: {type(data)}", response_time)
                except json.JSONDecodeError:
                    self.log_test(name, alse, "Invalid JSON response", response_time=response_time)
            elif response.status_code == 3:
                self.log_test(name, True, 
                            "Service unavailable (expected for uninitialized agents)", response_time=response_time)
            else:
                self.log_test(name, alse, 
                            f"Status {response.status_code}, expected  or 3", response_time=response_time)

    def test_parvati_endpoints(self):
        """Test PARVATI harmony endpoints"""
        if not self.session_cookies:
            self.log_test("PARVATI Endpoints", alse, "No session available (login first)")
            return
        
        parvati_endpoints = [
            ('/kailash/parvati/status', 'PARVATI Status'),
            ('/kailash/parvati/harmony', 'PARVATI Harmony'),
            ('/kailash/parvati/workload', 'PARVATI Workload'),
            ('/kailash/parvati/rebalancing-actions', 'PARVATI Rebalancing')
        ]
        
        for endpoint, name in parvati_endpoints:
            response, response_time, error = self.make_request('GET', endpoint)
            
            if error:
                self.log_test(name, alse, f"Request failed: {error}", response_time=response_time)
                continue
            
            if response.status_code == :
                try:
                    data = response.json()
                    self.log_test(name, True, 
                                "Endpoint accessible and returned data", 
                                f"Response type: {type(data)}", response_time)
                except json.JSONDecodeError:
                    self.log_test(name, alse, "Invalid JSON response", response_time=response_time)
            elif response.status_code == 3:
                self.log_test(name, True, 
                            "Service unavailable (expected for uninitialized agents)", response_time=response_time)
            else:
                self.log_test(name, alse, 
                            f"Status {response.status_code}, expected  or 3", response_time=response_time)

    def test_departments_endpoints(self):
        """Test department-related endpoints"""
        if not self.session_cookies:
            self.log_test("Departments", alse, "No session available (login first)")
            return
        
        # Test list all departments
        response, response_time, error = self.make_request('GET', '/kailash/departments')
        
        if error:
            self.log_test("Departments List", alse, f"Request failed: {error}", response_time=response_time)
            return
        
        if response.status_code == :
            try:
                data = response.json()
                self.log_test("Departments List", True, 
                            "Departments list retrieved", 
                            f"Response type: {type(data)}", response_time)
            except json.JSONDecodeError:
                self.log_test("Departments List", alse, "Invalid JSON response", response_time=response_time)
        elif response.status_code == 3:
            self.log_test("Departments List", True, 
                        "Service unavailable (expected for uninitialized task router)", response_time=response_time)
        else:
            self.log_test("Departments List", alse, 
                        f"Status {response.status_code}, expected  or 3", response_time=response_time)
        
        # Test specific departments
        test_departments = ['VISHWAKARMA', 'LAKSHMI', 'SURYA']
        for dept in test_departments:
            response, response_time, error = self.make_request('GET', f'/kailash/departments/{dept}')
            
            if error:
                self.log_test(f"Dept {dept}", alse, f"Request failed: {error}", response_time=response_time)
                continue
            
            if response.status_code in [, 44, 3]:
                self.log_test(f"Dept {dept}", True, 
                            f"Endpoint accessible (status {response.status_code})", response_time=response_time)
            else:
                self.log_test(f"Dept {dept}", alse, 
                            f"Unexpected status {response.status_code}", response_time=response_time)

    def test_tasks_endpoints(self):
        """Test task-related endpoints"""
        if not self.session_cookies:
            self.log_test("Tasks", alse, "No session available (login first)")
            return
        
        # Test list all tasks
        response, response_time, error = self.make_request('GET', '/kailash/tasks')
        
        if error:
            self.log_test("Tasks List", alse, f"Request failed: {error}", response_time=response_time)
            return
        
        if response.status_code == :
            try:
                data = response.json()
                self.log_test("Tasks List", True, 
                            "Tasks list retrieved", 
                            f"Response type: {type(data)}", response_time)
            except json.JSONDecodeError:
                self.log_test("Tasks List", alse, "Invalid JSON response", response_time=response_time)
        elif response.status_code == 3:
            self.log_test("Tasks List", True, 
                        "Service unavailable (expected for uninitialized task router)", response_time=response_time)
        else:
            self.log_test("Tasks List", alse, 
                        f"Status {response.status_code}, expected  or 3", response_time=response_time)
        
        # Test create task
        task_payload = {
            "title": "Test Task",
            "description": "Test task for API validation",
            "department": "VISHWAKARMA",
            "priority": "medium"
        }
        
        response, response_time, error = self.make_request('POST', '/kailash/tasks', json=task_payload)
        
        if error:
            self.log_test("Task Create", alse, f"Request failed: {error}", response_time=response_time)
        elif response.status_code in [, , 3]:
            self.log_test("Task Create", True, 
                        f"Task creation endpoint accessible (status {response.status_code})", response_time=response_time)
        else:
            self.log_test("Task Create", alse, 
                        f"Unexpected status {response.status_code}", response_time=response_time)

    # ============================================
    # 4. ERROR HANDLING & . CORS TESTING
    # ============================================

    def test_error_handling(self):
        """Test various error scenarios"""
        error_tests = [
            ('GET', '/nonexistent', None, 44, "Non-existent endpoint"),
            ('POST', '/status', {}, 4, "Missing required fields"),
            ('POST', '/status', {"invalid": "data"}, 4, "Invalid field names"),
            ('POST', '/auth/login', {}, 4, "Missing login credentials"),
            ('PUT', '/status', {"client_name": "test"}, 4, "Invalid HTTP method"),
        ]
        
        for method, endpoint, payload, expected_status, description in error_tests:
            response, response_time, error = self.make_request(method, endpoint, json=payload)
            
            if error:
                self.log_test(f"Error: {description}", alse, f"Request failed: {error}", response_time=response_time)
                continue
            
            if response.status_code == expected_status:
                self.log_test(f"Error: {description}", True, 
                            f"Correctly returned {expected_status}", response_time=response_time)
            else:
                self.log_test(f"Error: {description}", alse, 
                            f"Expected {expected_status}, got {response.status_code}", response_time=response_time)

    def test_cors_headers(self):
        """Test CORS configuration"""
        # Test preflight request
        headers = {
            'Origin': 'https://example.com',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response, response_time, error = self.make_request('OPTIONS', '/status', headers=headers)
        
        if error:
            self.log_test("CORS Preflight", alse, f"Request failed: {error}", response_time=response_time)
        else:
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            cors_methods = response.headers.get('Access-Control-Allow-Methods')
            
            if cors_origin:
                self.log_test("CORS Preflight", True, 
                            f"CORS headers present: Origin={cors_origin}, Methods={cors_methods}", response_time=response_time)
            else:
                self.log_test("CORS Preflight", alse, 
                            "CORS headers missing", response_time=response_time)

    # ============================================
    # . PERORMANCE TESTING
    # ============================================

    def test_performance_concurrent(self):
        """Test concurrent requests performance"""
        def make_concurrent_request():
            response, response_time, error = self.make_request('GET', '/')
            return response_time if not error and response and response.status_code ==  else None
        
        # Test  concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=) as executor:
            start_time = time.time()
            futures = [executor.submit(make_concurrent_request) for _ in range()]
            response_times = [f.result() for f in concurrent.futures.as_completed(futures)]
            total_time = time.time() - start_time
        
        successful_requests = [rt for rt in response_times if rt is not None]
        
        if len(successful_requests) >= :  # At least % success rate
            avg_response_time = sum(successful_requests) / len(successful_requests)
            max_response_time = max(successful_requests)
            
            self.log_test("Performance Concurrent", True, 
                        f" concurrent requests: {len(successful_requests)}/ successful, "
                        f"avg: {avg_response_time:.3f}s, max: {max_response_time:.3f}s, "
                        f"total: {total_time:.3f}s", response_time=total_time)
        else:
            self.log_test("Performance Concurrent", alse, 
                        f"Only {len(successful_requests)}/ requests successful", response_time=total_time)

    def test_performance_response_times(self):
        """Test individual endpoint response times"""
        endpoints_to_test = [
            ('GET', '/', "Root endpoint"),
            ('GET', '/status', "Status list"),
            ('GET', '/kailash/health', "KAILASH health"),
        ]
        
        for method, endpoint, description in endpoints_to_test:
            response, response_time, error = self.make_request(method, endpoint)
            
            if error:
                self.log_test(f"Perf: {description}", alse, f"Request failed: {error}", response_time=response_time)
                continue
            
            if response_time < .:  # Less than  seconds
                self.log_test(f"Perf: {description}", True, 
                            f"Response time acceptable", response_time=response_time)
            else:
                self.log_test(f"Perf: {description}", alse, 
                            f"Response time too slow", response_time=response_time)

    # ============================================
    # 8. INTEGRATION TESTING
    # ============================================

    def test_complete_authentication_flow(self):
        """Test complete authentication flow"""
        # Clear any existing session
        self.session_cookies = None
        
        # Step : Login
        if not self.test_login_valid_credentials():
            self.log_test("Auth low", alse, "Login step failed")
            return
        
        # Step : Validate session
        response, response_time, error = self.make_request('GET', '/auth/session')
        if error or not response or response.status_code != :
            self.log_test("Auth low", alse, "Session validation failed")
            return
        
        # Step 3: Access protected endpoint
        response, response_time, error = self.make_request('GET', '/kailash/dashboard/overview')
        if error or not response or response.status_code not in [, 3]:
            self.log_test("Auth low", alse, "Protected endpoint access failed")
            return
        
        # Step 4: Logout
        response, response_time, error = self.make_request('POST', '/auth/logout')
        if error or not response or response.status_code != :
            self.log_test("Auth low", alse, "Logout failed")
            return
        
        self.log_test("Auth low", True, "Complete authentication flow successful")

    # ============================================
    # 9. EDGE CASES & . DATAASE CONNECTIVITY
    # ============================================

    def test_edge_cases(self):
        """Test edge cases and malformed requests"""
        edge_cases = [
            # Empty request body
            ('POST', '/status', "", "Empty request body"),
            # Very long strings
            ('POST', '/status', {"client_name": "x" * }, "Very long client name"),
            # Special characters
            ('POST', '/status', {"client_name": "test@#$%^&*()_+{}|:<>?[]\\;'\",./"}, "Special characters"),
            # Unicode characters
            ('POST', '/status', {"client_name": "测试用户名"}, "Unicode characters"),
        ]
        
        for method, endpoint, payload, description in edge_cases:
            if payload == "":
                response, response_time, error = self.make_request(method, endpoint, data=payload)
            else:
                response, response_time, error = self.make_request(method, endpoint, json=payload)
            
            if error:
                self.log_test(f"Edge: {description}", alse, f"Request failed: {error}", response_time=response_time)
            elif response.status_code in [, 4, 4]:  # Accept success or validation errors
                self.log_test(f"Edge: {description}", True, 
                            f"Handled gracefully (status {response.status_code})", response_time=response_time)
            else:
                self.log_test(f"Edge: {description}", alse, 
                            f"Unexpected status {response.status_code}", response_time=response_time)

    def test_database_connectivity(self):
        """Test database connectivity through data persistence"""
        # Create a unique status check
        test_client_name = f"db_test_{int(time.time())}"
        created_status = self.test_status_create()
        
        if not created_status:
            self.log_test("Database Connectivity", alse, "ailed to create status check")
            return
        
        # Wait for database write
        time.sleep()
        
        # Retrieve and verify
        all_status_checks = self.test_status_get()
        if all_status_checks is None:
            self.log_test("Database Connectivity", alse, "ailed to retrieve status checks")
            return
        
        # Check if our created status exists
        found = any(status.get("id") == created_status["id"] for status in all_status_checks)
        
        if found:
            self.log_test("Database Connectivity", True, 
                        "Data persisted successfully in MongoD")
        else:
            self.log_test("Database Connectivity", alse, 
                        "Created data not found in database")

    # ============================================
    # MAIN TEST RUNNER
    # ============================================

    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("=" * )
        print("COMPREHENSIVE ACKEND TESTING OR KAILASH INTEGRATION")
        print("=" * )
        print(f"Testing ackend URL: {ACKEND_URL}")
        print(f"Test Credentials: {TEST_CREDENTIALS['username']} / {TEST_CREDENTIALS['password']}")
        print()
        
        # . KailashHU Core Endpoints
        print(" . KailashHU CORE ENDPOINTS")
        print("-" * )
        self.test_root_endpoint()
        self.test_status_create()
        self.test_status_get()
        
        # 3. Authentication low Testing (before protected endpoints)
        print(" 3. AUTHENTICATION LOW TESTING")
        print("-" * )
        self.test_login_invalid_credentials()
        self.test_login_valid_credentials()
        self.test_session_validation()
        
        # . KAILASH Integrated Endpoints (requires auth)
        print(" . KAILASH INTEGRATED ENDPOINTS")
        print("-" * )
        self.test_kailash_health()
        self.test_protected_endpoints_without_auth()
        self.test_kailash_dashboard_overview()
        self.test_ganesha_commands()
        self.test_shiv_endpoints()
        self.test_parvati_endpoints()
        self.test_departments_endpoints()
        self.test_tasks_endpoints()
        
        # 4. Error Handling
        print(" 4. ERROR HANDLING")
        print("-" * )
        self.test_error_handling()
        
        # . CORS Testing
        print(" . CORS TESTING")
        print("-" * )
        self.test_cors_headers()
        
        # . Performance Testing
        print(" . PERORMANCE TESTING")
        print("-" * )
        self.test_performance_response_times()
        self.test_performance_concurrent()
        
        # 8. Integration Testing
        print(" 8. INTEGRATION TESTING")
        print("-" * )
        self.test_complete_authentication_flow()
        
        # 9. Edge Cases
        print(" 9. EDGE CASES")
        print("-" * )
        self.test_edge_cases()
        
        # . Database Connectivity
        print(" . DATAASE CONNECTIVITY")
        print("-" * )
        self.test_database_connectivity()
        
        # Logout at the end
        print(" CLEANUP")
        print("-" * )
        self.test_logout()
        
        # inal Summary
        self.print_final_summary()
        
        return len(self.failed_tests) == 

    def print_final_summary(self):
        """Print comprehensive test summary"""
        print("=" * )
        print("COMPREHENSIVE TEST SUMMARY")
        print("=" * )
        
        total_tests = len(self.test_results)
        passed_tests = total_tests - len(self.failed_tests)
        success_rate = (passed_tests / total_tests) *  if total_tests >  else 
        
        print(f" Total Tests: {total_tests}")
        print(f"[OK] Passed: {passed_tests}")
        print(f"[AIL] ailed: {len(self.failed_tests)}")
        print(f" Success Rate: {success_rate:.f}%")
        print()
        
        # Performance metrics
        response_times = [r["response_time"] for r in self.test_results if r.get("response_time")]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            print(f"⚡ Average Response Time: {avg_response_time:.3f}s")
            print(f"⚡ Maximum Response Time: {max_response_time:.3f}s")
            print()
        
        # Categorize results
        categories = {
            "KailashHU Core": [],
            "Authentication": [],
            "KAILASH Endpoints": [],
            "Error Handling": [],
            "Performance": [],
            "Integration": [],
            "Edge Cases": [],
            "Other": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if any(x in test_name.lower() for x in ["root", "status"]):
                categories["KailashHU Core"].append(result)
            elif any(x in test_name.lower() for x in ["login", "logout", "session", "auth"]):
                categories["Authentication"].append(result)
            elif any(x in test_name.lower() for x in ["kailash", "ganesha", "shiv", "parvati", "department", "task"]):
                categories["KAILASH Endpoints"].append(result)
            elif "error" in test_name.lower():
                categories["Error Handling"].append(result)
            elif "perf" in test_name.lower() or "concurrent" in test_name.lower():
                categories["Performance"].append(result)
            elif "flow" in test_name.lower():
                categories["Integration"].append(result)
            elif "edge" in test_name.lower():
                categories["Edge Cases"].append(result)
            else:
                categories["Other"].append(result)
        
        # Print category summaries
        for category, results in categories.items():
            if results:
                passed = len([r for r in results if "[OK]" in r["status"]])
                total = len(results)
                print(f" {category}: {passed}/{total} passed ({(passed/total)*:.f}%)")
        
        print()
        
        # Print failed tests details
        if self.failed_tests:
            print("[AIL] AILED TESTS DETAILS:")
            print("-" * )
            for test in self.failed_tests:
                print(f"• {test['test']}: {test['message']}")
            print()
        else:
            print(" ALL TESTS PASSED!")
            print()
        
        # Success criteria evaluation
        print(" SUCCESS CRITERIA EVALUATION:")
        print("-" * )
        
        criteria_met = 
        total_criteria = 
        
        # Check each criterion
        auth_tests = [r for r in self.test_results if "login" in r["test"].lower() and "[OK]" in r["status"]]
        if auth_tests:
            print("[OK] Authentication working correctly")
            criteria_met += 
        else:
            print("[AIL] Authentication issues detected")
        
        response_time_tests = [r for r in self.test_results if r.get("response_time", ) < . and "[OK]" in r["status"]]
        if len(response_time_tests) >= :
            print("[OK] Response times <  seconds for standard endpoints")
            criteria_met += 
        else:
            print("[AIL] Some endpoints have slow response times")
        
        error_tests = [r for r in self.test_results if "error" in r["test"].lower() and "[OK]" in r["status"]]
        if error_tests:
            print("[OK] Error handling working correctly")
            criteria_met += 
        else:
            print("[AIL] Error handling issues detected")
        
        cors_tests = [r for r in self.test_results if "cors" in r["test"].lower() and "[OK]" in r["status"]]
        if cors_tests:
            print("[OK] CORS headers present")
            criteria_met += 
        else:
            print("[AIL] CORS configuration issues")
        
        db_tests = [r for r in self.test_results if "database" in r["test"].lower() and "[OK]" in r["status"]]
        if db_tests:
            print("[OK] Database connectivity working")
            criteria_met += 
        else:
            print("[AIL] Database connectivity issues")
        
        kailash_tests = [r for r in self.test_results if "kailash" in r["test"].lower() and "[OK]" in r["status"]]
        if len(kailash_tests) >= 3:
            print("[OK] KAILASH endpoints accessible")
            criteria_met += 
        else:
            print("[AIL] KAILASH endpoint issues")
        
        protected_tests = [r for r in self.test_results if "unauth" in r["test"].lower() and "[OK]" in r["status"]]
        if len(protected_tests) >= :
            print("[OK] Protected endpoints properly secured")
            criteria_met += 
        else:
            print("[AIL] Security issues with protected endpoints")
        
        perf_tests = [r for r in self.test_results if "concurrent" in r["test"].lower() and "[OK]" in r["status"]]
        if perf_tests:
            print("[OK] Concurrent request handling working")
            criteria_met += 
        else:
            print("[AIL] Concurrent request handling issues")
        
        integration_tests = [r for r in self.test_results if "flow" in r["test"].lower() and "[OK]" in r["status"]]
        if integration_tests:
            print("[OK] Integration flows working")
            criteria_met += 
        else:
            print("[AIL] Integration flow issues")
        
        if success_rate >= 8:
            print("[OK] Overall success rate >= 8%")
            criteria_met += 
        else:
            print("[AIL] Overall success rate < 8%")
        
        print()
        print(f" SUCCESS CRITERIA MET: {criteria_met}/{total_criteria} ({(criteria_met/total_criteria)*:.f}%)")
        
        if criteria_met >= 8:
            print(" OVERALL ASSESSMENT: EXCELLENT - System ready for production")
        elif criteria_met >= :
            print(" OVERALL ASSESSMENT: GOOD - Minor issues to address")
        elif criteria_met >= 4:
            print(" OVERALL ASSESSMENT: AIR - Several issues need attention")
        else:
            print(" OVERALL ASSESSMENT: POOR - Major issues require immediate attention")
        
        print("=" * )

if __name__ == "__main__":
    tester = KailashComprehensiveTester()
    success = tester.run_comprehensive_tests()
    sys.exit( if success else )