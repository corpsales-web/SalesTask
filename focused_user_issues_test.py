#!/usr/bin/env python3
"""
Focused test for specific user-reported issues
"""

import requests
import json
import time
from datetime import datetime

class FocusedUserIssuesTest:
    def __init__(self, base_url="https://greenstack-ai.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        
    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 [{self.tests_run}] Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
                
            response_time = round((time.time() - start_time) * 1000, 2)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code} ({response_time}ms)")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list):
                        print(f"   📊 Response: List with {len(response_data)} items")
                    elif isinstance(response_data, dict) and len(str(response_data)) < 200:
                        print(f"   📊 Response: {response_data}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   ❌ Error: {error_data}")
                except:
                    print(f"   ❌ Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            return False, {}

    def test_user_reported_issues(self):
        """Test specific issues reported by user"""
        print("🚨 TESTING USER-REPORTED CRITICAL ISSUES")
        print("="*60)
        
        issues_results = {}
        
        # 1. "Failed to fetch tasks" error
        print("\n1️⃣ TESTING: 'Failed to fetch tasks' error")
        success, tasks_data = self.run_test("GET /api/tasks", "GET", "tasks", 200)
        issues_results['fetch_tasks'] = success
        if success and isinstance(tasks_data, list):
            print(f"   ✅ SUCCESS: Found {len(tasks_data)} tasks - NO 'Failed to fetch tasks' error")
        else:
            print(f"   ❌ CONFIRMED: 'Failed to fetch tasks' error still exists")
            
        # 2. Task status update failures
        print("\n2️⃣ TESTING: Task status update failures")
        if success and len(tasks_data) > 0:
            task_id = tasks_data[0]['id']
            success, _ = self.run_test("PUT /api/tasks/{id}/status", "PUT", f"tasks/{task_id}", 200, 
                                    data={"status": "In Progress"})
            issues_results['task_status_update'] = success
            if success:
                print(f"   ✅ SUCCESS: Task status updates working correctly")
            else:
                print(f"   ❌ CONFIRMED: Task status update failures still exist")
        else:
            issues_results['task_status_update'] = False
            print(f"   ❌ CANNOT TEST: No tasks available for status update test")
            
        # 3. Lead fetching issues
        print("\n3️⃣ TESTING: Lead fetching issues")
        success, leads_data = self.run_test("GET /api/leads", "GET", "leads", 200)
        issues_results['fetch_leads'] = success
        if success and isinstance(leads_data, list):
            print(f"   ✅ SUCCESS: Found {len(leads_data)} leads - NO lead fetching errors")
        else:
            print(f"   ❌ CONFIRMED: Lead fetching errors still exist")
            
        # 4. API consistency issues
        print("\n4️⃣ TESTING: API consistency issues")
        api_endpoints = [
            ("Dashboard Stats", "GET", "dashboard/stats"),
            ("Health Check", "GET", ""),
            ("Leads List", "GET", "leads"),
            ("Tasks List", "GET", "tasks")
        ]
        
        consistent_responses = 0
        for name, method, endpoint in api_endpoints:
            success, _ = self.run_test(f"API Consistency - {name}", method, endpoint, 200)
            if success:
                consistent_responses += 1
                
        consistency_rate = (consistent_responses / len(api_endpoints)) * 100
        issues_results['api_consistency'] = consistency_rate >= 75
        print(f"   📊 API Consistency Rate: {consistency_rate}% ({consistent_responses}/{len(api_endpoints)})")
        
        if consistency_rate >= 75:
            print(f"   ✅ SUCCESS: API consistency is good")
        else:
            print(f"   ❌ CONFIRMED: API consistency issues exist")
            
        # 5. Camera/File upload 502 errors
        print("\n5️⃣ TESTING: Camera/File upload 502 errors")
        
        # Test face check-in with proper data
        checkin_data = {
            "employee_id": "test_employee_001",
            "face_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "location": {"latitude": 19.0760, "longitude": 72.8777}
        }
        
        success, _ = self.run_test("HRMS Face Check-in", "POST", "hrms/face-checkin", 200, data=checkin_data)
        issues_results['camera_502'] = success
        
        if success:
            print(f"   ✅ SUCCESS: Camera/Face check-in working - NO 502 errors")
        else:
            print(f"   ❌ CONFIRMED: Camera 502 errors may still exist")
            
        return issues_results

    def test_critical_endpoints_performance(self):
        """Test performance of critical endpoints"""
        print("\n🚀 PERFORMANCE TESTING OF CRITICAL ENDPOINTS")
        print("="*60)
        
        endpoints = [
            ("GET /api/tasks", "GET", "tasks"),
            ("GET /api/leads", "GET", "leads"), 
            ("GET /api/dashboard/stats", "GET", "dashboard/stats")
        ]
        
        performance_results = {}
        
        for name, method, endpoint in endpoints:
            print(f"\n🔍 Performance testing {name}...")
            times = []
            
            # Run 3 tests to get average response time
            for i in range(3):
                start_time = time.time()
                try:
                    url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
                    response = requests.get(url, timeout=10)
                    response_time = (time.time() - start_time) * 1000
                    times.append(response_time)
                    print(f"   Test {i+1}: {response_time:.2f}ms (Status: {response.status_code})")
                except Exception as e:
                    print(f"   Test {i+1}: FAILED - {str(e)}")
                    
            if times:
                avg_time = sum(times) / len(times)
                performance_results[endpoint or 'root'] = avg_time
                print(f"   📊 Average Response Time: {avg_time:.2f}ms")
                
                if avg_time < 100:
                    print(f"   ✅ EXCELLENT performance")
                elif avg_time < 500:
                    print(f"   ✅ GOOD performance")
                elif avg_time < 1000:
                    print(f"   ⚠️ ACCEPTABLE performance")
                else:
                    print(f"   ❌ POOR performance")
                    
        return performance_results

    def generate_final_report(self, issues_results, performance_results):
        """Generate final report for user-reported issues"""
        print("\n" + "="*80)
        print("📋 FINAL REPORT: USER-REPORTED ISSUES VERIFICATION")
        print("="*80)
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        
        print(f"📊 OVERALL TEST STATISTICS:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎯 USER-REPORTED ISSUES STATUS:")
        
        issue_status = {
            'fetch_tasks': "1. 'Failed to fetch tasks' error",
            'task_status_update': "2. Task status update failures", 
            'fetch_leads': "3. Lead fetching issues",
            'api_consistency': "4. API consistency issues",
            'camera_502': "5. Camera 502 errors"
        }
        
        resolved_count = 0
        for key, description in issue_status.items():
            status = "✅ RESOLVED" if issues_results.get(key, False) else "❌ STILL EXISTS"
            print(f"   {description}: {status}")
            if issues_results.get(key, False):
                resolved_count += 1
                
        resolution_rate = (resolved_count / len(issue_status)) * 100
        print(f"\n📈 ISSUE RESOLUTION RATE: {resolution_rate:.1f}% ({resolved_count}/{len(issue_status)})")
        
        print(f"\n⚡ PERFORMANCE SUMMARY:")
        if performance_results:
            for endpoint, avg_time in performance_results.items():
                print(f"   {endpoint}: {avg_time:.2f}ms average")
                
        print(f"\n🏆 FINAL ASSESSMENT:")
        if resolution_rate >= 80:
            print("   🟢 EXCELLENT - Most user issues have been resolved")
        elif resolution_rate >= 60:
            print("   🟡 GOOD - Majority of user issues resolved")
        elif resolution_rate >= 40:
            print("   🟠 FAIR - Some user issues still need attention")
        else:
            print("   🔴 POOR - Major user issues still unresolved")
            
        print("\n" + "="*80)
        
        return {
            'success_rate': success_rate,
            'resolution_rate': resolution_rate,
            'issues_resolved': resolved_count,
            'total_issues': len(issue_status)
        }

if __name__ == "__main__":
    print("🔍 Focused Test: User-Reported Backend Issues")
    print("Testing specific issues mentioned in the review request")
    print("="*80)
    
    tester = FocusedUserIssuesTest()
    
    # Test user-reported issues
    issues_results = tester.test_user_reported_issues()
    
    # Test performance
    performance_results = tester.test_critical_endpoints_performance()
    
    # Generate final report
    final_results = tester.generate_final_report(issues_results, performance_results)