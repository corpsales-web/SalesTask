#!/usr/bin/env python3
"""
Workflow Authoring Backend Testing
Tests the complete workflow creation and management functionality
"""

import requests
import json
import sys
from datetime import datetime, timezone
import uuid

class WorkflowAuthoringTester:
    def __init__(self, base_url="https://aavana-greens.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_workflows = []
        self.created_templates = []
        self.auth_token = None
        self.test_user_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

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
        
        # Create test user
        import time
        timestamp = str(int(time.time()))
        user_data = {
            "username": f"workflow_tester_{timestamp}",
            "email": f"workflow_tester_{timestamp}@example.com",
            "phone": f"987654{timestamp[-4:]}",
            "full_name": "Workflow Tester",
            "role": "Admin",
            "password": "WorkflowTest123!",
            "department": "Testing"
        }
        
        success, response = self.run_test("Create Test User", "POST", "auth/register", 200, data=user_data)
        if success and 'id' in response:
            self.test_user_id = response['id']
            
            # Login to get token
            login_data = {
                "identifier": user_data['username'],
                "password": user_data['password']
            }
            success, login_response = self.run_test("Login Test User", "POST", "auth/login", 200, data=login_data)
            if success and 'access_token' in login_response:
                self.auth_token = login_response['access_token']
                return True
        
        return False

    def get_auth_headers(self):
        """Get headers with authentication token"""
        if self.auth_token:
            return {'Authorization': f'Bearer {self.auth_token}'}
        return {}

    def test_create_prompt_template(self):
        """Test creating a GPT-5 prompt template"""
        template_data = {
            "name": "WhatsApp Lead Nurturing Template",
            "description": "Template for nurturing leads via WhatsApp messages",
            "category": "lead_nurturing",
            "system_prompt": "You are an expert sales assistant for Aavana Greens, a green building and landscaping company. Your role is to nurture leads through personalized WhatsApp messages.",
            "user_prompt_template": "Create a personalized WhatsApp message for {lead_name} who is interested in {service_type} with a budget of ₹{budget}. Their location is {location} and they have {space_size} space. Make it friendly, informative, and include a call-to-action.",
            "variables": ["lead_name", "service_type", "budget", "location", "space_size"],
            "ai_model": "gpt-5",
            "temperature": 0.7,
            "max_tokens": 500,
            "tags": ["whatsapp", "lead_nurturing", "personalized"],
            "is_active": True
        }
        
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Create Prompt Template", 
            "POST", 
            "workflows/prompt-templates", 
            200, 
            data=template_data,
            headers=headers
        )
        
        if success and response.get('success') and 'template_id' in response:
            self.created_templates.append(response['template_id'])
            return True, response
        return False, {}

    def test_get_prompt_templates(self):
        """Test getting prompt templates"""
        headers = self.get_auth_headers()
        return self.run_test(
            "Get Prompt Templates", 
            "GET", 
            "workflows/prompt-templates", 
            200,
            headers=headers
        )

    def test_prompt_template_with_category(self):
        """Test getting prompt templates by category"""
        headers = self.get_auth_headers()
        return self.run_test(
            "Get Prompt Templates by Category", 
            "GET", 
            "workflows/prompt-templates", 
            200,
            params={"category": "lead_nurturing"},
            headers=headers
        )

    def test_prompt_template_testing(self):
        """Test a prompt template with sample data"""
        if not self.created_templates:
            print("⚠️ Skipping test - no template available")
            return False, {}
        
        template_id = self.created_templates[0]
        test_data = {
            "variables": {
                "lead_name": "Rajesh Kumar",
                "service_type": "balcony garden setup",
                "budget": "50000",
                "location": "Mumbai",
                "space_size": "2 BHK balcony"
            }
        }
        
        headers = self.get_auth_headers()
        return self.run_test(
            "Test Prompt Template", 
            "POST", 
            f"workflows/prompt-templates/{template_id}/test", 
            200,
            data=test_data,
            headers=headers
        )

    def test_create_workflow(self):
        """Test creating a complete workflow"""
        workflow_data = {
            "name": "Test WhatsApp Lead Nurturing",
            "description": "Test workflow for lead nurturing via WhatsApp with AI responses",
            "category": "lead_nurturing",
            "trigger_conditions": {
                "lead_source": "whatsapp",
                "lead_status": "new"
            },
            "steps": [
                {
                    "type": "ai_response",
                    "name": "Generate Welcome Message",
                    "prompt": "Create a personalized welcome message for {lead_name} who contacted us about {service_interest}. Make it warm and professional.",
                    "ai_model": "gpt-5",
                    "temperature": 0.7,
                    "max_tokens": 300
                },
                {
                    "type": "send_message",
                    "name": "Send WhatsApp Welcome",
                    "message_template": "Hi {lead_name}! Thanks for your interest in Aavana Greens. {ai_response}",
                    "channel": "whatsapp"
                },
                {
                    "type": "wait_for_response",
                    "name": "Wait for Lead Response",
                    "timeout": 3600
                },
                {
                    "type": "conditional",
                    "name": "Check Response Type",
                    "conditions": [
                        {
                            "variable": "response_received",
                            "operator": "equals",
                            "value": True
                        }
                    ]
                },
                {
                    "type": "assign_agent",
                    "name": "Assign to Sales Team",
                    "agent_criteria": {
                        "department": "sales",
                        "availability": "available"
                    }
                },
                {
                    "type": "schedule_followup",
                    "name": "Schedule Follow-up Call",
                    "delay": 86400,
                    "action_type": "call"
                }
            ],
            "global_variables": {
                "company_name": "Aavana Greens",
                "contact_number": "+91-9876543210",
                "website": "www.aavanagreens.com"
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
            "Create Workflow", 
            "POST", 
            "workflows", 
            200,
            data=workflow_data,
            headers=headers
        )
        
        if success and response.get('success') and 'workflow_id' in response:
            self.created_workflows.append(response['workflow_id'])
            return True, response
        return False, {}

    def test_get_workflows(self):
        """Test getting all workflows"""
        headers = self.get_auth_headers()
        return self.run_test(
            "Get All Workflows", 
            "GET", 
            "workflows", 
            200,
            headers=headers
        )

    def test_get_workflows_by_category(self):
        """Test getting workflows by category"""
        headers = self.get_auth_headers()
        return self.run_test(
            "Get Workflows by Category", 
            "GET", 
            "workflows", 
            200,
            params={"category": "lead_nurturing"},
            headers=headers
        )

    def test_workflow_testing(self):
        """Test a complete workflow with sample data"""
        if not self.created_workflows:
            print("⚠️ Skipping test - no workflow available")
            return False, {}
        
        workflow_id = self.created_workflows[0]
        test_data = {
            "variables": {
                "lead_name": "Priya Sharma",
                "service_interest": "rooftop garden design",
                "lead_source": "whatsapp",
                "lead_phone": "+91-9876543210",
                "lead_location": "Bangalore"
            }
        }
        
        headers = self.get_auth_headers()
        return self.run_test(
            "Test Workflow Execution", 
            "POST", 
            f"workflows/{workflow_id}/test", 
            200,
            data=test_data,
            headers=headers
        )

    def test_publish_workflow(self):
        """Test publishing a workflow for production use"""
        if not self.created_workflows:
            print("⚠️ Skipping test - no workflow available")
            return False, {}
        
        workflow_id = self.created_workflows[0]
        headers = self.get_auth_headers()
        return self.run_test(
            "Publish Workflow", 
            "POST", 
            f"workflows/{workflow_id}/publish", 
            200,
            headers=headers
        )

    def test_workflow_analytics(self):
        """Test getting workflow analytics"""
        if not self.created_workflows:
            print("⚠️ Skipping test - no workflow available")
            return False, {}
        
        workflow_id = self.created_workflows[0]
        headers = self.get_auth_headers()
        return self.run_test(
            "Get Workflow Analytics", 
            "GET", 
            f"workflows/{workflow_id}/analytics", 
            200,
            headers=headers
        )

    def test_published_workflows_only(self):
        """Test getting only published workflows"""
        headers = self.get_auth_headers()
        return self.run_test(
            "Get Published Workflows Only", 
            "GET", 
            "workflows", 
            200,
            params={"published_only": True},
            headers=headers
        )

    def test_complex_workflow_creation(self):
        """Test creating a more complex workflow with multiple AI steps"""
        complex_workflow_data = {
            "name": "Advanced Lead Qualification Workflow",
            "description": "Multi-step workflow with AI-powered lead qualification and personalized responses",
            "category": "lead_qualification",
            "trigger_conditions": {
                "lead_source": ["website", "facebook", "google_ads"],
                "budget_range": "above_25000"
            },
            "steps": [
                {
                    "type": "ai_response",
                    "name": "Analyze Lead Profile",
                    "prompt": "Analyze this lead profile and determine their qualification score: Name: {lead_name}, Budget: ₹{budget}, Location: {location}, Interest: {service_type}. Provide a score from 1-10 and reasoning.",
                    "ai_model": "gpt-5",
                    "temperature": 0.3,
                    "max_tokens": 400
                },
                {
                    "type": "conditional",
                    "name": "Check Qualification Score",
                    "conditions": [
                        {
                            "variable": "qualification_score",
                            "operator": "greater_than",
                            "value": 7
                        }
                    ]
                },
                {
                    "type": "ai_response",
                    "name": "Generate Personalized Proposal",
                    "prompt": "Create a detailed proposal for {lead_name} interested in {service_type} with budget ₹{budget} in {location}. Include specific recommendations, timeline, and next steps.",
                    "ai_model": "gpt-5",
                    "temperature": 0.5,
                    "max_tokens": 800
                },
                {
                    "type": "send_message",
                    "name": "Send Proposal via Email",
                    "message_template": "Dear {lead_name},\n\nThank you for your interest in Aavana Greens!\n\n{ai_response}\n\nBest regards,\nAavana Greens Team",
                    "channel": "email"
                },
                {
                    "type": "assign_agent",
                    "name": "Assign to Senior Sales Executive",
                    "agent_criteria": {
                        "role": "senior_sales_executive",
                        "specialization": "high_value_leads"
                    }
                },
                {
                    "type": "trigger_notification",
                    "name": "Notify Sales Manager",
                    "notification_type": "high_value_lead",
                    "recipients": ["sales_manager", "assigned_agent"]
                }
            ],
            "global_variables": {
                "company_name": "Aavana Greens",
                "qualification_threshold": 7,
                "high_value_threshold": 100000
            },
            "settings": {
                "auto_assign": True,
                "send_notifications": True,
                "max_execution_time": 10800,
                "retry_on_failure": True,
                "priority": "high"
            },
            "tags": ["lead_qualification", "ai_powered", "high_value", "automated"],
            "is_active": False
        }
        
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Create Complex Workflow", 
            "POST", 
            "workflows", 
            200,
            data=complex_workflow_data,
            headers=headers
        )
        
        if success and response.get('success') and 'workflow_id' in response:
            self.created_workflows.append(response['workflow_id'])
            return True, response
        return False, {}

    def test_error_handling(self):
        """Test error handling with invalid data"""
        print("\n🚫 Testing Error Handling...")
        
        # Test invalid workflow creation
        invalid_workflow = {
            "name": "",  # Empty name should fail
            "steps": []  # Empty steps should fail
        }
        
        headers = self.get_auth_headers()
        self.run_test(
            "Create Invalid Workflow (Empty Name)", 
            "POST", 
            "workflows", 
            400,
            data=invalid_workflow,
            headers=headers
        )
        
        # Test invalid template ID
        self.run_test(
            "Test Non-existent Template", 
            "POST", 
            "workflows/prompt-templates/invalid-id/test", 
            400,
            data={"variables": {}},
            headers=headers
        )
        
        # Test invalid workflow ID
        self.run_test(
            "Test Non-existent Workflow", 
            "POST", 
            "workflows/invalid-id/test", 
            400,
            data={"variables": {}},
            headers=headers
        )

