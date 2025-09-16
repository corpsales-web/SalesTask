import requests
import sys
import json
from datetime import datetime, timezone
import uuid
import time

class LeadRoutingWorkflowTester:
    def __init__(self, base_url="https://navdebug-crm.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.test_user_id = None
        self.created_routing_rules = []
        self.created_prompt_templates = []
        self.created_workflows = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        default_headers = {'Content-Type': 'application/json'}
        
        if headers:
            default_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def setup_authentication(self):
        """Setup authentication for testing"""
        print("\n🔐 Setting up authentication...")
        
        # Try to login with master user
        login_data = {
            "identifier": "master",
            "password": "master123"
        }
        
        success, response = self.run_test("Master Login", "POST", "auth/login", 200, data=login_data)
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            self.test_user_id = response.get('user', {}).get('id', 'test_user_id')
            print(f"✅ Authentication successful. User ID: {self.test_user_id}")
            return True
        
        print("❌ Authentication failed")
        return False

    def get_auth_headers(self):
        """Get headers with authentication token"""
        if self.auth_token:
            return {'Authorization': f'Bearer {self.auth_token}'}
        return {}

    # Lead Routing API Tests
    def test_create_routing_rule(self):
        """Test creating a lead routing rule"""
        rule_data = {
            "name": "WhatsApp High Value Leads",
            "source": "whatsapp_360dialog",
            "conditions": {
                "budget_range": "high",
                "location": ["Mumbai", "Delhi", "Bangalore"],
                "time_range": {
                    "start": 9,
                    "end": 18
                }
            },
            "target_agent_id": "agent_001",
            "workflow_template_id": None,
            "priority": 1,
            "is_active": True
        }
        
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Create Routing Rule", "POST", "routing/rules", 200, 
            data=rule_data, headers=headers
        )
        
        if success and response.get('success') and response.get('rule_id'):
            self.created_routing_rules.append(response['rule_id'])
            return True, response
        return False, {}

    def test_create_routing_rule_facebook(self):
        """Test creating a routing rule for Facebook leads"""
        rule_data = {
            "name": "Facebook Residential Leads",
            "source": "facebook",
            "conditions": {
                "custom_fields": {
                    "lead_type": "residential"
                }
            },
            "target_team_id": "residential_team",
            "priority": 2,
            "is_active": True
        }
        
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Create Facebook Routing Rule", "POST", "routing/rules", 200,
            data=rule_data, headers=headers
        )
        
        if success and response.get('success') and response.get('rule_id'):
            self.created_routing_rules.append(response['rule_id'])
            return True, response
        return False, {}

    def test_get_routing_rules(self):
        """Test getting all routing rules"""
        headers = self.get_auth_headers()
        return self.run_test(
            "Get All Routing Rules", "GET", "routing/rules", 200,
            headers=headers
        )

    def test_get_routing_rules_by_source(self):
        """Test getting routing rules filtered by source"""
        headers = self.get_auth_headers()
        return self.run_test(
            "Get WhatsApp Routing Rules", "GET", "routing/rules", 200,
            params={"source": "whatsapp_360dialog"}, headers=headers
        )

    def test_route_lead_whatsapp(self):
        """Test routing a WhatsApp lead"""
        lead_data = {
            "id": str(uuid.uuid4()),
            "name": "Rajesh Kumar",
            "phone": "9876543210",
            "email": "rajesh@example.com",
            "source": "whatsapp_360dialog",
            "budget_range": "high",
            "location": "Mumbai",
            "space_size": "3 BHK",
            "notes": "Interested in premium green building solutions"
        }
        
        headers = self.get_auth_headers()
        return self.run_test(
            "Route WhatsApp Lead", "POST", "routing/route-lead", 200,
            data=lead_data, headers=headers
        )

    def test_route_lead_facebook(self):
        """Test routing a Facebook lead"""
        lead_data = {
            "id": str(uuid.uuid4()),
            "name": "Priya Sharma",
            "phone": "8765432109",
            "email": "priya@example.com",
            "source": "facebook",
            "budget_range": "medium",
            "location": "Delhi",
            "lead_type": "residential",
            "space_size": "2 BHK",
            "notes": "Looking for balcony garden setup"
        }
        
        headers = self.get_auth_headers()
        return self.run_test(
            "Route Facebook Lead", "POST", "routing/route-lead", 200,
            data=lead_data, headers=headers
        )

    def test_route_lead_no_rules(self):
        """Test routing a lead with no matching rules (default routing)"""
        lead_data = {
            "id": str(uuid.uuid4()),
            "name": "Amit Patel",
            "phone": "7654321098",
            "email": "amit@example.com",
            "source": "website_organic",
            "budget_range": "low",
            "location": "Pune",
            "space_size": "1 BHK",
            "notes": "First time buyer"
        }
        
        headers = self.get_auth_headers()
        return self.run_test(
            "Route Lead (No Rules)", "POST", "routing/route-lead", 200,
            data=lead_data, headers=headers
        )

    # Workflow Authoring API Tests
    def test_create_prompt_template(self):
        """Test creating a GPT-5 prompt template"""
        template_data = {
            "name": "Lead Qualification Assistant",
            "description": "AI assistant for qualifying incoming leads",
            "category": "lead_qualification",
            "system_prompt": "You are an expert lead qualification assistant for Aavana Greens, a premium green building and landscaping company. Your role is to assess lead quality and provide personalized responses.",
            "user_prompt_template": "Analyze this lead: Name: {lead_name}, Budget: {budget}, Location: {location}, Requirements: {requirements}. Provide qualification score (1-10) and next steps.",
            "variables": ["lead_name", "budget", "location", "requirements"],
            "ai_model": "gpt-5",
            "temperature": 0.7,
            "max_tokens": 1000,
            "functions": [],
            "examples": [
                {
                    "input": {"lead_name": "John Doe", "budget": "50000", "location": "Mumbai", "requirements": "Balcony garden"},
                    "output": "Qualification Score: 8/10. High-value lead with clear requirements."
                }
            ],
            "tags": ["lead_qualification", "ai_assistant", "gpt-5"],
            "is_active": True
        }
        
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Create Prompt Template", "POST", "workflows/prompt-templates", 200,
            data=template_data, headers=headers
        )
        
        if success and response.get('success') and response.get('template_id'):
            self.created_prompt_templates.append(response['template_id'])
            return True, response
        return False, {}

    def test_create_prompt_template_content_generation(self):
        """Test creating a content generation prompt template"""
        template_data = {
            "name": "WhatsApp Response Generator",
            "description": "Generate personalized WhatsApp responses for leads",
            "category": "content_generation",
            "system_prompt": "You are a friendly WhatsApp assistant for Aavana Greens. Generate warm, personalized responses that showcase our green building expertise.",
            "user_prompt_template": "Generate a WhatsApp response for {lead_name} who is interested in {service_type} for their {space_type} in {location}. Budget: {budget}. Keep it conversational and under 160 characters.",
            "variables": ["lead_name", "service_type", "space_type", "location", "budget"],
            "ai_model": "gpt-5",
            "temperature": 0.8,
            "max_tokens": 200,
            "tags": ["whatsapp", "content_generation", "personalization"],
            "is_active": True
        }
        
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Create Content Generation Template", "POST", "workflows/prompt-templates", 200,
            data=template_data, headers=headers
        )
        
        if success and response.get('success') and response.get('template_id'):
            self.created_prompt_templates.append(response['template_id'])
            return True, response
        return False, {}

    def test_get_prompt_templates(self):
        """Test getting all prompt templates"""
        headers = self.get_auth_headers()
        return self.run_test(
            "Get All Prompt Templates", "GET", "workflows/prompt-templates", 200,
            headers=headers
        )

    def test_get_prompt_templates_by_category(self):
        """Test getting prompt templates by category"""
        headers = self.get_auth_headers()
        return self.run_test(
            "Get Lead Qualification Templates", "GET", "workflows/prompt-templates", 200,
            params={"category": "lead_qualification"}, headers=headers
        )

    def test_prompt_template_test(self):
        """Test a prompt template with sample data"""
        if not self.created_prompt_templates:
            print("⚠️ Skipping test - no prompt templates available")
            return False, {}
        
        template_id = self.created_prompt_templates[0]
        test_data = {
            "variables": {
                "lead_name": "Rajesh Kumar",
                "budget": "75000",
                "location": "Mumbai",
                "requirements": "Complete balcony transformation with automated watering system"
            }
        }
        
        headers = self.get_auth_headers()
        return self.run_test(
            "Test Prompt Template", "POST", f"workflows/prompt-templates/{template_id}/test", 200,
            data=test_data, headers=headers
        )

    def test_create_workflow(self):
        """Test creating a complete workflow"""
        workflow_data = {
            "name": "WhatsApp Lead Nurturing Workflow",
            "description": "Automated workflow for nurturing WhatsApp leads with AI-powered responses",
            "category": "lead_nurturing",
            "trigger_conditions": {
                "source": "whatsapp_360dialog",
                "lead_status": "new"
            },
            "steps": [
                {
                    "type": "ai_response",
                    "name": "Initial Greeting",
                    "prompt_template_id": self.created_prompt_templates[1] if len(self.created_prompt_templates) > 1 else None,
                    "ai_model": "gpt-5",
                    "temperature": 0.7
                },
                {
                    "type": "send_message",
                    "name": "Send Welcome Message",
                    "message_template": "Hi {lead_name}! Thanks for your interest in Aavana Greens. {ai_response}",
                    "channel": "whatsapp"
                },
                {
                    "type": "wait_for_response",
                    "name": "Wait for Reply",
                    "timeout": 3600
                },
                {
                    "type": "conditional",
                    "name": "Check Response",
                    "conditions": [
                        {
                            "variable": "user_response",
                            "operator": "contains",
                            "value": "interested"
                        }
                    ]
                },
                {
                    "type": "assign_agent",
                    "name": "Assign to Sales Agent",
                    "agent_criteria": {
                        "department": "sales",
                        "location": "{lead_location}"
                    }
                }
            ],
            "global_variables": {
                "company_name": "Aavana Greens",
                "response_time": "24 hours"
            },
            "settings": {
                "auto_assign": True,
                "send_notifications": True,
                "max_execution_time": 7200,
                "retry_on_failure": True
            },
            "tags": ["whatsapp", "lead_nurturing", "automated"],
            "is_active": False
        }
        
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Create Workflow", "POST", "workflows", 200,
            data=workflow_data, headers=headers
        )
        
        if success and response.get('success') and response.get('workflow_id'):
            self.created_workflows.append(response['workflow_id'])
            return True, response
        return False, {}

    def test_create_workflow_email_followup(self):
        """Test creating an email follow-up workflow"""
        workflow_data = {
            "name": "Email Follow-up Workflow",
            "description": "Automated email follow-up for qualified leads",
            "category": "email_marketing",
            "trigger_conditions": {
                "lead_status": "qualified",
                "days_since_contact": 3
            },
            "steps": [
                {
                    "type": "ai_response",
                    "name": "Generate Email Content",
                    "system_prompt": "Generate a professional follow-up email for a qualified lead interested in green building solutions.",
                    "prompt": "Create an email for {lead_name} who showed interest in {service_type}. Include our latest portfolio and schedule a consultation.",
                    "ai_model": "gpt-5",
                    "temperature": 0.6
                },
                {
                    "type": "send_message",
                    "name": "Send Follow-up Email",
                    "message_template": "{ai_response}",
                    "channel": "email"
                },
                {
                    "type": "schedule_followup",
                    "name": "Schedule Next Follow-up",
                    "delay_days": 7,
                    "action": "phone_call"
                }
            ],
            "tags": ["email", "follow_up", "qualified_leads"],
            "is_active": False
        }
        
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Create Email Workflow", "POST", "workflows", 200,
            data=workflow_data, headers=headers
        )
        
        if success and response.get('success') and response.get('workflow_id'):
            self.created_workflows.append(response['workflow_id'])
            return True, response
        return False, {}

    def test_get_workflows(self):
        """Test getting all workflows"""
        headers = self.get_auth_headers()
        return self.run_test(
            "Get All Workflows", "GET", "workflows", 200,
            headers=headers
        )

    def test_get_workflows_by_category(self):
        """Test getting workflows by category"""
        headers = self.get_auth_headers()
        return self.run_test(
            "Get Lead Nurturing Workflows", "GET", "workflows", 200,
            params={"category": "lead_nurturing"}, headers=headers
        )

    def test_workflow_test(self):
        """Test a workflow with sample data"""
        if not self.created_workflows:
            print("⚠️ Skipping test - no workflows available")
            return False, {}
        
        workflow_id = self.created_workflows[0]
        test_data = {
            "variables": {
                "lead_name": "Priya Sharma",
                "lead_location": "Delhi",
                "service_type": "balcony garden",
                "budget": "45000",
                "user_response": "Yes, I'm very interested in your services"
            }
        }
        
        headers = self.get_auth_headers()
        return self.run_test(
            "Test Workflow", "POST", f"workflows/{workflow_id}/test", 200,
            data=test_data, headers=headers
        )

    def test_publish_workflow(self):
        """Test publishing a workflow"""
        if not self.created_workflows:
            print("⚠️ Skipping test - no workflows available")
            return False, {}
        
        workflow_id = self.created_workflows[0]
        headers = self.get_auth_headers()
        return self.run_test(
            "Publish Workflow", "POST", f"workflows/{workflow_id}/publish", 200,
            headers=headers
        )

    def test_workflow_analytics(self):
        """Test getting workflow analytics"""
        if not self.created_workflows:
            print("⚠️ Skipping test - no workflows available")
            return False, {}
        
        workflow_id = self.created_workflows[0]
        headers = self.get_auth_headers()
        return self.run_test(
            "Get Workflow Analytics", "GET", f"workflows/{workflow_id}/analytics", 200,
            headers=headers
        )

    # Error Handling Tests
    def test_create_routing_rule_invalid_data(self):
        """Test creating routing rule with invalid data"""
        rule_data = {
            "name": "",  # Empty name
            "source": "invalid_source",  # Invalid source
            "priority": "high"  # Invalid priority type
        }
        
        headers = self.get_auth_headers()
        return self.run_test(
            "Create Invalid Routing Rule", "POST", "routing/rules", 400,
            data=rule_data, headers=headers
        )

    def test_create_prompt_template_missing_fields(self):
        """Test creating prompt template with missing required fields"""
        template_data = {
            "description": "Missing name field"
            # Missing required 'name' field
        }
        
        headers = self.get_auth_headers()
        return self.run_test(
            "Create Invalid Prompt Template", "POST", "workflows/prompt-templates", 400,
            data=template_data, headers=headers
        )

    def test_test_nonexistent_template(self):
        """Test testing a non-existent prompt template"""
        fake_template_id = str(uuid.uuid4())
        test_data = {"variables": {"test": "value"}}
        
        headers = self.get_auth_headers()
        return self.run_test(
            "Test Non-existent Template", "POST", f"workflows/prompt-templates/{fake_template_id}/test", 400,
            data=test_data, headers=headers
        )

    def test_publish_nonexistent_workflow(self):
        """Test publishing a non-existent workflow"""
        fake_workflow_id = str(uuid.uuid4())
        headers = self.get_auth_headers()
        return self.run_test(
            "Publish Non-existent Workflow", "POST", f"workflows/{fake_workflow_id}/publish", 400,
            headers=headers
        )

    def test_unauthorized_access(self):
        """Test accessing endpoints without authentication"""
        return self.run_test(
            "Unauthorized Routing Rules Access", "GET", "routing/rules", 401
        )

