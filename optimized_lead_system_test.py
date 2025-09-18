#!/usr/bin/env python3
"""
Optimized Lead Creation System Testing
Testing new optimized lead creation with auto-qualification and deal conversion
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://green-crm-suite.preview.emergentagent.com')
BASE_URL = f"{BACKEND_URL}/api"

class OptimizedLeadSystemTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def setup_session(self):
        """Setup HTTP session"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: dict = None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()
        
    async def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        try:
            async with self.session.get(f"{BASE_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Backend Connectivity", True, f"Backend responding: {data.get('message', 'OK')}")
                    return True
                else:
                    self.log_test("Backend Connectivity", False, f"Status: {response.status}")
                    return False
        except Exception as e:
            self.log_test("Backend Connectivity", False, f"Connection error: {str(e)}")
            return False
            
    async def test_optimized_lead_creation_high_score(self):
        """Test optimized lead creation with high qualification score (should auto-convert to deal)"""
        high_score_lead_data = {
            "name": "Rajesh Kumar",
            "email": "rajesh@test.com", 
            "phone": "+91-9876543210",
            "company": "Kumar Enterprises",
            "location": "Bandra West",
            "city": "Mumbai",
            "state": "Maharashtra",
            "project_type": "commercial_green_building",
            "space_type": "office_complex",
            "area_size": "5000_sqft",
            "services_needed": ["landscape_design", "plant_installation", "maintenance"],
            "requirements": "Need comprehensive green building solution with rooftop garden and indoor plants for 50-person office",
            "budget_range": "250k_500k",
            "timeline": "1_month",
            "urgency": "high",
            "decision_maker": "yes",
            "approval_process": "direct_authority",
            "current_situation": "new_office_setup",
            "previous_experience": "yes_satisfied",
            "qualification_score": 85,  # High score for auto-conversion
            "qualification_level": "HIGH",
            "priority": "HIGH",
            "status": "Qualified",
            "lead_source": "Website Contact Form",
            "ai_notes": "Highly qualified lead with clear requirements and budget"
        }
        
        try:
            async with self.session.post(f"{BASE_URL}/leads/optimized-create", 
                                       json=high_score_lead_data,
                                       headers={'Content-Type': 'application/json'}) as response:
                
                if response.status == 201:
                    data = await response.json()
                    
                    # Verify lead creation
                    if data.get('success') and data.get('lead'):
                        lead = data['lead']
                        
                        # Check auto-conversion to deal
                        auto_converted = data.get('auto_converted_to_deal', False)
                        deal_data = data.get('deal')
                        
                        if auto_converted and deal_data:
                            self.log_test("High-Score Lead Auto-Conversion", True, 
                                        f"Lead {lead['name']} (Score: {lead['qualification_score']}) auto-converted to deal {deal_data['id']}")
                            
                            # Verify deal data
                            expected_value = deal_data.get('estimated_value')
                            if expected_value == 375000:  # Expected for 250k_500k range
                                self.log_test("Deal Value Estimation", True, f"Correct deal value: ₹{expected_value}")
                            else:
                                self.log_test("Deal Value Estimation", False, f"Incorrect deal value: ₹{expected_value}, expected: ₹375000")
                                
                            return True
                        else:
                            self.log_test("High-Score Lead Auto-Conversion", False, 
                                        f"Lead with score {lead['qualification_score']} should auto-convert but didn't")
                            return False
                    else:
                        self.log_test("High-Score Lead Creation", False, "Lead creation failed", data)
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("High-Score Lead Creation", False, f"Status: {response.status}, Error: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("High-Score Lead Creation", False, f"Exception: {str(e)}")
            return False
            
    async def test_optimized_lead_creation_low_score(self):
        """Test optimized lead creation with low qualification score (should NOT auto-convert)"""
        low_score_lead_data = {
            "name": "Priya Sharma",
            "email": "priya.sharma@example.com",
            "phone": "+91-9123456789",
            "location": "Andheri East",
            "city": "Mumbai", 
            "state": "Maharashtra",
            "project_type": "residential_balcony",
            "budget_range": "under_25k",
            "timeline": "flexible",
            "decision_maker": "maybe",
            "qualification_score": 35,  # Low score - should NOT auto-convert
            "qualification_level": "LOW",
            "priority": "LOW",
            "status": "New",
            "lead_source": "Social Media",
            "ai_notes": "Needs nurturing - budget and timeline unclear"
        }
        
        try:
            async with self.session.post(f"{BASE_URL}/leads/optimized-create",
                                       json=low_score_lead_data,
                                       headers={'Content-Type': 'application/json'}) as response:
                
                if response.status == 201:
                    data = await response.json()
                    
                    if data.get('success') and data.get('lead'):
                        lead = data['lead']
                        auto_converted = data.get('auto_converted_to_deal', False)
                        
                        if not auto_converted:
                            self.log_test("Low-Score Lead Nurturing Path", True,
                                        f"Lead {lead['name']} (Score: {lead['qualification_score']}) correctly routed to nurturing")
                            return True
                        else:
                            self.log_test("Low-Score Lead Nurturing Path", False,
                                        f"Lead with score {lead['qualification_score']} should NOT auto-convert but did")
                            return False
                    else:
                        self.log_test("Low-Score Lead Creation", False, "Lead creation failed", data)
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("Low-Score Lead Creation", False, f"Status: {response.status}, Error: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("Low-Score Lead Creation", False, f"Exception: {str(e)}")
            return False
            
    async def test_ai_lead_qualification_analysis(self):
        """Test AI lead qualification analysis endpoint"""
        analysis_request = {
            "formData": {
                "name": "Rajesh Kumar",
                "project_type": "commercial_green_building",
                "budget_range": "250k_500k",
                "timeline": "1_month",
                "decision_maker": "yes",
                "urgency": "high"
            },
            "qualificationScore": 85
        }
        
        try:
            async with self.session.post(f"{BASE_URL}/ai/analyze-lead-qualification",
                                       json=analysis_request,
                                       headers={'Content-Type': 'application/json'}) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('analysis'):
                        analysis = data['analysis']
                        
                        # Verify analysis components
                        qualification = analysis.get('qualification')
                        confidence = analysis.get('confidence')
                        recommendations = analysis.get('recommendations', [])
                        next_actions = analysis.get('next_actions', [])
                        
                        if qualification == "QUALIFIED" and confidence > 80 and len(recommendations) >= 3:
                            self.log_test("AI Lead Qualification Analysis", True,
                                        f"Analysis complete: {qualification} (Confidence: {confidence}%)")
                            
                            # Test GPT-4o integration
                            ai_insights = analysis.get('ai_insights', '')
                            if ai_insights and len(ai_insights) > 100:
                                self.log_test("GPT-4o Integration", True, "AI insights generated successfully")
                            else:
                                self.log_test("GPT-4o Integration", False, "AI insights missing or too short")
                                
                            return True
                        else:
                            self.log_test("AI Lead Qualification Analysis", False,
                                        f"Incomplete analysis: {qualification}, confidence: {confidence}")
                            return False
                    else:
                        self.log_test("AI Lead Qualification Analysis", False, "Analysis failed", data)
                        return False
                else:
                    error_data = await response.text()
                    self.log_test("AI Lead Qualification Analysis", False, f"Status: {response.status}, Error: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_test("AI Lead Qualification Analysis", False, f"Exception: {str(e)}")
            return False
            
    async def test_helper_functions_validation(self):
        """Test helper functions through the API by creating leads with different budget ranges"""
        budget_test_cases = [
            {"budget_range": "under_25k", "expected_value": 20000},
            {"budget_range": "25k_50k", "expected_value": 37500},
            {"budget_range": "50k_100k", "expected_value": 75000},
            {"budget_range": "100k_250k", "expected_value": 175000},
            {"budget_range": "250k_500k", "expected_value": 375000},
            {"budget_range": "500k_1M", "expected_value": 750000},
            {"budget_range": "above_1M", "expected_value": 1500000}
        ]
        
        timeline_test_cases = [
            {"timeline": "immediate", "expected_days": 14},
            {"timeline": "1_month", "expected_days": 30},
            {"timeline": "3_months", "expected_days": 90},
            {"timeline": "6_months", "expected_days": 180},
            {"timeline": "flexible", "expected_days": 120}
        ]
        
        all_passed = True
        
        # Test budget value estimation
        for i, test_case in enumerate(budget_test_cases):
            test_lead = {
                "name": f"Test User {i+1}",
                "email": f"test{i+1}@budgettest.com",
                "phone": f"+91-987654321{i}",
                "budget_range": test_case["budget_range"],
                "timeline": "1_month",
                "qualification_score": 75,  # High enough for auto-conversion
                "status": "Qualified"
            }
            
            try:
                async with self.session.post(f"{BASE_URL}/leads/optimized-create",
                                           json=test_lead,
                                           headers={'Content-Type': 'application/json'}) as response:
                    
                    if response.status == 201:
                        data = await response.json()
                        if data.get('auto_converted_to_deal') and data.get('deal'):
                            deal = data['deal']
                            actual_value = deal.get('estimated_value')
                            expected_value = test_case["expected_value"]
                            
                            if actual_value == expected_value:
                                self.log_test(f"Budget Estimation - {test_case['budget_range']}", True,
                                            f"Correct value: ₹{actual_value}")
                            else:
                                self.log_test(f"Budget Estimation - {test_case['budget_range']}", False,
                                            f"Expected: ₹{expected_value}, Got: ₹{actual_value}")
                                all_passed = False
                        else:
                            self.log_test(f"Budget Estimation - {test_case['budget_range']}", False,
                                        "Deal not created for testing")
                            all_passed = False
                    else:
                        self.log_test(f"Budget Estimation - {test_case['budget_range']}", False,
                                    f"Lead creation failed: {response.status}")
                        all_passed = False
                        
            except Exception as e:
                self.log_test(f"Budget Estimation - {test_case['budget_range']}", False, f"Exception: {str(e)}")
                all_passed = False
                
        return all_passed
        
    async def test_data_validation_and_error_handling(self):
        """Test data validation and error handling"""
        test_cases = [
            {
                "name": "Missing Required Fields",
                "data": {"name": "Test User"},  # Missing email and phone
                "expected_status": 400
            },
            {
                "name": "Invalid Email Format", 
                "data": {"name": "Test User", "email": "invalid-email", "phone": "+91-9876543210"},
                "expected_status": 400
            },
            {
                "name": "Duplicate Email",
                "data": {"name": "Duplicate User", "email": "rajesh@test.com", "phone": "+91-9876543210"},
                "expected_status": 409
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                async with self.session.post(f"{BASE_URL}/leads/optimized-create",
                                           json=test_case["data"],
                                           headers={'Content-Type': 'application/json'}) as response:
                    
                    if response.status == test_case["expected_status"]:
                        self.log_test(f"Validation - {test_case['name']}", True,
                                    f"Correctly returned status {response.status}")
                    else:
                        self.log_test(f"Validation - {test_case['name']}", False,
                                    f"Expected status {test_case['expected_status']}, got {response.status}")
                        all_passed = False
                        
            except Exception as e:
                self.log_test(f"Validation - {test_case['name']}", False, f"Exception: {str(e)}")
                all_passed = False
                
        return all_passed
        
    async def test_conversion_logging(self):
        """Test that lead-to-deal conversions are properly logged"""
        # Create a high-score lead that should auto-convert
        conversion_test_lead = {
            "name": "Conversion Test User",
            "email": "conversion@test.com",
            "phone": "+91-9876543211",
            "project_type": "commercial_green_building",
            "budget_range": "500k_1M",
            "timeline": "1_month",
            "qualification_score": 90,
            "status": "Qualified"
        }
        
        try:
            async with self.session.post(f"{BASE_URL}/leads/optimized-create",
                                       json=conversion_test_lead,
                                       headers={'Content-Type': 'application/json'}) as response:
                
                if response.status == 201:
                    data = await response.json()
                    
                    if data.get('auto_converted_to_deal'):
                        lead_id = data['lead']['id']
                        deal_id = data['deal']['id']
                        
                        self.log_test("Conversion Logging", True,
                                    f"Lead {lead_id} successfully converted to deal {deal_id}")
                        return True
                    else:
                        self.log_test("Conversion Logging", False, "High-score lead did not auto-convert")
                        return False
                else:
                    self.log_test("Conversion Logging", False, f"Lead creation failed: {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("Conversion Logging", False, f"Exception: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all optimized lead system tests"""
        print("🚀 STARTING OPTIMIZED LEAD CREATION SYSTEM TESTING")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Test backend connectivity first
            if not await self.test_backend_connectivity():
                print("❌ Backend connectivity failed. Stopping tests.")
                return
                
            print("\n📋 TESTING OPTIMIZED LEAD CREATION ENDPOINTS")
            print("-" * 50)
            
            # Test optimized lead creation with high score (auto-conversion)
            await self.test_optimized_lead_creation_high_score()
            
            # Test optimized lead creation with low score (nurturing path)
            await self.test_optimized_lead_creation_low_score()
            
            print("\n🤖 TESTING AI LEAD QUALIFICATION ANALYSIS")
            print("-" * 50)
            
            # Test AI qualification analysis
            await self.test_ai_lead_qualification_analysis()
            
            print("\n🔧 TESTING HELPER FUNCTIONS")
            print("-" * 50)
            
            # Test helper functions validation
            await self.test_helper_functions_validation()
            
            print("\n✅ TESTING DATA VALIDATION & ERROR HANDLING")
            print("-" * 50)
            
            # Test data validation and error handling
            await self.test_data_validation_and_error_handling()
            
            print("\n📊 TESTING CONVERSION LOGGING")
            print("-" * 50)
            
            # Test conversion logging
            await self.test_conversion_logging()
            
        finally:
            await self.cleanup_session()
            
        # Print final results
        self.print_final_results()
        
    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("🎯 OPTIMIZED LEAD SYSTEM TEST RESULTS")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"   {result['status']}: {result['test']}")
            if result['details']:
                print(f"      → {result['details']}")
                
        print("\n" + "=" * 60)
        
        if success_rate >= 80:
            print("🎉 OPTIMIZED LEAD SYSTEM TESTING COMPLETED SUCCESSFULLY!")
        else:
            print("⚠️  OPTIMIZED LEAD SYSTEM HAS ISSUES THAT NEED ATTENTION")
            
        print("=" * 60)

async def main():
    """Main test execution"""
    tester = OptimizedLeadSystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())