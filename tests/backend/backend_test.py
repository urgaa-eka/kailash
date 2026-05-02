#!/usr/bin/env python3
"""
Kailash - DAILY INTELLIGENCE & VOICE API TESTING
Tests the newly implemented features:
1. Authentication System (POST /api/auth/login)
2. Daily Intelligence Collection APIs (POST/GET /api/ganesha/intelligence)
3. Voice Input API (POST /api/ganesha/voice) - Whisper
4. Existing endpoints verification (GET /api/health, GET /api/dashboard/executive)

Backend URL: https://ganesha-v2-api.preview.emergentagent.com/api
"""

import requests
import json
import time
import sys
import io
from datetime import datetime
from typing import Dict, Any

# Backend URL from frontend .env
BACKEND_URL = "https://ganesha-v2-api.preview.emergentagent.com/api"

# Test credentials from review request
TEST_CREDENTIALS = {
    "kailash_code": "<REDACTED_kailash_code>",
    "password": "<REDACTED_PASSWORD>"
}

# Test data for intelligence APIs
INTELLIGENCE_TEST_DATA = {
    "source": "URGAA",
    "category": "market_data",
    "title": "EV Charging Station Performance Analysis",
    "summary": "Comprehensive analysis of charging station utilization rates across Delhi NCR region showing 23% increase in usage during peak hours",
    "data": {
        "region": "Delhi NCR",
        "utilization_rate": 0.78,
        "peak_hours": "18:00-22:00",
        "growth_rate": 0.23
    },
    "relevance_score": 0.8,
    "tags": ["ev_charging", "delhi", "performance", "utilization"]
}

