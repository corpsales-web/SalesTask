#!/usr/bin/env python3
"""
Comprehensive Backend Audit - All Endpoints and Functionality
Testing all HRMS, Task Management, Lead Management, AI Stack, ERP, Voice, Workflow, and Notification APIs
"""

import requests
import json
import time
import uuid
import sys
from datetime import datetime, timezone, timedelta
import base64
import os

class ComprehensiveBackendAudit:
    def __init__(self, base_url="https://green-crm-suite.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.critical_failures = []
        self.auth_token = None
        self.test_user_id = None
        self.created_resources = {
            'leads': [],
            'tasks': [],
            'users': [],
            'workflows': [],
            'templates': [],
            'routing_rules': []
        }
        
        # Test data
        self.test_lead_data = {
            "name": "Rajesh Kumar",
            "phone": "9876543210",
            "email": "rajesh.kumar@example.com",
            "budget": 75000,
            "space_size": "3 BHK Balcony",
            "location": "Mumbai, Maharashtra",
            "source": "Website",
            "category": "Residential",
            "notes": "Interested in complete balcony garden transformation"
        }
        
        self.test_task_data = {
            "title": "Follow up with Rajesh Kumar",
            "description": "Call client to discuss balcony garden proposal",
            "priority": "High",
            "due_date": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        }

    def log_test(self, category, name, method, endpoint, expected_status, result, response_data=None, error=None):
        """Log test results with detailed information"""
        self.tests_run += 1
        status = "✅ PASS" if result else "❌ FAIL"
        
        print(f"\n{status} [{category}] {name}")
        print(f"   Method: {method} | Endpoint: /{endpoint}")
        print(f"   Expected: {expected_status} | Result: {'SUCCESS' if result else 'FAILED'}")
        
        if result:
            self.tests_passed += 1
            if response_data and isinstance(response_data, dict):
                if len(str(response_data)) < 300:
                    print(f"   Response: {response_data}")
                else:
                    print(f"   Response: Large response ({len(str(response_data))} chars)")
        else:
            self.tests_failed += 1
            if error:
                print(f"   Error: {error}")
                if "502" in str(error) or "500" in str(error):
                    self.critical_failures.append(f"{category} - {name}: {error}")

    def make_request(self, method, endpoint, data=None, params=None, headers=None, files=None):
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        if self.auth_token and 'Authorization' not in headers:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                if files:
                    # Remove Content-Type for file uploads
                    headers.pop('Content-Type', None)
                    response = requests.post(url, data=data, files=files, headers=headers, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            return None, str(e)

    def test_endpoint(self, category, name, method, endpoint, expected_status, data=None, params=None, headers=None, files=None):
        """Test a single endpoint"""
        response = self.make_request(method, endpoint, data, params, headers, files)
        
        if isinstance(response, tuple):  # Error case
            self.log_test(category, name, method, endpoint, expected_status, False, error=response[1])
            return False, {}
        
        success = response.status_code == expected_status
        
        try:
            response_data = response.json() if response.content else {}
        except:
            response_data = {"raw_response": response.text[:200]}
        
        error_msg = None
        if not success:
            error_msg = f"Status {response.status_code}: {response_data.get('detail', response.text[:100])}"
        
        self.log_test(category, name, method, endpoint, expected_status, success, response_data, error_msg)
        return success, response_data

    # ==================== AUTHENTICATION TESTS ====================
    
    def test_authentication_system(self):
        """Test complete authentication system"""
        print("\n" + "="*80)
        print("🔐 TESTING AUTHENTICATION SYSTEM")
        print("="*80)
        
        # Test basic health check first
        self.test_endpoint("HEALTH", "Backend Health Check", "GET", "", 200)
        
        # Test admin login (fallback)
        admin_login = {
            "identifier": "admin",
            "password": "admin123"
        }
        success, response = self.test_endpoint(
            "AUTH", "Admin Login", "POST", "auth/login", 200, admin_login
        )
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
        
        # Test user registration
        timestamp = str(int(time.time()))
        user_data = {
            "username": f"testuser{timestamp}",
            "email": f"testuser{timestamp}@example.com",
            "phone": f"987654{timestamp[-4:]}",
            "full_name": "Test User Admin",
            "role": "Admin",
            "password": "SecurePass123!",
            "department": "Testing"
        }
        
        success, response = self.test_endpoint(
            "AUTH", "User Registration", "POST", "auth/register", 200, user_data
        )
        
        if success and 'id' in response:
            self.created_resources['users'].append(response['id'])
            self.test_user_id = response['id']
        
        # Test phone OTP request
        phone_data = {"phone": "9876543210"}
        self.test_endpoint(
            "AUTH", "Phone OTP Request", "POST", "auth/phone-request-otp", 200, phone_data
        )
        
        # Test password reset request
        reset_data = {"email": user_data["email"]}
        self.test_endpoint(
            "AUTH", "Password Reset Request", "POST", "auth/password-reset", 200, reset_data
        )

    # ==================== LEAD MANAGEMENT TESTS ====================
    
    def test_lead_management_apis(self):
        """Test all lead management endpoints"""
        print("\n" + "="*80)
        print("👥 TESTING LEAD MANAGEMENT APIs")
        print("="*80)
        
        # Create lead
        success, response = self.test_endpoint(
            "LEADS", "Create Lead", "POST", "leads", 200, self.test_lead_data
        )
        
        lead_id = None
        if success and 'id' in response:
            lead_id = response['id']
            self.created_resources['leads'].append(lead_id)
        
        # Get all leads
        self.test_endpoint("LEADS", "Get All Leads", "GET", "leads", 200)
        
        # Get leads with status filter
        self.test_endpoint("LEADS", "Get New Leads", "GET", "leads", 200, params={"status": "New"})
        
        if lead_id:
            # Get specific lead
            self.test_endpoint("LEADS", "Get Lead by ID", "GET", f"leads/{lead_id}", 200)
            
            # Update lead
            update_data = {
                "status": "Qualified",
                "notes": "Updated: Client confirmed interest in premium package"
            }
            self.test_endpoint("LEADS", "Update Lead", "PUT", f"leads/{lead_id}", 200, update_data)
            
            # Test lead routing
            routing_data = {
                "lead_id": lead_id,
                "source": "Website",
                "location": "Mumbai",
                "budget": 75000
            }
            self.test_endpoint("LEADS", "Route Lead", "POST", "routing/route-lead", 200, routing_data)

    # ==================== TASK MANAGEMENT TESTS ====================
    
    def test_task_management_apis(self):
        """Test all task management endpoints"""
        print("\n" + "="*80)
        print("📋 TESTING TASK MANAGEMENT APIs")
        print("="*80)
        
        # Create task
        success, response = self.test_endpoint(
            "TASKS", "Create Task", "POST", "tasks", 200, self.test_task_data
        )
        
        task_id = None
        if success and 'id' in response:
            task_id = response['id']
            self.created_resources['tasks'].append(task_id)
        
        # Get all tasks
        self.test_endpoint("TASKS", "Get All Tasks", "GET", "tasks", 200)
        
        # Get tasks with status filter
        self.test_endpoint("TASKS", "Get Pending Tasks", "GET", "tasks", 200, params={"status": "Pending"})
        
        if task_id:
            # Update task status
            update_data = {"status": "In Progress"}
            self.test_endpoint("TASKS", "Update Task Status", "PUT", f"tasks/{task_id}", 200, update_data)
            
            # Complete task
            complete_data = {"status": "Completed"}
            self.test_endpoint("TASKS", "Complete Task", "PUT", f"tasks/{task_id}", 200, complete_data)

    # ==================== HRMS & CAMERA TESTS ====================
    
    def test_hrms_camera_apis(self):
        """Test HRMS and camera functionality"""
        print("\n" + "="*80)
        print("📷 TESTING HRMS & CAMERA APIs")
        print("="*80)
        
        # Test face check-in endpoint
        checkin_data = {
            "employee_id": "test_employee_001",
            "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "location": {
                "latitude": 19.0760,
                "longitude": 72.8777
            }
        }
        self.test_endpoint("HRMS", "Face Check-in", "POST", "hrms/face-checkin", 200, checkin_data)
        
        # Test GPS check-in
        gps_checkin_data = {
            "employee_id": "test_employee_001",
            "location": {
                "latitude": 19.0760,
                "longitude": 72.8777
            }
        }
        self.test_endpoint("HRMS", "GPS Check-in", "POST", "hrms/gps-checkin", 200, gps_checkin_data)
        
        # Test leave application
        leave_data = {
            "employee_id": "test_employee_001",
            "leave_type": "Casual Leave",
            "start_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "reason": "Personal work"
        }
        self.test_endpoint("HRMS", "Apply Leave", "POST", "hrms/leave-request", 200, leave_data)
        
        # Test attendance records
        self.test_endpoint("HRMS", "Get Attendance", "GET", "hrms/attendance", 200)

    # ==================== AI STACK TESTS ====================
    
    def test_ai_stack_integration(self):
        """Test all 19 AI endpoints across different categories"""
        print("\n" + "="*80)
        print("🤖 TESTING AI STACK INTEGRATION (19 ENDPOINTS)")
        print("="*80)
        
        # Core AI Services
        voice_data = {
            "voice_input": "Create a task to call Rajesh Kumar tomorrow at 10 AM to discuss the balcony garden proposal",
            "context": "lead_management"
        }
        self.test_endpoint("AI-CORE", "Voice to Task", "POST", "ai/voice-to-task", 200, voice_data)
        
        insight_data = {
            "type": "leads",
            "timeframe": "last_30_days"
        }
        self.test_endpoint("AI-CORE", "AI Insights", "POST", "ai/insights", 200, insight_data)
        
        content_data = {
            "type": "email",
            "context": "lead_nurturing",
            "target_audience": "residential_clients"
        }
        self.test_endpoint("AI-CORE", "Content Generation", "POST", "ai/generate-content", 200, content_data)
        
        # Conversational CRM AI
        self.test_endpoint("AI-CRM", "Smart Lead Scoring", "POST", "ai/crm/smart-lead-scoring", 200, 
                          params={"lead_id": "test_lead_001"})
        
        conversation_data = {
            "conversation": "Customer: I'm interested in balcony gardens. Agent: Great! What's your budget?",
            "participants": ["customer", "agent"]
        }
        self.test_endpoint("AI-CRM", "Conversation Analysis", "POST", "ai/crm/conversation-analysis", 200, conversation_data)
        
        self.test_endpoint("AI-CRM", "Recall Context", "GET", "ai/recall-context/test_client_001", 200)
        
        # Sales & Pipeline AI
        self.test_endpoint("AI-SALES", "Deal Prediction", "POST", "ai/sales/deal-prediction", 200)
        
        proposal_data = {"service_type": "balcony_garden_complete"}
        self.test_endpoint("AI-SALES", "Smart Proposal Generator", "POST", "ai/sales/smart-proposal-generator", 200, 
                          proposal_data, params={"lead_id": "test_lead_001"})
        
        # Marketing & Growth AI
        campaign_data = {
            "campaign_type": "lead_generation",
            "target_location": "Mumbai",
            "budget": 50000
        }
        self.test_endpoint("AI-MARKETING", "Campaign Optimizer", "POST", "ai/marketing/campaign-optimizer", 200, campaign_data)
        
        self.test_endpoint("AI-MARKETING", "Competitor Analysis", "POST", "ai/marketing/competitor-analysis", 200, 
                          params={"location": "Mumbai"})
        
        # Product & Project AI
        self.test_endpoint("AI-PRODUCT", "Smart Catalog", "POST", "ai/product/smart-catalog", 200)
        
        design_data = {
            "space_type": "balcony",
            "size": "3BHK",
            "budget": 75000,
            "preferences": ["low_maintenance", "flowering_plants"]
        }
        self.test_endpoint("AI-PRODUCT", "Design Suggestions", "POST", "ai/project/design-suggestions", 200, design_data)
        
        # Analytics & Admin AI
        self.test_endpoint("AI-ANALYTICS", "Business Intelligence", "POST", "ai/analytics/business-intelligence", 200)
        
        self.test_endpoint("AI-ANALYTICS", "Predictive Forecasting", "POST", "ai/analytics/predictive-forecasting", 200, 
                          params={"forecast_type": "revenue"})
        
        # HR & Team Operations AI
        self.test_endpoint("AI-HR", "Performance Analysis", "POST", "ai/hr/performance-analysis", 200)
        
        scheduling_data = {
            "department": "field_operations",
            "date_range": "next_week",
            "requirements": ["site_visits", "installations"]
        }
        self.test_endpoint("AI-HR", "Smart Scheduling", "POST", "ai/hr/smart-scheduling", 200, scheduling_data)
        
        # Automation Layer AI
        self.test_endpoint("AI-AUTOMATION", "Workflow Optimization", "POST", "ai/automation/workflow-optimization", 200, 
                          params={"department": "sales"})
        
        notification_data = {
            "context": "lead_follow_up",
            "urgency": "high",
            "channel": "whatsapp"
        }
        self.test_endpoint("AI-AUTOMATION", "Smart Notifications", "POST", "ai/automation/smart-notifications", 200, notification_data)
        
        # Global AI Assistant
        assistant_data = {
            "query": "What's the status of all high-priority leads in Mumbai?",
            "context": "business_overview"
        }
        self.test_endpoint("AI-GLOBAL", "Global AI Assistant", "POST", "ai/assistant/query", 200, assistant_data)

    # ==================== WORKFLOW & ROUTING TESTS ====================
    
    def test_workflow_routing_apis(self):
        """Test workflow authoring and lead routing APIs"""
        print("\n" + "="*80)
        print("🔄 TESTING WORKFLOW & ROUTING APIs")
        print("="*80)
        
        # Create routing rule
        routing_rule_data = {
            "name": "Mumbai Website Leads",
            "source": "Website",
            "conditions": {
                "location": "Mumbai",
                "budget_min": 50000
            },
            "target_agent_id": "agent_001",
            "priority": 1
        }
        success, response = self.test_endpoint("ROUTING", "Create Routing Rule", "POST", "routing/rules", 200, routing_rule_data)
        
        if success and 'rule' in response:
            self.created_resources['routing_rules'].append(response['rule']['id'])
        
        # Get routing rules
        self.test_endpoint("ROUTING", "Get Routing Rules", "GET", "routing/rules", 200)
        
        # Create prompt template
        template_data = {
            "name": "Lead Nurturing WhatsApp",
            "description": "Template for nurturing leads via WhatsApp",
            "category": "lead_nurturing",
            "system_prompt": "You are a helpful assistant for Aavana Greens",
            "user_prompt_template": "Create a personalized message for {lead_name} interested in {service_type}",
            "variables": ["lead_name", "service_type", "budget", "location"],
            "ai_model": "gpt-5"
        }
        success, response = self.test_endpoint("WORKFLOW", "Create Prompt Template", "POST", "workflows/prompt-templates", 200, template_data)
        
        template_id = None
        if success and 'template' in response:
            template_id = response['template']['id']
            self.created_resources['templates'].append(template_id)
        
        # Get prompt templates
        self.test_endpoint("WORKFLOW", "Get Prompt Templates", "GET", "workflows/prompt-templates", 200)
        
        if template_id:
            # Test prompt template
            test_data = {
                "variables": {
                    "lead_name": "Rajesh Kumar",
                    "service_type": "Balcony Garden",
                    "budget": "75000",
                    "location": "Mumbai"
                }
            }
            self.test_endpoint("WORKFLOW", "Test Prompt Template", "POST", f"workflows/prompt-templates/{template_id}/test", 200, test_data)
        
        # Create workflow
        workflow_data = {
            "name": "Lead Qualification Workflow",
            "description": "Automated lead qualification and nurturing",
            "category": "lead_nurturing",
            "steps": [
                {"type": "ai_response", "template_id": template_id},
                {"type": "send_message", "channel": "whatsapp"},
                {"type": "wait_for_response", "timeout": 3600},
                {"type": "conditional_logic", "condition": "response_positive"},
                {"type": "assign_agent", "agent_id": "agent_001"},
                {"type": "schedule_followup", "delay": 86400}
            ]
        }
        success, response = self.test_endpoint("WORKFLOW", "Create Workflow", "POST", "workflows", 200, workflow_data)
        
        workflow_id = None
        if success and 'workflow' in response:
            workflow_id = response['workflow']['id']
            self.created_resources['workflows'].append(workflow_id)
        
        # Get workflows
        self.test_endpoint("WORKFLOW", "Get Workflows", "GET", "workflows", 200)
        
        if workflow_id:
            # Test workflow
            workflow_test_data = {
                "lead_data": {
                    "name": "Test Lead",
                    "phone": "9876543210",
                    "service_interest": "Balcony Garden"
                }
            }
            self.test_endpoint("WORKFLOW", "Test Workflow", "POST", f"workflows/{workflow_id}/test", 200, workflow_test_data)
            
            # Publish workflow
            self.test_endpoint("WORKFLOW", "Publish Workflow", "POST", f"workflows/{workflow_id}/publish", 200)
            
            # Get workflow analytics
            self.test_endpoint("WORKFLOW", "Workflow Analytics", "GET", f"workflows/{workflow_id}/analytics", 200)

    # ==================== DASHBOARD & ANALYTICS TESTS ====================
    
    def test_dashboard_analytics(self):
        """Test dashboard and analytics endpoints"""
        print("\n" + "="*80)
        print("📊 TESTING DASHBOARD & ANALYTICS")
        print("="*80)
        
        # Test dashboard stats
        self.test_endpoint("DASHBOARD", "Dashboard Statistics", "GET", "dashboard/stats", 200)

    # ==================== AAVANA 2.0 TESTS ====================
    
    def test_aavana_2_0_apis(self):
        """Test Aavana 2.0 multilingual AI system"""
        print("\n" + "="*80)
        print("🌐 TESTING AAVANA 2.0 MULTILINGUAL AI")
        print("="*80)
        
        # Test health check
        self.test_endpoint("AAVANA", "Health Check", "GET", "aavana/health", 200)
        
        # Test English conversation
        english_data = {
            "message": "I need help with balcony garden setup",
            "channel": "in_app_chat",
            "user_id": "test_user_001",
            "language": "en"
        }
        self.test_endpoint("AAVANA", "English Conversation", "POST", "aavana/conversation", 200, english_data)
        
        # Test Hindi conversation
        hindi_data = {
            "message": "मुझे बालकनी गार्डन की जानकारी चाहिए",
            "channel": "in_app_chat",
            "user_id": "test_user_002",
            "language": "hi"
        }
        self.test_endpoint("AAVANA", "Hindi Conversation", "POST", "aavana/conversation", 200, hindi_data)
        
        # Test language detection
        detect_data = {"text": "Hello yaar, kya haal hai?"}
        self.test_endpoint("AAVANA", "Language Detection", "POST", "aavana/language-detect", 200, detect_data)
        
        # Test audio templates
        self.test_endpoint("AAVANA", "Audio Templates (EN)", "GET", "aavana/audio-templates", 200, params={"language": "en"})

    # ==================== MAIN TEST EXECUTION ====================
    
    def run_comprehensive_audit(self):
        """Run complete backend audit"""
        print("🚀 STARTING COMPREHENSIVE BACKEND AUDIT")
        print("Testing ALL endpoints and functionality as requested")
        print("="*80)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_authentication_system()
        self.test_lead_management_apis()
        self.test_task_management_apis()
        self.test_hrms_camera_apis()
        self.test_ai_stack_integration()
        self.test_workflow_routing_apis()
        self.test_dashboard_analytics()
        self.test_aavana_2_0_apis()
        
        # Calculate results
        end_time = time.time()
        duration = end_time - start_time
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        # Print comprehensive results
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE BACKEND AUDIT RESULTS")
        print("="*80)
        print(f"⏱️  Total Duration: {duration:.2f} seconds")
        print(f"🧪 Total Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_failed}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   • {failure}")
        
        print(f"\n🎯 AUDIT STATUS: {'✅ PASSED' if success_rate >= 70 else '❌ NEEDS ATTENTION'}")
        
        if success_rate >= 90:
            print("🏆 EXCELLENT: Backend is production-ready with minimal issues")
        elif success_rate >= 70:
            print("✅ GOOD: Backend is functional with some minor issues")
        elif success_rate >= 50:
            print("⚠️  MODERATE: Backend has significant issues requiring attention")
        else:
            print("🚨 CRITICAL: Backend has major issues blocking functionality")
        
        return {
            'total_tests': self.tests_run,
            'passed': self.tests_passed,
            'failed': self.tests_failed,
            'success_rate': success_rate,
            'critical_failures': self.critical_failures,
            'duration': duration
        }

if __name__ == "__main__":
    print("🌿 Aavana Greens CRM - Comprehensive Backend Audit")
    print("Testing all HRMS, AI, ERP, Voice, Workflow, and Notification APIs")
    print("="*80)
    
    auditor = ComprehensiveBackendAudit()
    results = auditor.run_comprehensive_audit()
    
    # Exit with appropriate code
    exit_code = 0 if results['success_rate'] >= 70 else 1
    sys.exit(exit_code)