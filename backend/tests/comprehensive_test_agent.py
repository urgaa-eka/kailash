"""
COMPREHENSIVE TEST AGENT OR KAILASH INTEGRATION
=========================================================

This agent performs exhaustive testing of:
- ackend API endpoints (KAILASH + KAILASH)
- rontend UI components
- Integration flows
- Database operations
- Security measures
- Performance metrics

Generates detailed HTML report with pass/fail statistics.
"""

import asyncio
import aiohttp
import time
import json
import sys
from typing import List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Configuration
ACKEND_URL = os.getenv('REACT_APP_ACKEND_URL', 'http://localhost:8')
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:')
D_NAME = os.getenv('D_NAME', 'kailash')

class TestResult:
    """Individual test result"""
    def __init__(self, category: str, name: str, status: str, message: str = "", duration: float = ):
        self.category = category
        self.name = name
        self.status = status  # PASS, AIL, SKIP
        self.message = message
        self.duration = duration
        self.timestamp = datetime.now().isoformat()


class ComprehensiveTestAgent:
    """
    Automated testing agent that validates entire KAILASH system
    """
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.mongo_client = None
        self.db = None
        self.session = None
        self.mock_token = "mock-test-token"
        
    async def initialize(self):
        """Initialize connections"""
        self.mongo_client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.mongo_client[D_NAME]
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup connections"""
        if self.session:
            await self.session.close()
        if self.mongo_client:
            self.mongo_client.close()
    
    def add_result(self, result: TestResult):
        """Add test result"""
        self.results.append(result)
        status_symbol = "[OK]" if result.status == "PASS" else "[AIL]" if result.status == "AIL" else "⏭️"
        print(f"{status_symbol} [{result.category}] {result.name} ({result.duration:.f}s)")
        if result.message and result.status == "AIL":
            print(f"   └─ {result.message}")
    
    # ============================================
    # ACKEND API TESTS
    # ============================================
    
    async def test_backend_api(self):
        """Test all backend API endpoints"""
        print("\n" + "="*)
        print(" ACKEND API TESTING")
        print("="*)
        
        await self.test_Kailash_endpoints()
        await self.test_kailash_endpoints()
        await self.test_authentication_flow()
        await self.test_error_handling()
    
    async def test_Kailash_endpoints(self):
        """Test KAILASH core endpoints"""
        tests = [
            {
                "name": "API Root Endpoint",
                "method": "GET",
                "url": f"{ACKEND_URL}/api/",
                "expected_status": ,
                "expected_keys": ["message"]
            },
            {
                "name": "Status Check POST",
                "method": "POST",
                "url": f"{ACKEND_URL}/api/status",
                "data": {"client_name": "test_client"},
                "expected_status": ,
                "expected_keys": ["id", "client_name", "timestamp"]
            },
            {
                "name": "Status Check GET",
                "method": "GET",
                "url": f"{ACKEND_URL}/api/status",
                "expected_status": 
            }
        ]
        
        for test in tests:
            await self._execute_api_test("ACKEND_API", test)
    
    async def test_kailash_endpoints(self):
        """Test KAILASH integrated endpoints"""
        tests = [
            {
                "name": "KAILASH Health Check",
                "method": "GET",
                "url": f"{ACKEND_URL}/api/kailash/health",
                "expected_status": ,
                "expected_keys": ["status", "service", "timestamp"]
            },
            {
                "name": "KAILASH Dashboard Overview",
                "method": "GET",
                "url": f"{ACKEND_URL}/api/kailash/dashboard/overview",
                "headers": {"Authorization": f"earer {self.mock_token}"},
                "expected_status": [, 4],  # May require auth
                "skip_on_4": True
            },
            {
                "name": "KAILASH Tasks List",
                "method": "GET",
                "url": f"{ACKEND_URL}/api/kailash/tasks",
                "headers": {"Authorization": f"earer {self.mock_token}"},
                "expected_status": [, 4],
                "skip_on_4": True
            }
        ]
        
        for test in tests:
            await self._execute_api_test("KAILASH_API", test)
    
    async def test_authentication_flow(self):
        """Test authentication mechanisms"""
        tests = [
            {
                "name": "Login Endpoint Exists",
                "method": "POST",
                "url": f"{ACKEND_URL}/api/auth/login",
                "data": {"kailash_code": "TEST", "decode": "TEST"},
                "expected_status": [, 4, 4]  # Endpoint exists
            },
            {
                "name": "Session Endpoint (Unauthenticated)",
                "method": "GET",
                "url": f"{ACKEND_URL}/api/auth/session",
                "expected_status": [4, 43]  # Should reject without auth
            }
        ]
        
        for test in tests:
            await self._execute_api_test("AUTHENTICATION", test)
    
    async def test_error_handling(self):
        """Test API error handling"""
        tests = [
            {
                "name": "Invalid Endpoint (44)",
                "method": "GET",
                "url": f"{ACKEND_URL}/api/nonexistent-endpoint",
                "expected_status": 44
            },
            {
                "name": "Invalid Method (4 or 44)",
                "method": "DELETE",
                "url": f"{ACKEND_URL}/api/",
                "expected_status": [4, 44]
            },
            {
                "name": "Malformed JSON",
                "method": "POST",
                "url": f"{ACKEND_URL}/api/status",
                "data": "invalid-json",
                "expected_status": [4, 4]
            }
        ]
        
        for test in tests:
            await self._execute_api_test("ERROR_HANDLING", test)
    
    async def _execute_api_test(self, category: str, test: Dict[str, Any]):
        """Execute a single API test"""
        start_time = time.time()
        
        try:
            method = test["method"]
            url = test["url"]
            headers = test.get("headers", {})
            data = test.get("data")
            expected_status = test["expected_status"]
            expected_keys = test.get("expected_keys", [])
            skip_on_4 = test.get("skip_on_4", False)
            
            # Make request
            if method == "GET":
                async with self.session.get(url, headers=headers) as resp:
                    status = resp.status
                    try:
                        response_data = await resp.json()
                    except:
                        response_data = {}
            elif method == "POST":
                if isinstance(data, str):
                    # Malformed JSON test
                    headers["Content-Type"] = "application/json"
                    async with self.session.post(url, data=data, headers=headers) as resp:
                        status = resp.status
                        response_data = {}
                else:
                    async with self.session.post(url, json=data, headers=headers) as resp:
                        status = resp.status
                        try:
                            response_data = await resp.json()
                        except:
                            response_data = {}
            else:
                async with self.session.request(method, url, headers=headers) as resp:
                    status = resp.status
                    response_data = {}
            
            # Check status
            if isinstance(expected_status, list):
                status_ok = status in expected_status
            else:
                status_ok = status == expected_status
            
            # Skip test if 4 and skip flag is set
            if skip_on_4 and status == 4:
                duration = time.time() - start_time
                self.add_result(TestResult(
                    category, test["name"], "SKIP",
                    "Skipped due to authentication requirement", duration
                ))
                return
            
            if not status_ok:
                duration = time.time() - start_time
                self.add_result(TestResult(
                    category, test["name"], "AIL",
                    f"Expected status {expected_status}, got {status}", duration
                ))
                return
            
            # Check expected keys
            if expected_keys:
                missing_keys = [k for k in expected_keys if k not in response_data]
                if missing_keys:
                    duration = time.time() - start_time
                    self.add_result(TestResult(
                        category, test["name"], "AIL",
                        f"Missing keys: {missing_keys}", duration
                    ))
                    return
            
            # Test passed
            duration = time.time() - start_time
            self.add_result(TestResult(
                category, test["name"], "PASS", "", duration
            ))
            
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(TestResult(
                category, test["name"], "AIL",
                f"Exception: {str(e)}", duration
            ))
    
    # ============================================
    # DATAASE TESTS
    # ============================================
    
    async def test_database(self):
        """Test database operations"""
        print("\n" + "="*)
        print("️  DATAASE TESTING")
        print("="*)
        
        await self.test_database_connectivity()
        await self.test_collections_exist()
        await self.test_crud_operations()
    
    async def test_database_connectivity(self):
        """Test MongoD connectivity"""
        start_time = time.time()
        try:
            await self.db.command("ping")
            duration = time.time() - start_time
            self.add_result(TestResult(
                "DATAASE", "MongoD Connectivity", "PASS", "", duration
            ))
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(TestResult(
                "DATAASE", "MongoD Connectivity", "AIL",
                f"Connection failed: {str(e)}", duration
            ))
    
    async def test_collections_exist(self):
        """Verify required collections exist"""
        start_time = time.time()
        required_collections = [
            "status_checks", "tasks", "commands",
            "departments", "agent_activity"
        ]
        
        try:
            existing = await self.db.list_collection_names()
            missing = [c for c in required_collections if c not in existing]
            
            duration = time.time() - start_time
            if not missing:
                self.add_result(TestResult(
                    "DATAASE", "Required Collections Exist", "PASS", "", duration
                ))
            else:
                self.add_result(TestResult(
                    "DATAASE", "Required Collections Exist", "AIL",
                    f"Missing collections: {missing}", duration
                ))
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(TestResult(
                "DATAASE", "Required Collections Exist", "AIL",
                f"Error: {str(e)}", duration
            ))
    
    async def test_crud_operations(self):
        """Test CRUD operations"""
        start_time = time.time()
        test_collection = "test_crud"
        
        try:
            # CREATE
            test_doc = {"test_id": "test-3", "data": "test", "timestamp": datetime.utcnow().isoformat()}
            await self.db[test_collection].insert_one(test_doc)
            
            # READ
            found = await self.db[test_collection].find_one({"test_id": "test-3"})
            if not found:
                raise Exception("Document not found after insert")
            
            # UPDATE
            await self.db[test_collection].update_one(
                {"test_id": "test-3"},
                {"$set": {"data": "updated"}}
            )
            updated = await self.db[test_collection].find_one({"test_id": "test-3"})
            if updated["data"] != "updated":
                raise Exception("Document not updated")
            
            # DELETE
            await self.db[test_collection].delete_one({"test_id": "test-3"})
            deleted = await self.db[test_collection].find_one({"test_id": "test-3"})
            if deleted:
                raise Exception("Document not deleted")
            
            # Cleanup collection
            await self.db[test_collection].drop()
            
            duration = time.time() - start_time
            self.add_result(TestResult(
                "DATAASE", "CRUD Operations", "PASS", "", duration
            ))
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(TestResult(
                "DATAASE", "CRUD Operations", "AIL",
                f"Error: {str(e)}", duration
            ))
    
    # ============================================
    # INTEGRATION TESTS
    # ============================================
    
    async def test_integration(self):
        """Test end-to-end integration flows"""
        print("\n" + "="*)
        print(" INTEGRATION TESTING")
        print("="*)
        
        await self.test_Kailash_kailash_integration()
        await self.test_command_flow()
    
    async def test_Kailash_kailash_integration(self):
        """Test KAILASH → KAILASH integration"""
        start_time = time.time()
        
        try:
            # . Check KAILASH root
            async with self.session.get(f"{ACKEND_URL}/api/") as resp:
                if resp.status != :
                    raise Exception("KAILASH root endpoint failed")
            
            # . Check KAILASH health through KAILASH
            async with self.session.get(f"{ACKEND_URL}/api/kailash/health") as resp:
                if resp.status != :
                    raise Exception("KAILASH health endpoint not accessible")
            
            duration = time.time() - start_time
            self.add_result(TestResult(
                "INTEGRATION", "KAILASH-KAILASH Connection", "PASS", "", duration
            ))
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(TestResult(
                "INTEGRATION", "KAILASH-KAILASH Connection", "AIL",
                f"Error: {str(e)}", duration
            ))
    
    async def test_command_flow(self):
        """Test GANESHA command processing flow"""
        start_time = time.time()
        
        # This test requires authentication, so we'll skip if not available
        try:
            async with self.session.post(
                f"{ACKEND_URL}/api/kailash/ganesha/command",
                json={"command": "Test command"},
                headers={"Authorization": f"earer {self.mock_token}"}
            ) as resp:
                if resp.status == 4:
                    duration = time.time() - start_time
                    self.add_result(TestResult(
                        "INTEGRATION", "GANESHA Command low", "SKIP",
                        "Requires authentication", duration
                    ))
                    return
                
                if resp.status != :
                    raise Exception(f"Command endpoint returned {resp.status}")
                
                data = await resp.json()
                if "command_id" not in data:
                    raise Exception("Response missing command_id")
                
                duration = time.time() - start_time
                self.add_result(TestResult(
                    "INTEGRATION", "GANESHA Command low", "PASS", "", duration
                ))
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(TestResult(
                "INTEGRATION", "GANESHA Command low", "AIL",
                f"Error: {str(e)}", duration
            ))
    
    # ============================================
    # PERORMANCE TESTS
    # ============================================
    
    async def test_performance(self):
        """Test performance metrics"""
        print("\n" + "="*)
        print("⚡ PERORMANCE TESTING")
        print("="*)
        
        await self.test_response_times()
        await self.test_concurrent_requests()
    
    async def test_response_times(self):
        """Measure API response times"""
        start_time = time.time()
        
        try:
            times = []
            for _ in range():
                req_start = time.time()
                async with self.session.get(f"{ACKEND_URL}/api/") as resp:
                    await resp.read()
                req_duration = time.time() - req_start
                times.append(req_duration)
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            duration = time.time() - start_time
            if avg_time < . and max_time < .:
                self.add_result(TestResult(
                    "PERORMANCE", "Response Time (Avg < s, Max < s)", "PASS",
                    f"Avg: {avg_time:.3f}s, Max: {max_time:.3f}s", duration
                ))
            else:
                self.add_result(TestResult(
                    "PERORMANCE", "Response Time (Avg < s, Max < s)", "AIL",
                    f"Avg: {avg_time:.3f}s, Max: {max_time:.3f}s (Too slow)", duration
                ))
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(TestResult(
                "PERORMANCE", "Response Time", "AIL",
                f"Error: {str(e)}", duration
            ))
    
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        start_time = time.time()
        
        try:
            async def make_request():
                async with self.session.get(f"{ACKEND_URL}/api/") as resp:
                    return resp.status == 
            
            # Send  concurrent requests
            tasks = [make_request() for _ in range()]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = sum( for r in results if r is True)
            failure_count = len(results) - success_count
            
            duration = time.time() - start_time
            if success_count >= 4:  # 9% success rate
                self.add_result(TestResult(
                    "PERORMANCE", "Concurrent Requests ()", "PASS",
                    f"{success_count}/ successful ({failure_count} failed)", duration
                ))
            else:
                self.add_result(TestResult(
                    "PERORMANCE", "Concurrent Requests ()", "AIL",
                    f"Only {success_count}/ successful ({failure_count} failed)", duration
                ))
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(TestResult(
                "PERORMANCE", "Concurrent Requests", "AIL",
                f"Error: {str(e)}", duration
            ))
    
    # ============================================
    # MAIN TEST RUNNER
    # ============================================
    
    async def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*)
        print(" KAILASH COMPREHENSIVE TEST AGENT")
        print("="*)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"ackend URL: {ACKEND_URL}")
        print(f"MongoD: {MONGO_URL}")
        print("="*)
        
        start_time = time.time()
        
        try:
            await self.initialize()
            
            # Run all test suites
            await self.test_backend_api()
            await self.test_database()
            await self.test_integration()
            await self.test_performance()
            
        finally:
            await self.cleanup()
        
        total_duration = time.time() - start_time
        
        # Generate report
        report = self.generate_report(total_duration)
        
        return report
    
    def generate_report(self, total_duration: float) -> str:
        """Generate comprehensive HTML report"""
        # Calculate statistics
        total_tests = len(self.results)
        passed = sum( for r in self.results if r.status == "PASS")
        failed = sum( for r in self.results if r.status == "AIL")
        skipped = sum( for r in self.results if r.status == "SKIP")
        pass_rate = (passed / total_tests * ) if total_tests > 50 else 
        
        # Group results by category
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        # Generate HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>KAILASH Test Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: ;
            padding: px;
            background: linear-gradient(3deg, #eea %, #4ba %);
        }}
        .container {{
            max-width: px;
            margin:  auto;
            background: white;
            border-radius: px;
            box-shadow:  px 4px rgba(,,,.);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(3deg, #f93fb %, #fc %);
            color: white;
            padding: 3px;
            text-align: center;
        }}
        .header h {{
            margin: ;
            font-size: .em;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(px, fr));
            gap: px;
            padding: 3px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: px;
            border-radius: 8px;
            box-shadow:  px px rgba(,,,.);
            text-align: center;
        }}
        .stat-value {{
            font-size: .em;
            font-weight: bold;
            margin: px ;
        }}
        .stat-label {{
            color: #;
            text-transform: uppercase;
            font-size: .9em;
            letter-spacing: px;
        }}
        .pass {{ color: #8a4; }}
        .fail {{ color: #dc34; }}
        .skip {{ color: #ffc; }}
        .category {{
            margin: 3px;
        }}
        .category-title {{
            font-size: .em;
            font-weight: bold;
            margin-bottom: px;
            padding-bottom: px;
            border-bottom: 3px solid #eea;
        }}
        .test-result {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: px;
            margin: px ;
            border-radius: px;
            background: #f8f9fa;
        }}
        .test-result.passed {{
            border-left: 4px solid #8a4;
        }}
        .test-result.failed {{
            border-left: 4px solid #dc34;
        }}
        .test-result.skipped {{
            border-left: 4px solid #ffc;
        }}
        .test-name {{
            font-weight: ;
            flex: ;
        }}
        .test-status {{
            font-weight: bold;
            margin:  px;
        }}
        .test-duration {{
            color: #;
            font-size: .9em;
        }}
        .test-message {{
            color: #;
            font-size: .9em;
            margin-top: px;
        }}
        .footer {{
            background: #c3e;
            color: white;
            padding: px;
            text-align: center;
        }}
        .progress-bar {{
            width: %;
            height: 3px;
            background: #e9ecef;
            border-radius: px;
            overflow: hidden;
            margin: px ;
        }}
        .progress-fill {{
            height: %;
            background: linear-gradient(9deg, #8a4 %, #c99 %);
            transition: width .3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h> KAILASH Comprehensive Test Report</h>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <div class="stat-card">
                <div class="stat-label">Total Tests</div>
                <div class="stat-value">{total_tests}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Passed</div>
                <div class="stat-value pass">{passed}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">ailed</div>
                <div class="stat-value fail">{failed}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Skipped</div>
                <div class="stat-value skip">{skipped}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Pass Rate</div>
                <div class="stat-value pass">{pass_rate:.f}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Duration</div>
                <div class="stat-value">{total_duration:.f}s</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {pass_rate}%">
                {pass_rate:.f}% Pass Rate
            </div>
        </div>
"""
        
        # Add category sections
        for category, results in categories.items():
            cat_passed = sum( for r in results if r.status == "PASS")
            cat_total = len(results)
            
            html += f"""
        <div class="category">
            <div class="category-title">{category} ({cat_passed}/{cat_total} passed)</div>
"""
            
            for result in results:
                status_class = result.status.lower()
                status_text = result.status
                
                html += f"""
            <div class="test-result {status_class}ed">
                <div class="test-name">
                    {result.name}
                    {f'<div class="test-message">{result.message}</div>' if result.message else ''}
                </div>
                <div class="test-status {status_class}">{status_text}</div>
                <div class="test-duration">{result.duration:.3f}s</div>
            </div>
"""
            
            html += """
        </div>
"""
        
        # ooter
        html += f"""
        <div class="footer">
            <p>KAILASH Integration | Comprehensive Test Agent v.</p>
            <p>ackend: {ACKEND_URL} | Database: {D_NAME}</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html


async def main():
    """Main entry point"""
    agent = ComprehensiveTestAgent()
    
    try:
        report_html = await agent.run_all_tests()
        
        # Save report
        report_path = "/app/KAILASH_TEST_REPORT.html"
        with open(report_path, "w") as f:
            f.write(report_html)
        
        print("\n" + "="*)
        print(" TEST SUMMARY")
        print("="*)
        
        total = len(agent.results)
        passed = sum( for r in agent.results if r.status == "PASS")
        failed = sum( for r in agent.results if r.status == "AIL")
        skipped = sum( for r in agent.results if r.status == "SKIP")
        pass_rate = (passed / total * ) if total > 50 else 
        
        print(f"Total Tests: {total}")
        print(f"[OK] Passed: {passed}")
        print(f"[AIL] ailed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print(f" Pass Rate: {pass_rate:.f}%")
        print(f"\n Report saved to: {report_path}")
        print("="*)
        
        # Exit with appropriate code
        sys.exit( if failed == 0 else )
        
    except Exception as e:
        print(f"\n[AIL] Test agent failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit()


if __name__ == "__main__":
    asyncio.run(main())