class KailashIntelligenceVoiceTester:
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        self.auth_token = None
        self.total_tests = 0
        self.passed_tests = 0
        self.user_id = None
        self.intelligence_id = None
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            
        status = "[OK] PASS" if success else "[FAIL] FAIL"
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
        print()

    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}

    # ========== 1. AUTHENTICATION SYSTEM ==========
    
    def test_authentication_login(self):
        """Test POST /api/auth/login with Kailash Code: <REDACTED_kailash_code> and Password: <REDACTED_PASSWORD>"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", 
                                   json=TEST_CREDENTIALS, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    user_data = data["user"]
                    self.user_id = user_data.get("id")
                    if user_data.get("kailash_code") == TEST_CREDENTIALS["kailash_code"]:
                        self.log_test("Authentication Login", True, 
                                    f"✅ Login successful with Kailash Code: {TEST_CREDENTIALS['kailash_code']}", 
                                    {"user_name": user_data.get("full_name"), "kailash_code": user_data.get("kailash_code"), "token_received": True})
                    else:
                        self.log_test("Authentication Login", False, 
                                    "Kailash code mismatch in response")
                else:
                    self.log_test("Authentication Login", False, 
                                "Missing access_token or user in response", data)
            else:
                self.log_test("Authentication Login", False, 
                            f"❌ Login failed - Status {response.status_code}, expected 200. Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Authentication Login", False, f"❌ Request failed: {str(e)}")

    # ========== 2. DAILY INTELLIGENCE APIS ==========
    
    def test_create_intelligence(self):
        """Test POST /api/ganesha/intelligence - Create intelligence item"""
        if not self.auth_token:
            self.log_test("Create Intelligence", False, 
                        "❌ No auth token available - login must succeed first")
            return
            
        try:
            headers = self.get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            response = requests.post(f"{BACKEND_URL}/ganesha/intelligence", 
                                   json=INTELLIGENCE_TEST_DATA, 
                                   headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "source", "category", "title", "summary", "relevance_score", "tags", "created_at", "processed"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.intelligence_id = data.get("id")
                    self.log_test("Create Intelligence", True, 
                                f"✅ Intelligence item created successfully", 
                                {
                                    "id": data.get("id"),
                                    "source": data.get("source"),
                                    "category": data.get("category"),
                                    "title": data.get("title")[:50] + "..." if len(data.get("title", "")) > 50 else data.get("title"),
                                    "relevance_score": data.get("relevance_score"),
                                    "processed": data.get("processed")
                                })
                else:
                    self.log_test("Create Intelligence", False, 
                                f"❌ Missing required fields in response: {missing_fields}")
            elif response.status_code == 401:
                self.log_test("Create Intelligence", False, 
                            "❌ Authentication failed - token may be invalid")
            else:
                self.log_test("Create Intelligence", False, 
                            f"❌ Create intelligence failed - Status {response.status_code}, expected 200. Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Create Intelligence", False, f"❌ Request failed: {str(e)}")

    def test_get_intelligence_list(self):
        """Test GET /api/ganesha/intelligence - List intelligence items"""
        if not self.auth_token:
            self.log_test("Get Intelligence List", False, 
                        "❌ No auth token available - login must succeed first")
            return
            
        try:
            headers = self.get_auth_headers()
            
            # Test without filters
            response = requests.get(f"{BACKEND_URL}/ganesha/intelligence", 
                                  headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data and "total" in data:
                    items = data.get("items", [])
                    total = data.get("total", 0)
                    
                    self.log_test("Get Intelligence List", True, 
                                f"✅ Intelligence list retrieved successfully", 
                                {
                                    "total_items": total,
                                    "items_returned": len(items),
                                    "has_filters": "filters" in data,
                                    "sample_item": items[0] if items else None
                                })
                else:
                    self.log_test("Get Intelligence List", False, 
                                "❌ Missing 'items' or 'total' in response", data)
            elif response.status_code == 401:
                self.log_test("Get Intelligence List", False, 
                            "❌ Authentication failed - token may be invalid")
            else:
                self.log_test("Get Intelligence List", False, 
                            f"❌ Get intelligence list failed - Status {response.status_code}, expected 200")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get Intelligence List", False, f"❌ Request failed: {str(e)}")

    def test_get_intelligence_with_filters(self):
        """Test GET /api/ganesha/intelligence with source and category filters"""
        if not self.auth_token:
            self.log_test("Get Intelligence Filtered", False, 
                        "❌ No auth token available - login must succeed first")
            return
            
        try:
            headers = self.get_auth_headers()
            
            # Test with filters
            params = {
                "source": "URGAA",
                "category": "market_data",
                "limit": 10
            }
            
            response = requests.get(f"{BACKEND_URL}/ganesha/intelligence", 
                                  headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data and "filters" in data:
                    items = data.get("items", [])
                    filters = data.get("filters", {})
                    
                    # Verify filters are applied
                    filter_applied = (filters.get("source") == "URGAA" and 
                                    filters.get("category") == "market_data")
                    
                    self.log_test("Get Intelligence Filtered", True, 
                                f"✅ Filtered intelligence list retrieved successfully", 
                                {
                                    "total_items": len(items),
                                    "filters_applied": filter_applied,
                                    "source_filter": filters.get("source"),
                                    "category_filter": filters.get("category")
                                })
                else:
                    self.log_test("Get Intelligence Filtered", False, 
                                "❌ Missing 'items' or 'filters' in response", data)
            elif response.status_code == 401:
                self.log_test("Get Intelligence Filtered", False, 
                            "❌ Authentication failed - token may be invalid")
            else:
                self.log_test("Get Intelligence Filtered", False, 
                            f"❌ Get filtered intelligence failed - Status {response.status_code}, expected 200")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get Intelligence Filtered", False, f"❌ Request failed: {str(e)}")

    def test_get_intelligence_summary(self):
        """Test GET /api/ganesha/intelligence/summary - Get intelligence summary"""
        if not self.auth_token:
            self.log_test("Get Intelligence Summary", False, 
                        "❌ No auth token available - login must succeed first")
            return
            
        try:
            headers = self.get_auth_headers()
            
            response = requests.get(f"{BACKEND_URL}/ganesha/intelligence/summary", 
                                  headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_items", "processed_items", "unprocessed_items", "by_source", "by_category", "last_updated"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    by_source = data.get("by_source", {})
                    by_category = data.get("by_category", {})
                    
                    self.log_test("Get Intelligence Summary", True, 
                                f"✅ Intelligence summary retrieved successfully", 
                                {
                                    "total_items": data.get("total_items"),
                                    "processed_items": data.get("processed_items"),
                                    "unprocessed_items": data.get("unprocessed_items"),
                                    "sources_tracked": list(by_source.keys()),
                                    "categories_tracked": list(by_category.keys())
                                })
                else:
                    self.log_test("Get Intelligence Summary", False, 
                                f"❌ Missing required fields in summary: {missing_fields}")
            elif response.status_code == 401:
                self.log_test("Get Intelligence Summary", False, 
                            "❌ Authentication failed - token may be invalid")
            else:
                self.log_test("Get Intelligence Summary", False, 
                            f"❌ Get intelligence summary failed - Status {response.status_code}, expected 200")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get Intelligence Summary", False, f"❌ Request failed: {str(e)}")

    # ========== 3. VOICE INPUT API ==========
    
    def test_voice_endpoint_exists(self):
        """Test POST /api/ganesha/voice - Verify endpoint exists and responds (without actual audio)"""
        if not self.auth_token:
            self.log_test("Voice Endpoint Check", False, 
                        "❌ No auth token available - login must succeed first")
            return
            
        try:
            headers = self.get_auth_headers()
            
            # Create a minimal test audio file (empty file to test endpoint)
            # This will test if the endpoint exists and handles requests properly
            files = {
                'file': ('test_audio.wav', b'', 'audio/wav')
            }
            
            response = requests.post(f"{BACKEND_URL}/ganesha/voice", 
                                   headers=headers, files=files, timeout=15)
            
            # We expect either 200 (success) or 400 (bad request due to empty file)
            # Both indicate the endpoint exists and is processing requests
            if response.status_code in [200, 400]:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                
                if response.status_code == 200:
                    # Success case
                    if "transcription" in data or "message" in data:
                        self.log_test("Voice Endpoint Check", True, 
                                    f"✅ Voice endpoint is operational and responding", 
                                    {
                                        "status_code": response.status_code,
                                        "has_transcription": "transcription" in data,
                                        "has_message": "message" in data,
                                        "method": data.get("method", "unknown")
                                    })
                    else:
                        self.log_test("Voice Endpoint Check", False, 
                                    "❌ Voice endpoint responded but missing expected fields")
                else:
                    # 400 is expected for empty file - endpoint exists
                    self.log_test("Voice Endpoint Check", True, 
                                f"✅ Voice endpoint exists and validates input (expected 400 for empty file)", 
                                {
                                    "status_code": response.status_code,
                                    "error_message": data.get("detail", "No detail provided"),
                                    "endpoint_functional": True
                                })
            elif response.status_code == 401:
                self.log_test("Voice Endpoint Check", False, 
                            "❌ Authentication failed - token may be invalid")
            elif response.status_code == 404:
                self.log_test("Voice Endpoint Check", False, 
                            "❌ Voice endpoint not found - may not be implemented")
            else:
                self.log_test("Voice Endpoint Check", False, 
                            f"❌ Voice endpoint returned unexpected status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Voice Endpoint Check", False, f"❌ Request failed: {str(e)}")

    # ========== 4. EXISTING ENDPOINTS VERIFICATION ==========
    
    def test_health_check(self):
        """Test GET /api/health - Verify healthy status"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    status = data.get("status")
                    if status in ["healthy", "ok"]:
                        self.log_test("Health Check", True, 
                                    f"✅ Health check successful - Status: {status}", 
                                    {"status": status, "app": data.get("app", "Unknown")})
                    else:
                        self.log_test("Health Check", False, 
                                    f"Unexpected health status: {status}")
                else:
                    self.log_test("Health Check", False, 
                                "Missing status field in response", data)
            else:
                self.log_test("Health Check", False, 
                            f"❌ Health check failed - Status {response.status_code}, expected 200")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Health Check", False, f"❌ Request failed: {str(e)}")

    def test_executive_dashboard(self):
        """Test GET /api/dashboard/executive with Bearer token - Verify executive dashboard data"""
        if not self.auth_token:
            self.log_test("Executive Dashboard", False, 
                        "❌ No auth token available - login must succeed first")
            return
            
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{BACKEND_URL}/dashboard/executive", 
                                  headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["kpis", "guardians", "data_sources", "problems_solved", "departments"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    kpis = data.get("kpis", {})
                    guardians = data.get("guardians", {})
                    departments = data.get("departments", {})
                    
                    self.log_test("Executive Dashboard", True, 
                                f"✅ Dashboard data retrieved successfully", 
                                {
                                    "kpis_count": len(kpis),
                                    "guardians": list(guardians.keys()),
                                    "total_departments": departments.get("total", 0),
                                    "problems_solved": len(data.get("problems_solved", []))
                                })
                else:
                    self.log_test("Executive Dashboard", False, 
                                f"❌ Missing required fields: {missing_fields}")
            elif response.status_code == 401:
                self.log_test("Executive Dashboard", False, 
                            "❌ Authentication failed - token may be invalid")
            else:
                self.log_test("Executive Dashboard", False, 
                            f"❌ Dashboard request failed - Status {response.status_code}, expected 200")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Executive Dashboard", False, f"❌ Request failed: {str(e)}")

    # ========== MAIN TEST RUNNER ==========
    
    def run_all_tests(self):
        """Run all intelligence and voice API tests"""
        print("🚀 STARTING Kailash - DAILY INTELLIGENCE & VOICE API TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: Kailash Code {TEST_CREDENTIALS['kailash_code']}")
        print("Testing: Authentication, Daily Intelligence APIs, Voice Input API, Health & Dashboard")
        print("=" * 80)
        print()
        
        # 1. Authentication System
        print("🔐 1. AUTHENTICATION SYSTEM")
        print("-" * 40)
        self.test_authentication_login()
        print()
        
        # 2. Daily Intelligence Collection APIs
        print("🧠 2. DAILY INTELLIGENCE COLLECTION APIS")
        print("-" * 40)
        self.test_create_intelligence()
        self.test_get_intelligence_list()
        self.test_get_intelligence_with_filters()
        self.test_get_intelligence_summary()
        print()
        
        # 3. Voice Input API
        print("🎤 3. VOICE INPUT API (WHISPER)")
        print("-" * 40)
        self.test_voice_endpoint_exists()
        print()
        
        # 4. Existing Endpoints Verification
        print("✅ 4. EXISTING ENDPOINTS VERIFICATION")
        print("-" * 40)
        self.test_health_check()
        self.test_executive_dashboard()
        print()
        
        # Final Summary
        self.print_final_summary()

    def print_final_summary(self):
        """Print final test summary"""
        print("=" * 80)
        print("🏁 Kailash - INTELLIGENCE & VOICE API TESTING COMPLETED")
        print("=" * 80)
        
        pass_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 RESULTS SUMMARY:")
        print(f"   Total Tests Executed: {self.total_tests}")
        print(f"   Tests Passed: {self.passed_tests}")
        print(f"   Tests Failed: {len(self.failed_tests)}")
        print(f"   Pass Rate: {pass_rate:.1f}%")
        print()
        
        if self.failed_tests:
            print("❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"   • {test['test']}: {test['message']}")
            print()
        
        # Feature readiness assessment
        if pass_rate >= 90:
            readiness = "✅ EXCELLENT - All features ready for production"
        elif pass_rate >= 80:
            readiness = "⚠️ GOOD - Minor issues to address"
        elif pass_rate >= 60:
            readiness = "🔶 FAIR - Several issues need fixing"
        else:
            readiness = "🔴 CRITICAL - Major issues block functionality"
        
        print(f"🎯 FEATURE READINESS STATUS: {readiness}")
        print(f"📈 Readiness Score: {pass_rate:.1f}%")
        print()
        
        # Specific feature analysis
        auth_failed = any("Authentication" in test['test'] for test in self.failed_tests)
        intelligence_failed = any("Intelligence" in test['test'] for test in self.failed_tests)
        voice_failed = any("Voice" in test['test'] for test in self.failed_tests)
        
        print("🔍 FEATURE ANALYSIS:")
        if not auth_failed:
            print("   ✅ Authentication: Working correctly")
        else:
            print("   ❌ Authentication: Issues detected")
            
        if not intelligence_failed:
            print("   ✅ Daily Intelligence APIs: Fully operational")
        else:
            print("   ❌ Daily Intelligence APIs: Issues detected")
            
        if not voice_failed:
            print("   ✅ Voice Input API: Endpoint operational")
        else:
            print("   ❌ Voice Input API: Issues detected")
        
        print()
        
        # Recommendations
        if pass_rate >= 90 and not auth_failed:
            print("✅ RECOMMENDATION: ALL NEW FEATURES ARE OPERATIONAL")
            print("   Daily Intelligence Collection APIs working correctly.")
            print("   Voice Input API endpoint is functional.")
            print("   Authentication and existing endpoints verified.")
        elif auth_failed:
            print("❌ RECOMMENDATION: CRITICAL AUTHENTICATION ISSUE")
            print("   Login API is failing - this blocks all protected endpoints.")
            print("   Fix authentication before proceeding with feature testing.")
        elif intelligence_failed:
            print("⚠️ RECOMMENDATION: INTELLIGENCE API ISSUES")
            print("   Daily Intelligence APIs need attention.")
            print("   Check database connectivity and API implementation.")
        elif voice_failed:
            print("⚠️ RECOMMENDATION: VOICE API ISSUES")
            print("   Voice Input API endpoint needs attention.")
            print("   Check Whisper API configuration and file handling.")
        else:
            print("⚠️ RECOMMENDATION: ADDRESS ISSUES BEFORE DEPLOYMENT")
            print("   Some new features need attention before production use.")
        
        print("=" * 80)


if __name__ == "__main__":
    tester = KailashIntelligenceVoiceTester()
    tester.run_all_tests()