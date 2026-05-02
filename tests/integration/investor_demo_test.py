#!/usr/bin/env python3
"""
Kailash - Investor Demo Backend API Testing
Tests the newly implemented investor demo features:
1. GANESHA Multi-Model AI Orchestrator
2. SHIV Auto-Rectification Engine  
3. Executive Dashboard APIs
4. Guardian Status APIs

Backend URL: https://ganesha-v2-api.preview.emergentagent.com/api
Test Credentials: Kailash Code <REDACTED_kailash_code>, Password <REDACTED_PASSWORD>
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone
import asyncio
import aiohttp

# Backend URL from frontend .env
BACKEND_URL = "https://ganesha-v2-api.preview.emergentagent.com/api"

# Test credentials from review request
TEST_CREDENTIALS = {
    "kailash_code": "<REDACTED_kailash_code>",
    "password": "<REDACTED_PASSWORD>"
}

class InvestorDemoTester:
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        self.auth_token = None
        self.total_tests = 0
        self.passed_tests = 0
        self.user_id = None
        
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
        """Test POST /api/auth/login with investor demo credentials"""
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
                                    "Login successful with investor demo credentials", 
                                    {"user_name": user_data.get("full_name"), "kailash_code": user_data.get("kailash_code")})
                    else:
                        self.log_test("Authentication Login", False, 
                                    "Kailash code mismatch in response")
                else:
                    self.log_test("Authentication Login", False, 
                                "Missing access_token or user in response")
            else:
                self.log_test("Authentication Login", False, 
                            f"Status {response.status_code}, expected 200. Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Authentication Login", False, f"Request failed: {str(e)}")

    # ========== 2. GANESHA MULTI-MODEL AI ORCHESTRATOR ==========
    
    def test_ganesha_internal_query(self):
        """Test POST /api/ganesha/query - Internal query"""
        try:
            headers = self.get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            payload = {
                "message": "What is our financial status?",
                "model": "auto",
                "include_level2": False
            }
            
            response = requests.post(f"{BACKEND_URL}/ganesha/query", 
                                   json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["response", "routed_to", "scope", "models_used", "data_sources"]
                if all(field in data for field in required_fields):
                    if data["scope"] == "internal":
                        self.log_test("GANESHA Internal Query", True, 
                                    f"Query routed to {data['routed_to']} department, scope: {data['scope']}", 
                                    {"routed_to": data["routed_to"], "scope": data["scope"], "models_used": data["models_used"]})
                    else:
                        self.log_test("GANESHA Internal Query", False, 
                                    f"Expected internal scope, got: {data['scope']}")
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("GANESHA Internal Query", False, 
                                f"Missing required fields: {missing_fields}")
            elif response.status_code == 401:
                self.log_test("GANESHA Internal Query", False, 
                            "Authentication required - token may be invalid")
            else:
                self.log_test("GANESHA Internal Query", False, 
                            f"Status {response.status_code}, expected 200. Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("GANESHA Internal Query", False, f"Request failed: {str(e)}")

    def test_ganesha_external_query(self):
        """Test POST /api/ganesha/query - External query with Level 2"""
        try:
            headers = self.get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            payload = {
                "message": "How is URGAA charger utilization?",
                "model": "auto",
                "include_level2": True
            }
            
            response = requests.post(f"{BACKEND_URL}/ganesha/query", 
                                   json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["response", "routed_to", "scope", "source_product", "models_used", "data_sources"]
                if all(field in data for field in required_fields):
                    if data["scope"] == "external" and data.get("source_product") == "URGAA":
                        level = data.get("level", 1)
                        self.log_test("GANESHA External Query", True, 
                                    f"Query routed to {data['routed_to']}, product: {data['source_product']}, level: {level}", 
                                    {"routed_to": data["routed_to"], "source_product": data["source_product"], "level": level})
                    else:
                        self.log_test("GANESHA External Query", False, 
                                    f"Expected external/URGAA, got: {data['scope']}/{data.get('source_product')}")
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("GANESHA External Query", False, 
                                f"Missing required fields: {missing_fields}")
            else:
                self.log_test("GANESHA External Query", False, 
                            f"Status {response.status_code}, expected 200. Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("GANESHA External Query", False, f"Request failed: {str(e)}")

    def test_ganesha_routing_info(self):
        """Test GET /api/ganesha/routing-info - Department routing information"""
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{BACKEND_URL}/ganesha/routing-info", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["internal_departments", "external_departments", "guardian_departments", "total_departments"]
                if all(field in data for field in required_fields):
                    total = data["total_departments"]
                    internal_count = len(data["internal_departments"])
                    external_count = len(data["external_departments"])
                    self.log_test("GANESHA Routing Info", True, 
                                f"Retrieved routing info: {total} total departments ({internal_count} internal, {external_count} external)", 
                                {"total": total, "internal": internal_count, "external": external_count})
                else:
                    self.log_test("GANESHA Routing Info", False, 
                                "Missing required fields in routing info")
            else:
                self.log_test("GANESHA Routing Info", False, 
                            f"Status {response.status_code}, expected 200")
                
        except requests.exceptions.RequestException as e:
            self.log_test("GANESHA Routing Info", False, f"Request failed: {str(e)}")

    # ========== 3. SHIV AUTO-RECTIFICATION ENGINE ==========
    
    def test_shiv_automation_stats(self):
        """Test GET /api/shiv/automation-stats - Auto-rectification statistics"""
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{BACKEND_URL}/shiv/automation-stats", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_issues_detected", "auto_resolved", "escalated_to_physical", "automation_rate"]
                if all(field in data for field in required_fields):
                    total = data["total_issues_detected"]
                    auto_resolved = data["auto_resolved"]
                    rate = data["automation_rate"]
                    self.log_test("SHIV Automation Stats", True, 
                                f"Retrieved stats: {total} issues, {auto_resolved} auto-resolved, rate: {rate}", 
                                {"total_issues": total, "auto_resolved": auto_resolved, "rate": rate})
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("SHIV Automation Stats", False, 
                                f"Missing required fields: {missing_fields}")
            else:
                self.log_test("SHIV Automation Stats", False, 
                            f"Status {response.status_code}, expected 200")
                
        except requests.exceptions.RequestException as e:
            self.log_test("SHIV Automation Stats", False, f"Request failed: {str(e)}")

    def test_shiv_analyze_charger(self):
        """Test POST /api/shiv/analyze-charger - Charger health analysis"""
        try:
            headers = self.get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            payload = {
                "charger_id": "URG-001",
                "status": "Unavailable",
                "last_heartbeat": "2024-12-14T10:00:00Z",
                "error_codes": [],
                "temperature": 35.5,
                "active_session_hours": None,
                "firmware_version": "2.1.0"
            }
            
            response = requests.post(f"{BACKEND_URL}/shiv/analyze-charger", 
                                   json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["charger_id", "status", "issues_found", "auto_fixed", "escalated", "results"]
                if all(field in data for field in required_fields):
                    charger_id = data["charger_id"]
                    issues = data["issues_found"]
                    auto_fixed = data["auto_fixed"]
                    self.log_test("SHIV Analyze Charger", True, 
                                f"Analyzed {charger_id}: {issues} issues found, {auto_fixed} auto-fixed", 
                                {"charger_id": charger_id, "issues": issues, "auto_fixed": auto_fixed})
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("SHIV Analyze Charger", False, 
                                f"Missing required fields: {missing_fields}")
            else:
                self.log_test("SHIV Analyze Charger", False, 
                            f"Status {response.status_code}, expected 200. Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("SHIV Analyze Charger", False, f"Request failed: {str(e)}")

    def test_shiv_rectification_rules(self):
        """Test GET /api/shiv/rectification-rules - Auto-rectification rules"""
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{BACKEND_URL}/shiv/rectification-rules", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["auto_rectify_rules", "requires_physical_intervention", "ocpp_commands"]
                if all(field in data for field in required_fields):
                    rules_count = len(data["auto_rectify_rules"])
                    physical_count = len(data["requires_physical_intervention"])
                    commands_count = len(data["ocpp_commands"])
                    self.log_test("SHIV Rectification Rules", True, 
                                f"Retrieved {rules_count} auto-rectify rules, {physical_count} physical-only issues, {commands_count} OCPP commands", 
                                {"rules": rules_count, "physical": physical_count, "commands": commands_count})
                else:
                    self.log_test("SHIV Rectification Rules", False, 
                                "Missing required fields in rules response")
            else:
                self.log_test("SHIV Rectification Rules", False, 
                            f"Status {response.status_code}, expected 200")
                
        except requests.exceptions.RequestException as e:
            self.log_test("SHIV Rectification Rules", False, f"Request failed: {str(e)}")

    # ========== 4. EXECUTIVE DASHBOARD APIs ==========
    
    def test_dashboard_kpis(self):
        """Test GET /api/dashboard/kpis - Executive KPIs"""
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{BACKEND_URL}/dashboard/kpis", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_kpis = ["company_health", "total_revenue", "active_users", "system_uptime", "auto_resolved"]
                if all(kpi in data for kpi in expected_kpis):
                    health = data["company_health"]["value"]
                    revenue = data["total_revenue"]["value"]
                    uptime = data["system_uptime"]["value"]
                    self.log_test("Dashboard KPIs", True, 
                                f"Retrieved KPIs: Health {health}%, Revenue ₹{revenue:,}, Uptime {uptime}%", 
                                {"health": health, "revenue": revenue, "uptime": uptime})
                else:
                    missing_kpis = [kpi for kpi in expected_kpis if kpi not in data]
                    self.log_test("Dashboard KPIs", False, 
                                f"Missing KPIs: {missing_kpis}")
            else:
                self.log_test("Dashboard KPIs", False, 
                            f"Status {response.status_code}, expected 200")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Dashboard KPIs", False, f"Request failed: {str(e)}")

    def test_dashboard_executive(self):
        """Test GET /api/dashboard/executive - Full executive dashboard"""
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{BACKEND_URL}/dashboard/executive", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_sections = ["kpis", "guardians", "data_sources", "problems_solved", "departments"]
                if all(section in data for section in required_sections):
                    guardians = data["guardians"]
                    problems_count = len(data["problems_solved"])
                    dept_total = data["departments"]["total"]
                    
                    # Check guardian data
                    guardian_status = "OK" if "shiv" in guardians and "parvati" in guardians else "Missing"
                    
                    self.log_test("Dashboard Executive", True, 
                                f"Executive dashboard complete: {problems_count} problems solved, {dept_total} departments, guardians: {guardian_status}", 
                                {"problems_solved": problems_count, "departments": dept_total, "guardians": guardian_status})
                else:
                    missing_sections = [section for section in required_sections if section not in data]
                    self.log_test("Dashboard Executive", False, 
                                f"Missing sections: {missing_sections}")
            else:
                self.log_test("Dashboard Executive", False, 
                            f"Status {response.status_code}, expected 200")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Dashboard Executive", False, f"Request failed: {str(e)}")

    def test_dashboard_alerts(self):
        """Test GET /api/dashboard/alerts - Active alerts"""
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{BACKEND_URL}/dashboard/alerts", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "alerts" in data and "summary" in data:
                    alerts_count = len(data["alerts"])
                    summary = data["summary"]
                    critical = summary.get("critical", 0)
                    warning = summary.get("warning", 0)
                    self.log_test("Dashboard Alerts", True, 
                                f"Retrieved {alerts_count} alerts: {critical} critical, {warning} warning", 
                                {"total_alerts": alerts_count, "critical": critical, "warning": warning})
                else:
                    self.log_test("Dashboard Alerts", False, 
                                "Missing alerts or summary in response")
            else:
                self.log_test("Dashboard Alerts", False, 
                            f"Status {response.status_code}, expected 200")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Dashboard Alerts", False, f"Request failed: {str(e)}")

    # ========== 5. GUARDIAN STATUS ==========
    
    def test_guardians_status(self):
        """Test GET /api/guardians/status - Guardian status"""
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{BACKEND_URL}/guardians/status", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_guardians = ["SHIV", "PARVATI", "GANESHA"]
                if all(guardian in data for guardian in expected_guardians):
                    shiv_status = data["SHIV"].get("status", "unknown")
                    parvati_status = data["PARVATI"].get("status", "unknown")
                    ganesha_status = data["GANESHA"].get("status", "unknown")
                    self.log_test("Guardians Status", True, 
                                f"All guardians responding: SHIV={shiv_status}, PARVATI={parvati_status}, GANESHA={ganesha_status}", 
                                {"SHIV": shiv_status, "PARVATI": parvati_status, "GANESHA": ganesha_status})
                else:
                    missing_guardians = [g for g in expected_guardians if g not in data]
                    self.log_test("Guardians Status", False, 
                                f"Missing guardians: {missing_guardians}")
            else:
                self.log_test("Guardians Status", False, 
                            f"Status {response.status_code}, expected 200")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Guardians Status", False, f"Request failed: {str(e)}")

    # ========== MAIN TEST RUNNER ==========
    
    def run_all_tests(self):
        """Run all investor demo backend tests"""
        print("🚀 STARTING Kailash INVESTOR DEMO BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: Kailash Code {TEST_CREDENTIALS['kailash_code']}")
        print("Testing: GANESHA Multi-Model AI, SHIV Auto-Rectification, Executive Dashboard, Guardian Status")
        print("=" * 80)
        print()
        
        # 1. Authentication System
        print("🔐 1. AUTHENTICATION SYSTEM")
        print("-" * 40)
        self.test_authentication_login()
        print()
        
        if not self.auth_token:
            print("❌ AUTHENTICATION FAILED - CANNOT CONTINUE WITH PROTECTED ENDPOINTS")
            self.print_final_summary()
            return
        
        # 2. GANESHA Multi-Model AI Orchestrator
        print("🧠 2. GANESHA MULTI-MODEL AI ORCHESTRATOR")
        print("-" * 40)
        self.test_ganesha_internal_query()
        self.test_ganesha_external_query()
        self.test_ganesha_routing_info()
        print()
        
        # 3. SHIV Auto-Rectification Engine
        print("⚡ 3. SHIV AUTO-RECTIFICATION ENGINE")
        print("-" * 40)
        self.test_shiv_automation_stats()
        self.test_shiv_analyze_charger()
        self.test_shiv_rectification_rules()
        print()
        
        # 4. Executive Dashboard APIs
        print("📊 4. EXECUTIVE DASHBOARD APIs")
        print("-" * 40)
        self.test_dashboard_kpis()
        self.test_dashboard_executive()
        self.test_dashboard_alerts()
        print()
        
        # 5. Guardian Status
        print("🛡️ 5. GUARDIAN STATUS")
        print("-" * 40)
        self.test_guardians_status()
        print()
        
        # Final Summary
        self.print_final_summary()

    def print_final_summary(self):
        """Print final test summary"""
        print("=" * 80)
        print("🏁 Kailash INVESTOR DEMO TESTING COMPLETED")
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
        
        # Investor Demo Readiness Assessment
        if pass_rate >= 90:
            readiness = "✅ EXCELLENT - Investor Demo Ready"
        elif pass_rate >= 80:
            readiness = "⚠️ GOOD - Minor Issues to Address"
        elif pass_rate >= 60:
            readiness = "🔶 FAIR - Several Issues Need Fixing"
        else:
            readiness = "🔴 CRITICAL - Major Issues Block Demo"
        
        print(f"🎯 INVESTOR DEMO READINESS: {readiness}")
        print(f"📈 Readiness Score: {pass_rate:.1f}%")
        print()
        
        # Specific recommendations
        critical_failures = [t for t in self.failed_tests if any(keyword in t['test'] for keyword in ['Authentication', 'GANESHA', 'Dashboard'])]
        
        if pass_rate >= 85 and not critical_failures:
            print("✅ RECOMMENDATION: INVESTOR DEMO READY FOR PRESENTATION")
            print("   All core AI orchestration and dashboard features operational.")
            print("   SHIV auto-rectification and executive insights working correctly.")
        elif critical_failures:
            print("❌ RECOMMENDATION: CRITICAL ISSUES MUST BE RESOLVED")
            print("   Authentication or core demo features are failing.")
            print("   Fix critical issues before investor presentation.")
        else:
            print("⚠️ RECOMMENDATION: ADDRESS ISSUES BEFORE DEMO")
            print("   Some investor demo features need attention for optimal presentation.")
        
        print("=" * 80)


if __name__ == "__main__":
    tester = InvestorDemoTester()
    tester.run_all_tests()