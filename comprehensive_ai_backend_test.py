import requests
import sys
import json
from datetime import datetime, timezone
import uuid
import time

class ComprehensiveAIBackendTester:
    def __init__(self, base_url="https://greenstack-ai.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.test_results = []
        
    def log_test_result(self, test_name, success, status_code, response_data=None, error=None):
        """Log test result for detailed reporting"""
        result = {
            "test_name": test_name,
            "success": success,
            "status_code": status_code,
            "response_data": response_data,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, headers=None):
        """Run a single API test with enhanced logging"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 300:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    else:
                        print(f"   Response: Large response received")
                    self.log_test_result(name, True, response.status_code, response_data)
                    return True, response_data
                except:
                    self.log_test_result(name, True, response.status_code)
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    self.log_test_result(name, False, response.status_code, error=error_data)
                except:
                    print(f"   Error: {response.text}")
                    self.log_test_result(name, False, response.status_code, error=response.text)
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.log_test_result(name, False, 0, error=str(e))
            return False, {}

    # Enhanced AI Endpoints Testing
    def test_ai_generate(self):
        """Test /api/ai/generate - Multi-model AI response generation"""
        data = {
            "prompt": "Generate a professional proposal for a 2 BHK balcony garden transformation project in Mumbai with a budget of ₹50,000",
            "provider": "openai",
            "model": "gpt-5",
            "temperature": 0.7,
            "system_message": "You are an expert landscaping consultant for Aavana Greens, specializing in urban balcony gardens and green building solutions."
        }
        return self.run_test("AI Generate - Multi-model Response", "POST", "ai/generate", 200, data=data)

    def test_ai_smart_selection(self):
        """Test /api/ai/smart-selection - Automatic model selection"""
        data = {
            "task_type": "business",
            "prompt": "Analyze the lead conversion rate for our green building consultancy and suggest improvements"
        }
        return self.run_test("AI Smart Selection - Auto Model Selection", "POST", "ai/smart-selection", 200, data=data)

    def test_ai_analyze_conversation(self):
        """Test /api/ai/analyze-conversation - Conversation analysis"""
        data = {
            "conversation": [
                {"speaker": "customer", "message": "Hi, I'm interested in setting up a balcony garden"},
                {"speaker": "agent", "message": "Great! What's your space size and budget?"},
                {"speaker": "customer", "message": "It's a 2 BHK balcony, around 50k budget"}
            ],
            "context": "lead_qualification"
        }
        return self.run_test("AI Analyze Conversation - Lead Analysis", "POST", "ai/analyze-conversation", 200, data=data)

    def test_ai_generate_proposal(self):
        """Test /api/ai/generate-proposal - Smart proposal generation"""
        data = {
            "lead_data": {
                "name": "Rajesh Kumar",
                "location": "Mumbai",
                "budget": 50000,
                "space_size": "2 BHK Balcony",
                "requirements": "Low maintenance plants, automated watering"
            },
            "service_type": "balcony_garden_setup"
        }
        return self.run_test("AI Generate Proposal - Smart Proposals", "POST", "ai/generate-proposal", 200, data=data)

    def test_ai_optimize_workflow(self):
        """Test /api/ai/optimize-workflow - Workflow optimization"""
        data = {
            "workflow_name": "Lead Nurturing Process",
            "current_steps": [
                "Initial Contact",
                "Requirement Gathering", 
                "Site Visit",
                "Proposal Creation",
                "Follow-up"
            ],
            "performance_metrics": {
                "conversion_rate": 25,
                "avg_cycle_time": 14
            }
        }
        return self.run_test("AI Optimize Workflow - Process Optimization", "POST", "ai/optimize-workflow", 200, data=data)

    def test_ai_marketing_content(self):
        """Test /api/ai/marketing-content - Marketing content generation"""
        data = {
            "campaign_type": "social_media",
            "target_audience": "urban_homeowners",
            "service": "balcony_gardens",
            "tone": "professional_friendly",
            "platform": "instagram"
        }
        return self.run_test("AI Marketing Content - Content Generation", "POST", "ai/marketing-content", 200, data=data)

    def test_ai_predict_deals(self):
        """Test /api/ai/predict-deals - Deal closure prediction"""
        data = [
            {
                "lead_id": "lead_001",
                "name": "Priya Sharma",
                "budget": 75000,
                "engagement_score": 8,
                "days_in_pipeline": 12,
                "interactions": 5
            },
            {
                "lead_id": "lead_002", 
                "name": "Amit Patel",
                "budget": 30000,
                "engagement_score": 6,
                "days_in_pipeline": 25,
                "interactions": 3
            }
        ]
        return self.run_test("AI Predict Deals - Closure Prediction", "POST", "ai/predict-deals", 200, data=data)

    def test_ai_task_automation(self):
        """Test /api/ai/task-automation - Task automation suggestions"""
        data = {
            "task_type": "follow_up",
            "lead_data": {
                "name": "Customer Name",
                "status": "Qualified",
                "last_interaction": "2024-01-15",
                "interest_level": "high"
            },
            "context": "post_site_visit"
        }
        return self.run_test("AI Task Automation - Automation Suggestions", "POST", "ai/task-automation", 200, data=data)

    # HRMS Camera API Testing
    def test_hrms_face_checkin(self):
        """Test /api/hrms/face-checkin - Face recognition check-in"""
        # Create mock image data (base64 encoded small image)
        mock_image_data = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
        
        data = {
            "employee_id": "emp_001",
            "image_data": mock_image_data,
            "location": {
                "latitude": 19.0760,
                "longitude": 72.8777
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        return self.run_test("HRMS Face Check-in - Face Recognition", "POST", "hrms/face-checkin", 200, data=data)

    def test_hrms_gps_checkin(self):
        """Test /api/hrms/gps-checkin - GPS-based check-in"""
        data = {
            "employee_id": "emp_001",
            "location": {
                "latitude": 19.0760,
                "longitude": 72.8777,
                "accuracy": 10
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "check_type": "check_in"
        }
        return self.run_test("HRMS GPS Check-in - Location Based", "POST", "hrms/gps-checkin", 200, data=data)

    # File Upload API Testing
    def test_file_upload(self):
        """Test /api/upload/file - Enhanced file upload with chunked support"""
        # Create mock file data
        mock_file_content = "This is a test file content for upload testing"
        
        data = {
            "file_name": "test_document.txt",
            "file_size": len(mock_file_content),
            "file_type": "text/plain",
            "chunk_index": 0,
            "total_chunks": 1,
            "file_data": mock_file_content,
            "upload_id": str(uuid.uuid4())
        }
        return self.run_test("File Upload - Enhanced Upload System", "POST", "upload/file", 200, data=data)

    # Workflow Templates Testing
    def test_workflow_templates_get(self):
        """Test /api/workflow-templates - Template management (GET)"""
        return self.run_test("Workflow Templates - Get Templates", "GET", "workflow-templates", 200)

    def test_workflow_templates_create(self):
        """Test workflow template creation"""
        data = {
            "name": "Lead Qualification Workflow",
            "description": "Automated workflow for qualifying new leads",
            "category": "lead_management",
            "steps": [
                {
                    "type": "ai_response",
                    "name": "Initial Assessment",
                    "config": {
                        "prompt": "Assess lead quality based on provided information",
                        "model": "gpt-5"
                    }
                },
                {
                    "type": "send_message",
                    "name": "Welcome Message",
                    "config": {
                        "template": "Welcome to Aavana Greens! We'll help you create your dream garden."
                    }
                }
            ],
            "trigger_conditions": {
                "source": "website_form",
                "budget_min": 25000
            }
        }
        return self.run_test("Workflow Templates - Create Template", "POST", "workflows", 200, data=data)

    # Core CRM APIs Testing
    def test_leads_api(self):
        """Test /api/leads - Lead management"""
        # Test GET leads
        success_get, _ = self.run_test("Core CRM - Get Leads", "GET", "leads", 200)
        
        # Test POST lead
        lead_data = {
            "name": "Test Customer",
            "phone": "9876543210",
            "email": "test@example.com",
            "budget": 60000,
            "space_size": "3 BHK",
            "location": "Mumbai",
            "source": "Website",
            "category": "Residential",
            "notes": "Interested in complete balcony transformation"
        }
        success_post, response = self.run_test("Core CRM - Create Lead", "POST", "leads", 200, data=lead_data)
        
        return success_get and success_post, response

    def test_tasks_api(self):
        """Test /api/tasks - Task management"""
        # Test GET tasks
        success_get, _ = self.run_test("Core CRM - Get Tasks", "GET", "tasks", 200)
        
        # Test POST task
        task_data = {
            "title": "Follow up with new lead",
            "description": "Call the customer to discuss requirements",
            "priority": "High",
            "assigned_to": "Sales Team",
            "due_date": "2024-12-31T10:00:00Z"
        }
        success_post, response = self.run_test("Core CRM - Create Task", "POST", "tasks", 200, data=task_data)
        
        return success_get and success_post, response

    def test_auth_login(self):
        """Test /api/auth/login - Authentication"""
        # Try with demo credentials
        login_data = {
            "identifier": "admin",
            "password": "admin123"
        }
        success, response = self.run_test("Core CRM - Authentication Login", "POST", "auth/login", 200, data=login_data)
        
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            
        return success, response

    # Comprehensive AI Stack Integration Tests
    def test_ai_crm_smart_lead_scoring(self):
        """Test AI CRM - Smart Lead Scoring"""
        return self.run_test("AI CRM - Smart Lead Scoring", "POST", "ai/crm/smart-lead-scoring", 200, params={"lead_id": "demo_lead_001"})

    def test_ai_crm_conversation_analysis(self):
        """Test AI CRM - Conversation Analysis"""
        data = {
            "conversation_id": "conv_001",
            "messages": [
                {"role": "customer", "content": "I want a beautiful garden for my balcony"},
                {"role": "agent", "content": "What's your budget and space size?"},
                {"role": "customer", "content": "Around 40k for a 2 BHK balcony"}
            ]
        }
        return self.run_test("AI CRM - Conversation Analysis", "POST", "ai/crm/conversation-analysis", 200, data=data)

    def test_ai_sales_deal_prediction(self):
        """Test AI Sales - Deal Prediction"""
        return self.run_test("AI Sales - Deal Prediction", "POST", "ai/sales/deal-prediction", 200)

    def test_ai_sales_smart_proposal_generator(self):
        """Test AI Sales - Smart Proposal Generator"""
        return self.run_test("AI Sales - Smart Proposal Generator", "POST", "ai/sales/smart-proposal-generator", 200, 
                           params={"lead_id": "demo_lead_001", "service_type": "balcony_garden"})

    def test_ai_marketing_campaign_optimizer(self):
        """Test AI Marketing - Campaign Optimizer"""
        data = {
            "campaign_name": "Summer Garden Campaign",
            "target_audience": "urban_homeowners",
            "budget": 50000,
            "channels": ["google_ads", "facebook", "instagram"],
            "goals": ["lead_generation", "brand_awareness"]
        }
        return self.run_test("AI Marketing - Campaign Optimizer", "POST", "ai/marketing/campaign-optimizer", 200, data=data)

    def test_ai_marketing_competitor_analysis(self):
        """Test AI Marketing - Competitor Analysis"""
        return self.run_test("AI Marketing - Competitor Analysis", "POST", "ai/marketing/competitor-analysis", 200, 
                           params={"location": "Mumbai"})

    def test_health_check(self):
        """Test basic API health"""
        return self.run_test("API Health Check", "GET", "", 200)

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        return self.run_test("Dashboard Statistics", "GET", "dashboard/stats", 200)

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE AI BACKEND TEST REPORT")
        print("="*80)
        
        # Overall Statistics
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"   Total Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Categorize results
        ai_tests = [r for r in self.test_results if 'AI' in r['test_name']]
        hrms_tests = [r for r in self.test_results if 'HRMS' in r['test_name']]
        file_tests = [r for r in self.test_results if 'File' in r['test_name']]
        workflow_tests = [r for r in self.test_results if 'Workflow' in r['test_name']]
        crm_tests = [r for r in self.test_results if 'CRM' in r['test_name']]
        
        # Category-wise results
        categories = [
            ("🤖 AI ENDPOINTS", ai_tests),
            ("👤 HRMS CAMERA API", hrms_tests), 
            ("📁 FILE UPLOAD API", file_tests),
            ("⚙️ WORKFLOW TEMPLATES", workflow_tests),
            ("📊 CORE CRM APIs", crm_tests)
        ]
        
        for category_name, tests in categories:
            if tests:
                passed = len([t for t in tests if t['success']])
                total = len(tests)
                rate = (passed / total * 100) if total > 0 else 0
                print(f"\n{category_name}:")
                print(f"   Tests: {passed}/{total} passed ({rate:.1f}%)")
                
                # Show failed tests
                failed_tests = [t for t in tests if not t['success']]
                if failed_tests:
                    print(f"   ❌ Failed Tests:")
                    for test in failed_tests:
                        print(f"      - {test['test_name']} (Status: {test['status_code']})")
        
        # Critical Issues
        critical_failures = [r for r in self.test_results if not r['success'] and r['status_code'] in [500, 502, 503]]
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES:")
            for failure in critical_failures:
                print(f"   - {failure['test_name']}: {failure['error']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if success_rate >= 90:
            print("   ✅ Excellent! Backend is production-ready.")
        elif success_rate >= 75:
            print("   ⚠️ Good performance, minor issues to address.")
        else:
            print("   ❌ Significant issues found, requires attention.")
            
        if critical_failures:
            print("   🔧 Fix critical server errors (500/502/503) immediately.")
            
        return success_rate

def main():
    print("🚀 Starting Comprehensive AI Backend Testing")
    print("🎯 Focus: Enhanced AI Endpoints, HRMS Camera, File Upload, Workflow Templates, Core CRM")
    print("="*80)
    
    tester = ComprehensiveAIBackendTester()
    
    # Test 1: Basic Health Check
    print("\n🏥 BASIC HEALTH CHECKS")
    print("-" * 40)
    success, _ = tester.test_health_check()
    if not success:
        print("❌ API Health check failed, continuing with other tests...")
    
    tester.test_dashboard_stats()
    
    # Test 2: Enhanced AI Endpoints (8 new endpoints)
    print("\n🤖 ENHANCED AI ENDPOINTS TESTING")
    print("-" * 40)
    tester.test_ai_generate()
    tester.test_ai_smart_selection()
    tester.test_ai_analyze_conversation()
    tester.test_ai_generate_proposal()
    tester.test_ai_optimize_workflow()
    tester.test_ai_marketing_content()
    tester.test_ai_predict_deals()
    tester.test_ai_task_automation()
    
    # Test 3: HRMS Camera API
    print("\n👤 HRMS CAMERA API TESTING")
    print("-" * 40)
    tester.test_hrms_face_checkin()
    tester.test_hrms_gps_checkin()
    
    # Test 4: File Upload API
    print("\n📁 FILE UPLOAD API TESTING")
    print("-" * 40)
    tester.test_file_upload()
    
    # Test 5: Workflow Templates
    print("\n⚙️ WORKFLOW TEMPLATES TESTING")
    print("-" * 40)
    tester.test_workflow_templates_get()
    tester.test_workflow_templates_create()
    
    # Test 6: Core CRM APIs
    print("\n📊 CORE CRM APIs TESTING")
    print("-" * 40)
    tester.test_auth_login()
    tester.test_leads_api()
    tester.test_tasks_api()
    
    # Test 7: Comprehensive AI Stack Integration
    print("\n🧠 COMPREHENSIVE AI STACK INTEGRATION")
    print("-" * 40)
    tester.test_ai_crm_smart_lead_scoring()
    tester.test_ai_crm_conversation_analysis()
    tester.test_ai_sales_deal_prediction()
    tester.test_ai_sales_smart_proposal_generator()
    tester.test_ai_marketing_campaign_optimizer()
    tester.test_ai_marketing_competitor_analysis()
    
    # Generate comprehensive report
    success_rate = tester.generate_test_report()
    
    # Return appropriate exit code
    if success_rate >= 75:
        print("\n🎉 Backend testing completed successfully!")
        return 0
    else:
        print("\n⚠️ Backend testing completed with issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())