def main():
    print("🚀 Starting Workflow Authoring Backend Tests")
    print("=" * 60)
    
    tester = WorkflowAuthoringTester()

    # Setup authentication
    if not tester.setup_authentication():
        print("❌ Authentication setup failed, stopping tests")
        return 1

    print("\n📋 Testing Prompt Template Management...")
    print("=" * 50)
    
    # Test prompt template creation
    tester.test_create_prompt_template()
    
    # Test getting prompt templates
    tester.test_get_prompt_templates()
    
    # Test getting templates by category
    tester.test_prompt_template_with_category()
    
    # Test prompt template testing
    tester.test_prompt_template_testing()

    print("\n🔄 Testing Workflow Management...")
    print("=" * 50)
    
    # Test workflow creation
    tester.test_create_workflow()
    
    # Test getting workflows
    tester.test_get_workflows()
    
    # Test getting workflows by category
    tester.test_get_workflows_by_category()
    
    # Test workflow testing
    tester.test_workflow_testing()
    
    # Test workflow publishing
    tester.test_publish_workflow()
    
    # Test workflow analytics
    tester.test_workflow_analytics()
    
    # Test getting published workflows only
    tester.test_published_workflows_only()

    print("\n🔧 Testing Advanced Features...")
    print("=" * 50)
    
    # Test complex workflow creation
    tester.test_complex_workflow_creation()
    
    # Test error handling
    tester.test_error_handling()

    # Final Results
    print("\n" + "=" * 60)
    print(f"📊 WORKFLOW AUTHORING TEST RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    print(f"\n📈 Created Resources:")
    print(f"Prompt Templates: {len(tester.created_templates)}")
    print(f"Workflows: {len(tester.created_workflows)}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All workflow authoring tests passed! Backend is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the workflow authoring implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())