import requests
import sys
import json
from datetime import datetime, timezone
import uuid

class AavanaGreensAIStackTester:
    def __init__(self, base_url="https://aavana-workspace.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.test_lead_id = None
        self.test_client_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict):
                        # Show key fields for AI responses
                        if 'lead_scoring' in response_data:
                            print(f"   AI Response: Lead scoring completed")
                        elif 'conversation_analysis' in response_data:
                            print(f"   AI Response: Conversation analysis completed")
                        elif 'deal_predictions' in response_data:
                            print(f"   AI Response: Deal predictions generated")
                        elif 'proposal' in response_data:
                            print(f"   AI Response: Proposal generated")
                        elif 'campaign_optimization' in response_data:
                            print(f"   AI Response: Campaign optimization completed")
                        elif 'competitor_analysis' in response_data:
                            print(f"   AI Response: Competitor analysis completed")
                        elif 'catalog_optimization' in response_data:
                            print(f"   AI Response: Catalog optimization completed")
                        elif 'design_suggestions' in response_data:
                            print(f"   AI Response: Design suggestions generated")
                        elif 'performance_analysis' in response_data:
                            print(f"   AI Response: Performance analysis completed")
                        elif 'smart_schedule' in response_data:
                            print(f"   AI Response: Smart schedule generated")
                        elif 'business_intelligence' in response_data:
                            print(f"   AI Response: Business intelligence report generated")
                        elif 'predictive_forecast' in response_data:
                            print(f"   AI Response: Predictive forecast completed")
                        elif 'workflow_optimization' in response_data:
                            print(f"   AI Response: Workflow optimization completed")
                        elif 'smart_notifications' in response_data:
                            print(f"   AI Response: Smart notifications generated")
                        elif 'response' in response_data:
                            print(f"   AI Response: Global assistant responded")
                        elif 'context' in response_data:
                            print(f"   AI Response: Context recalled successfully")
                        else:
                            print(f"   Response: {str(response_data)[:100]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'endpoint': endpoint
                })
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            self.failed_tests.append({
                'name': name,
                'error': str(e),
                'endpoint': endpoint
            })
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def setup_test_data(self):
        """Create test lead for AI endpoints that need lead_id"""
        print("\n🔧 Setting up test data...")
        
        # Create a test lead
        test_lead = {
            "name": "Arjun Mehta",
            "phone": "9876543210",
            "email": "arjun.mehta@example.com",
            "budget": 800000,
            "space_size": "3 BHK Apartment",
            "location": "Mumbai",
            "source": "Google Ads",
            "category": "Residential",
            "notes": "Interested in complete balcony garden setup and green building consultation",
            "tags": ["premium", "eco-conscious", "urgent"]
        }
        
        success, response = self.run_test("Setup Test Lead", "POST", "leads", 200, data=test_lead)
        if success and 'id' in response:
            self.test_lead_id = response['id']
            self.test_client_id = response['id']  # Use same ID for client context
            print(f"   Test Lead ID: {self.test_lead_id}")
            return True
        return False

    def test_conversational_crm_ai(self):
        """Test Conversational CRM AI endpoints"""
        print("\n🤖 Testing Conversational CRM AI Features...")
        
        # Test 1: Smart Lead Scoring
        if self.test_lead_id:
            self.run_test(
                "AI Smart Lead Scoring", 
                "POST", 
                f"ai/crm/smart-lead-scoring?lead_id={self.test_lead_id}", 
                200
            )
        
        # Test 2: Conversation Analysis
        conversation_data = {
            "conversation": [
                {
                    "speaker": "customer",
                    "message": "Hi, I'm interested in setting up a balcony garden for my 3 BHK apartment in Mumbai. What would be the cost?",
                    "timestamp": "2024-12-20T10:00:00Z"
                },
                {
                    "speaker": "agent",
                    "message": "Hello! I'd be happy to help you with a balcony garden setup. For a 3 BHK apartment, we typically recommend a combination of vertical gardens and planters. The cost usually ranges from ₹50,000 to ₹1,50,000 depending on the complexity.",
                    "timestamp": "2024-12-20T10:01:00Z"
                },
                {
                    "speaker": "customer", 
                    "message": "That sounds reasonable. I'm also interested in making my apartment more eco-friendly overall. Do you provide green building consultation?",
                    "timestamp": "2024-12-20T10:02:00Z"
                }
            ],
            "customer_info": {
                "name": "Arjun Mehta",
                "location": "Mumbai",
                "property_type": "3 BHK Apartment"
            }
        }
        
        self.run_test(
            "AI Conversation Analysis", 
            "POST", 
            "ai/crm/conversation-analysis", 
            200, 
            data=conversation_data
        )
        
        # Test 3: Recall Context
        if self.test_client_id:
            self.run_test(
                "AI Recall Context", 
                "GET", 
                f"ai/recall-context/{self.test_client_id}", 
                200,
                params={"query": "What are this client's preferences and requirements?"}
            )

    def test_sales_pipeline_ai(self):
        """Test Sales & Pipeline AI endpoints"""
        print("\n💼 Testing Sales & Pipeline AI Features...")
        
        # Test 1: Deal Prediction
        self.run_test(
            "AI Deal Prediction", 
            "POST", 
            "ai/sales/deal-prediction", 
            200
        )
        
        # Test 2: Smart Proposal Generator
        if self.test_lead_id:
            self.run_test(
                "AI Smart Proposal Generator", 
                "POST", 
                f"ai/sales/smart-proposal-generator?lead_id={self.test_lead_id}&service_type=balcony_garden", 
                200
            )

    def test_marketing_growth_ai(self):
        """Test Marketing & Growth AI endpoints"""
        print("\n📈 Testing Marketing & Growth AI Features...")
        
        # Test 1: Campaign Optimizer
        campaign_data = {
            "campaign_name": "Mumbai Balcony Gardens Winter Campaign",
            "target_audience": "Urban homeowners in Mumbai, age 25-45, interested in gardening",
            "budget": 100000,
            "duration": "30 days",
            "channels": ["Google Ads", "Facebook", "Instagram", "WhatsApp"],
            "objectives": ["Lead Generation", "Brand Awareness", "Service Promotion"],
            "current_performance": {
                "impressions": 50000,
                "clicks": 2500,
                "conversions": 125,
                "cost_per_click": 15
            }
        }
        
        self.run_test(
            "AI Campaign Optimizer", 
            "POST", 
            "ai/marketing/campaign-optimizer", 
            200, 
            data=campaign_data
        )
        
        # Test 2: Competitor Analysis
        self.run_test(
            "AI Competitor Analysis", 
            "POST", 
            "ai/marketing/competitor-analysis?location=Mumbai", 
            200
        )

    def test_product_project_ai(self):
        """Test Product & Project AI endpoints"""
        print("\n🌱 Testing Product & Project AI Features...")
        
        # Test 1: Smart Catalog
        self.run_test(
            "AI Smart Catalog", 
            "POST", 
            "ai/product/smart-catalog", 
            200
        )
        
        # Test 2: Design Suggestions
        project_requirements = {
            "space_type": "Balcony",
            "space_size": "8x6 feet",
            "location": "Mumbai",
            "sunlight": "Morning sun, partial shade afternoon",
            "budget": 75000,
            "maintenance_level": "Medium",
            "preferences": ["Flowering plants", "Herbs", "Low maintenance", "Air purifying"],
            "special_requirements": ["Pet-friendly plants", "Vertical garden elements"],
            "client_lifestyle": "Working professional, weekend gardener"
        }
        
        self.run_test(
            "AI Design Suggestions", 
            "POST", 
            "ai/project/design-suggestions", 
            200, 
            data=project_requirements
        )

    def test_analytics_admin_ai(self):
        """Test Analytics & Admin AI endpoints"""
        print("\n📊 Testing Analytics & Admin AI Features...")
        
        # Test 1: Business Intelligence
        self.run_test(
            "AI Business Intelligence", 
            "POST", 
            "ai/analytics/business-intelligence", 
            200
        )
        
        # Test 2: Predictive Forecasting
        self.run_test(
            "AI Predictive Forecasting - Revenue", 
            "POST", 
            "ai/analytics/predictive-forecasting?forecast_type=revenue", 
            200
        )
        
        # Test 3: Predictive Forecasting - Demand
        self.run_test(
            "AI Predictive Forecasting - Demand", 
            "POST", 
            "ai/analytics/predictive-forecasting?forecast_type=demand", 
            200
        )

    def test_hr_team_operations_ai(self):
        """Test HR & Team Operations AI endpoints"""
        print("\n👥 Testing HR & Team Operations AI Features...")
        
        # Test 1: Performance Analysis
        self.run_test(
            "AI Performance Analysis", 
            "POST", 
            "ai/hr/performance-analysis", 
            200
        )
        
        # Test 2: Smart Scheduling
        scheduling_requirements = {
            "department": "Field Operations",
            "date_range": {
                "start": "2024-12-23",
                "end": "2024-12-29"
            },
            "projects": [
                {
                    "project_id": "PROJ001",
                    "location": "Bandra, Mumbai",
                    "type": "Balcony Garden Installation",
                    "duration": "4 hours",
                    "skills_required": ["Garden Design", "Plant Installation"],
                    "priority": "High"
                },
                {
                    "project_id": "PROJ002", 
                    "location": "Andheri, Mumbai",
                    "type": "Maintenance Visit",
                    "duration": "2 hours",
                    "skills_required": ["Plant Care", "Maintenance"],
                    "priority": "Medium"
                }
            ],
            "team_availability": {
                "total_team_members": 8,
                "available_skills": ["Garden Design", "Plant Installation", "Maintenance", "Consultation"]
            }
        }
        
        self.run_test(
            "AI Smart Scheduling", 
            "POST", 
            "ai/hr/smart-scheduling", 
            200, 
            data=scheduling_requirements
        )

    def test_automation_layer_ai(self):
        """Test Automation Layer AI endpoints"""
        print("\n⚙️ Testing Automation Layer AI Features...")
        
        # Test 1: Workflow Optimization
        self.run_test(
            "AI Workflow Optimization - Sales", 
            "POST", 
            "ai/automation/workflow-optimization", 
            200, 
            data={"department": "Sales"}
        )
        
        self.run_test(
            "AI Workflow Optimization - Operations", 
            "POST", 
            "ai/automation/workflow-optimization", 
            200, 
            data={"department": "Operations"}
        )
        
        # Test 2: Smart Notifications
        self.run_test(
            "AI Smart Notifications", 
            "POST", 
            "ai/automation/smart-notifications", 
            200
        )

    def test_global_ai_assistant(self):
        """Test Global AI Assistant endpoint"""
        print("\n🌐 Testing Global AI Assistant...")
        
        # Test various types of queries
        test_queries = [
            {
                "message": "What's the status of our current sales pipeline?",
                "context": {"user_role": "Sales Manager", "department": "Sales"}
            },
            {
                "message": "How can we improve our lead conversion rate?",
                "context": {"user_role": "Business Owner", "focus_area": "Growth"}
            },
            {
                "message": "What are the best plants for a north-facing balcony in Mumbai?",
                "context": {"user_role": "Consultant", "client_query": True}
            },
            {
                "message": "Generate a marketing strategy for the upcoming monsoon season",
                "context": {"user_role": "Marketing Manager", "season": "Monsoon"}
            }
        ]
        
        for i, query in enumerate(test_queries):
            self.run_test(
                f"AI Global Assistant - Query {i+1}", 
                "POST", 
                "ai/chat/global-assistant", 
                200, 
                data=query
            )

    def test_ai_model_integration(self):
        """Test that AI models are properly integrated"""
        print("\n🧠 Testing AI Model Integration...")
        
        # Test basic AI endpoints to ensure models are working
        basic_ai_tests = [
            {
                "name": "Voice to Task Processing",
                "endpoint": "ai/voice-to-task",
                "data": {
                    "voice_input": "Schedule a follow-up call with the Mumbai client tomorrow at 2 PM to discuss their balcony garden requirements",
                    "context": {"user": "Sales Team", "priority": "high"}
                }
            },
            {
                "name": "AI Insights Generation",
                "endpoint": "ai/insights", 
                "data": {
                    "type": "leads",
                    "timeframe": "current",
                    "data": {"focus": "conversion_optimization"}
                }
            },
            {
                "name": "Content Generation",
                "endpoint": "ai/generate-content",
                "data": {
                    "type": "social_post",
                    "topic": "Winter gardening tips for Mumbai balconies",
                    "target_audience": "Urban homeowners interested in balcony gardening"
                }
            }
        ]
        
        for test in basic_ai_tests:
            self.run_test(
                test["name"], 
                "POST", 
                test["endpoint"], 
                200, 
                data=test["data"]
            )

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        if self.test_lead_id:
            self.run_test("Cleanup Test Lead", "DELETE", f"leads/{self.test_lead_id}", 200)

    def run_comprehensive_ai_tests(self):
        """Run all AI stack tests"""
        print("🚀 Starting Comprehensive AI Stack Integration Tests")
        print("=" * 60)
        
        # Setup test data
        if not self.setup_test_data():
            print("❌ Failed to setup test data, some tests may fail")
        
        # Run all AI test suites
        self.test_conversational_crm_ai()
        self.test_sales_pipeline_ai()
        self.test_marketing_growth_ai()
        self.test_product_project_ai()
        self.test_analytics_admin_ai()
        self.test_hr_team_operations_ai()
        self.test_automation_layer_ai()
        self.test_global_ai_assistant()
        self.test_ai_model_integration()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Final Results
        print("\n" + "=" * 60)
        print(f"📊 COMPREHENSIVE AI STACK TEST RESULTS")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS SUMMARY:")
            for failure in self.failed_tests:
                if 'error' in failure:
                    print(f"   • {failure['name']}: {failure['error']}")
                else:
                    print(f"   • {failure['name']}: Expected {failure['expected']}, got {failure['actual']}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All AI stack tests passed! AI integration is working correctly.")
            return 0
        else:
            print("⚠️ Some AI tests failed. Please check the AI service implementation.")
            return 1

def main():
    tester = AavanaGreensAIStackTester()
    return tester.run_comprehensive_ai_tests()

if __name__ == "__main__":
    sys.exit(main())