def main():
    print("🚀 Starting Lead Routing & Workflow Authoring API Tests")
    print("=" * 60)
    
    tester = LeadRoutingWorkflowTester()

    # Setup authentication
    if not tester.setup_authentication():
        print("❌ Authentication setup failed, stopping tests")
        return 1

    # Test Lead Routing APIs
    print("\n📍 Testing Lead Routing APIs...")
    print("=" * 40)
    
    print("\n🔧 Creating Routing Rules...")
    tester.test_create_routing_rule()
    tester.test_create_routing_rule_facebook()
    
    print("\n📋 Getting Routing Rules...")
    tester.test_get_routing_rules()
    tester.test_get_routing_rules_by_source()
    
    print("\n🎯 Testing Lead Routing...")
    tester.test_route_lead_whatsapp()
    tester.test_route_lead_facebook()
    tester.test_route_lead_no_rules()

    # Test Workflow Authoring APIs
    print("\n🤖 Testing Workflow Authoring APIs...")
    print("=" * 40)
    
    print("\n📝 Creating Prompt Templates...")
    tester.test_create_prompt_template()
    tester.test_create_prompt_template_content_generation()
    
    print("\n📋 Getting Prompt Templates...")
    tester.test_get_prompt_templates()
    tester.test_get_prompt_templates_by_category()
    
    print("\n🧪 Testing Prompt Templates...")
    tester.test_prompt_template_test()
    
    print("\n⚙️ Creating Workflows...")
    tester.test_create_workflow()
    tester.test_create_workflow_email_followup()
    
    print("\n📋 Getting Workflows...")
    tester.test_get_workflows()
    tester.test_get_workflows_by_category()
    
    print("\n🧪 Testing Workflows...")
    tester.test_workflow_test()
    
    print("\n🚀 Publishing Workflows...")
    tester.test_publish_workflow()
    
    print("\n📊 Getting Analytics...")
    tester.test_workflow_analytics()

    # Test Error Handling
    print("\n🚫 Testing Error Handling...")
    print("=" * 40)
    tester.test_create_routing_rule_invalid_data()
    tester.test_create_prompt_template_missing_fields()
    tester.test_test_nonexistent_template()
    tester.test_publish_nonexistent_workflow()
    tester.test_unauthorized_access()

    # Final Results
    print("\n" + "=" * 60)
    print(f"📊 FINAL TEST RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Lead Routing & Workflow Authoring APIs are working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())