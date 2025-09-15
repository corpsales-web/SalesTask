#!/usr/bin/env python3
"""
Enhanced Backend Services Test Suite for Aavana Greens
Tests all new service endpoints and functionality
"""

import requests
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from io import BytesIO
import tempfile
import os

class EnhancedBackendTester:
    def __init__(self, base_url="https://aavana-greens-crm.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None
        self.test_user_id = None
        self.test_lead_id = None
        self.test_role_id = None
        self.test_department_id = None
        self.test_file_id = None
        self.test_voice_task_id = None
        self.test_queue_id = None
        
    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, files=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        
        if not headers:
            headers = {'Content-Type': 'application/json'}
        
        if self.auth_token and 'Authorization' not in headers:
            headers['Authorization'] = f'Bearer {self.auth_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                if files:
                    # Remove Content-Type for multipart/form-data
                    headers.pop('Content-Type', None)
                    response = requests.post(url, data=data, files=files, headers=headers)
                else:
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
                    if isinstance(response_data, dict) and len(str(response_data)) < 300:
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

    def authenticate(self):
        """Authenticate with master user"""
        print("\n🔐 Authenticating with master user...")
        login_data = {
            "identifier": "master",
            "password": "master123"
        }
        
        success, response = self.run_test(
            "Master Authentication", "POST", "auth/login", 200, data=login_data
        )
        
        if success and 'access_token' in response:
            self.auth_token = response['access_token']
            self.test_user_id = response['user']['id']
            print(f"✅ Authenticated as: {response['user']['username']}")
            return True
        else:
            print("❌ Authentication failed")
            return False

    def test_health_check_services(self):
        """Test health check for all services"""
        return self.run_test("Health Check - All Services", "GET", "health/services", 200)

    # ============== FILE UPLOAD SERVICE TESTS ==============
    
    def test_file_upload_single(self):
        """Test single file upload"""
        # Create a test file
        test_content = b"This is a test file for Aavana Greens file upload service"
        
        files = {
            'file': ('test_document.txt', BytesIO(test_content), 'text/plain')
        }
        
        data = {
            'project_id': 'test_project_123'
        }
        
        success, response = self.run_test(
            "File Upload - Single File", "POST", "upload/file", 200, 
            data=data, files=files
        )
        
        if success and 'file_id' in response:
            self.test_file_id = response['file_id']
        
        return success, response

    def test_file_upload_multiple(self):
        """Test multiple file upload"""
        # Create test files
        files = {
            'files': [
                ('test_doc1.txt', BytesIO(b"Test document 1"), 'text/plain'),
                ('test_doc2.txt', BytesIO(b"Test document 2"), 'text/plain')
            ]
        }
        
        data = {
            'project_id': 'test_project_multi'
        }
        
        return self.run_test(
            "File Upload - Multiple Files", "POST", "upload/multiple", 200,
            data=data, files=files
        )

    def test_presigned_url_generation(self):
        """Test presigned URL generation"""
        data = {
            'filename': 'test_presigned.pdf',
            'content_type': 'application/pdf'
        }
        
        return self.run_test(
            "File Upload - Presigned URL", "POST", "upload/presigned-url", 200, data=data
        )

    # ============== ROLE MANAGEMENT SERVICE TESTS ==============
    
    def test_get_roles(self):
        """Test getting all roles"""
        return self.run_test("Role Management - Get Roles", "GET", "roles", 200)

    def test_create_role(self):
        """Test creating a new role"""
        role_data = {
            'name': 'Test Manager',
            'description': 'Test role for automated testing',
            'level': 4,
            'permissions': {
                'leads': ['view', 'create'],
                'tasks': ['view', 'create', 'edit'],
                'users': ['view']
            }
        }
        
        success, response = self.run_test(
            "Role Management - Create Role", "POST", "roles", 200, data=role_data
        )
        
        if success and 'id' in response:
            self.test_role_id = response['id']
        
        return success, response

    def test_update_role(self):
        """Test updating a role"""
        if not self.test_role_id:
            print("⚠️ Skipping role update test - no role ID available")
            return False, {}
        
        update_data = {
            'description': 'Updated test role description',
            'permissions': {
                'leads': ['view', 'create', 'edit'],
                'tasks': ['view', 'create', 'edit', 'assign']
            }
        }
        
        return self.run_test(
            "Role Management - Update Role", "PUT", f"roles/{self.test_role_id}", 200, 
            data=update_data
        )

    def test_get_departments(self):
        """Test getting all departments"""
        return self.run_test("Role Management - Get Departments", "GET", "departments", 200)

    def test_create_department(self):
        """Test creating a new department"""
        department_data = {
            'name': 'Test Department',
            'description': 'Department for automated testing',
            'budget': 100000,
            'location': 'Test Office'
        }
        
        success, response = self.run_test(
            "Role Management - Create Department", "POST", "departments", 200, 
            data=department_data
        )
        
        if success and 'id' in response:
            self.test_department_id = response['id']
        
        return success, response

    def test_get_user_permissions(self):
        """Test getting user permissions"""
        if not self.test_user_id:
            print("⚠️ Skipping user permissions test - no user ID available")
            return False, {}
        
        return self.run_test(
            "Role Management - Get User Permissions", "GET", 
            f"users/{self.test_user_id}/permissions", 200
        )

    # ============== ENHANCED LEAD MANAGEMENT TESTS ==============
    
    def create_test_lead(self):
        """Create a test lead for enhanced testing"""
        lead_data = {
            "name": "Enhanced Test Lead",
            "phone": "9876543210",
            "email": "enhanced.test@example.com",
            "budget": 75000,
            "space_size": "3 BHK",
            "location": "Mumbai, Maharashtra",
            "source": "Website",
            "category": "Individual",
            "notes": "Test lead for enhanced lead management testing"
        }
        
        success, response = self.run_test(
            "Enhanced Lead Management - Create Test Lead", "POST", "leads", 200, 
            data=lead_data
        )
        
        if success and 'id' in response:
            self.test_lead_id = response['id']
        
        return success, response

    def test_get_leads_with_actions(self):
        """Test getting leads with available actions"""
        params = {
            'page': 1,
            'limit': 10,
            'source': 'Website'
        }
        
        return self.run_test(
            "Enhanced Lead Management - Get Leads with Actions", "GET", 
            "leads/with-actions", 200, params=params
        )

    def test_execute_lead_action_call(self):
        """Test executing a call action on a lead"""
        if not self.test_lead_id:
            print("⚠️ Skipping lead action test - no lead ID available")
            return False, {}
        
        action_data = {
            'action_type': 'call',
            'duration': 300,  # 5 minutes
            'notes': 'Discussed project requirements and budget',
            'outcome': 'interested',
            'follow_up_required': True,
            'next_call_date': '2024-12-30T10:00:00Z'
        }
        
        return self.run_test(
            "Enhanced Lead Management - Execute Call Action", "POST", 
            f"leads/{self.test_lead_id}/actions", 200, data=action_data
        )

    def test_execute_lead_action_whatsapp(self):
        """Test executing a WhatsApp action on a lead"""
        if not self.test_lead_id:
            print("⚠️ Skipping WhatsApp action test - no lead ID available")
            return False, {}
        
        action_data = {
            'action_type': 'whatsapp',
            'message': 'Hello! Thank you for your interest in Aavana Greens. We have some exciting green building solutions for you.'
        }
        
        return self.run_test(
            "Enhanced Lead Management - Execute WhatsApp Action", "POST", 
            f"leads/{self.test_lead_id}/actions", 200, data=action_data
        )

    def test_execute_lead_action_email(self):
        """Test executing an email action on a lead"""
        if not self.test_lead_id:
            print("⚠️ Skipping email action test - no lead ID available")
            return False, {}
        
        action_data = {
            'action_type': 'email',
            'subject': 'Your Green Building Project - Aavana Greens',
            'message': 'Dear Customer,\n\nThank you for your interest in sustainable building solutions. We would love to discuss your project requirements.\n\nBest regards,\nAavana Greens Team'
        }
        
        return self.run_test(
            "Enhanced Lead Management - Execute Email Action", "POST", 
            f"leads/{self.test_lead_id}/actions", 200, data=action_data
        )

    def test_get_lead_actions(self):
        """Test getting action history for a lead"""
        if not self.test_lead_id:
            print("⚠️ Skipping lead actions history test - no lead ID available")
            return False, {}
        
        return self.run_test(
            "Enhanced Lead Management - Get Lead Actions", "GET", 
            f"leads/{self.test_lead_id}/actions", 200
        )

    def test_add_lead_remark(self):
        """Test adding a remark to a lead"""
        if not self.test_lead_id:
            print("⚠️ Skipping lead remark test - no lead ID available")
            return False, {}
        
        remark_data = {
            'type': 'text',
            'content': 'Customer is very interested in sustainable solutions. Prefers eco-friendly materials.',
            'is_private': False
        }
        
        return self.run_test(
            "Enhanced Lead Management - Add Lead Remark", "POST", 
            f"leads/{self.test_lead_id}/remarks", 200, data=remark_data
        )

    def test_get_lead_remarks(self):
        """Test getting remarks for a lead"""
        if not self.test_lead_id:
            print("⚠️ Skipping lead remarks retrieval test - no lead ID available")
            return False, {}
        
        return self.run_test(
            "Enhanced Lead Management - Get Lead Remarks", "GET", 
            f"leads/{self.test_lead_id}/remarks", 200
        )

    # ============== VOICE STT SERVICE TESTS ==============
    
    def test_voice_transcribe(self):
        """Test voice transcription"""
        # Create a mock audio file (in real scenario, this would be actual audio)
        audio_content = b"Mock audio data for transcription testing"
        
        files = {
            'audio_file': ('test_audio.wav', BytesIO(audio_content), 'audio/wav')
        }
        
        data = {
            'language': 'en',
            'provider': 'whisper_local'
        }
        
        return self.run_test(
            "Voice STT - Transcribe Audio", "POST", "voice/transcribe", 200,
            data=data, files=files
        )

    def test_voice_remark(self):
        """Test voice remark processing"""
        if not self.test_lead_id:
            print("⚠️ Skipping voice remark test - no lead ID available")
            return False, {}
        
        # Create a mock audio file
        audio_content = b"Mock voice remark audio data"
        
        files = {
            'audio_file': ('voice_remark.wav', BytesIO(audio_content), 'audio/wav')
        }
        
        data = {
            'lead_id': self.test_lead_id,
            'language': 'en'
        }
        
        return self.run_test(
            "Voice STT - Process Voice Remark", "POST", "voice/remark", 200,
            data=data, files=files
        )

    def test_voice_extract_tasks(self):
        """Test task extraction from voice"""
        # Create a mock audio file
        audio_content = b"Mock audio data with task instructions"
        
        files = {
            'audio_file': ('task_audio.wav', BytesIO(audio_content), 'audio/wav')
        }
        
        data = {
            'language': 'en'
        }
        
        success, response = self.run_test(
            "Voice STT - Extract Tasks from Voice", "POST", "voice/extract-tasks", 200,
            data=data, files=files
        )
        
        if success and 'id' in response:
            self.test_voice_task_id = response['id']
        
        return success, response

    def test_get_voice_transcriptions(self):
        """Test getting voice transcription history"""
        return self.run_test(
            "Voice STT - Get Transcriptions", "GET", "voice/transcriptions", 200
        )

    def test_get_voice_tasks(self):
        """Test getting voice-extracted tasks"""
        params = {
            'status': 'pending',
            'limit': 20
        }
        
        return self.run_test(
            "Voice STT - Get Voice Tasks", "GET", "voice/tasks", 200, params=params
        )

    # ============== OFFLINE SYNC SERVICE TESTS ==============
    
    def test_queue_offline_operation(self):
        """Test queueing an offline operation"""
        operation_data = {
            'operation_data': {
                'name': 'Offline Test Lead',
                'phone': '9876543211',
                'email': 'offline.test@example.com',
                'source': 'Offline App'
            },
            'entity_type': 'leads',
            'operation_type': 'create'
        }
        
        success, response = self.run_test(
            "Offline Sync - Queue Operation", "POST", "offline/queue", 200, 
            data=operation_data
        )
        
        if success and 'queue_id' in response:
            self.test_queue_id = response['queue_id']
        
        return success, response

    def test_autosave_data(self):
        """Test auto-saving data"""
        autosave_data = {
            'data': {
                'name': 'Auto-saved Lead',
                'phone': '9876543212',
                'notes': 'This is auto-saved data'
            },
            'entity_type': 'leads',
            'entity_id': 'test_lead_autosave_123'
        }
        
        return self.run_test(
            "Offline Sync - Auto-save Data", "POST", "offline/autosave", 200, 
            data=autosave_data
        )

    def test_get_autosaved_data(self):
        """Test retrieving auto-saved data"""
        return self.run_test(
            "Offline Sync - Get Auto-saved Data", "GET", 
            "offline/autosave/leads/test_lead_autosave_123", 200
        )

    def test_get_sync_status(self):
        """Test getting sync queue status"""
        return self.run_test(
            "Offline Sync - Get Sync Status", "GET", "offline/sync-status", 200
        )

    def test_get_sync_conflicts(self):
        """Test getting sync conflicts"""
        return self.run_test(
            "Offline Sync - Get Sync Conflicts", "GET", "offline/conflicts", 200
        )

    # ============== SERVICE INITIALIZATION VERIFICATION ==============
    
    def test_service_initialization(self):
        """Test that all services are properly initialized"""
        print("\n🔧 Testing Service Initialization...")
        
        # Test role management service initialization
        success1, _ = self.run_test(
            "Service Init - Role Management", "GET", "roles", 200
        )
        
        # Test departments (should have default departments)
        success2, response2 = self.run_test(
            "Service Init - Default Departments", "GET", "departments", 200
        )
        
        # Check if default departments exist
        if success2 and isinstance(response2, list) and len(response2) > 0:
            print(f"   ✅ Found {len(response2)} default departments")
        
        # Test voice STT service health
        success3, _ = self.run_test(
            "Service Init - Voice STT Health", "GET", "health/services", 200
        )
        
        return success1 and success2 and success3

    # ============== AUTHENTICATION & AUTHORIZATION TESTS ==============
    
    def test_role_based_access_control(self):
        """Test role-based access control"""
        print("\n🔐 Testing Role-Based Access Control...")
        
        # Test Super Admin access to role management
        success1, _ = self.run_test(
            "RBAC - Super Admin Role Access", "GET", "roles", 200
        )
        
        # Test permission checking
        permission_data = {
            'permission': 'users:create'
        }
        
        success2, _ = self.run_test(
            "RBAC - Permission Check", "POST", "auth/check-permission", 200, 
            data=permission_data
        )
        
        return success1 and success2

    def test_authentication_failures(self):
        """Test authentication failure scenarios"""
        print("\n🚫 Testing Authentication Failures...")
        
        # Test accessing protected endpoint without token
        headers = {}  # No Authorization header
        
        success1, _ = self.run_test(
            "Auth Failure - No Token", "GET", "roles", 401, headers=headers
        )
        
        # Test with invalid token
        headers = {'Authorization': 'Bearer invalid_token_123'}
        
        success2, _ = self.run_test(
            "Auth Failure - Invalid Token", "GET", "roles", 401, headers=headers
        )
        
        return success1 and success2

    # ============== DATA PERSISTENCE TESTS ==============
    
    def test_data_persistence(self):
        """Test data persistence across operations"""
        print("\n💾 Testing Data Persistence...")
        
        # Create a lead and verify it persists
        lead_data = {
            "name": "Persistence Test Lead",
            "phone": "9876543213",
            "email": "persistence@example.com",
            "source": "API Test"
        }
        
        success1, response1 = self.run_test(
            "Data Persistence - Create Lead", "POST", "leads", 200, data=lead_data
        )
        
        if success1 and 'id' in response1:
            lead_id = response1['id']
            
            # Retrieve the lead to verify persistence
            success2, response2 = self.run_test(
                "Data Persistence - Retrieve Lead", "GET", f"leads/{lead_id}", 200
            )
            
            if success2 and response2.get('name') == lead_data['name']:
                print("   ✅ Lead data persisted correctly")
                return True
        
        return False

    # ============== ERROR HANDLING TESTS ==============
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n⚠️ Testing Error Handling...")
        
        # Test 400 - Bad Request
        success1, _ = self.run_test(
            "Error Handling - Bad Request (400)", "POST", "offline/queue", 400, 
            data={'invalid': 'data'}
        )
        
        # Test 404 - Not Found
        success2, _ = self.run_test(
            "Error Handling - Not Found (404)", "GET", "leads/nonexistent_id", 404
        )
        
        # Test 403 - Forbidden (try to delete role as non-super-admin)
        if self.test_role_id:
            # First, login as regular admin
            admin_login = {
                "identifier": "admin",
                "password": "admin123"
            }
            
            admin_success, admin_response = self.run_test(
                "Error Handling - Admin Login", "POST", "auth/login", 200, 
                data=admin_login
            )
            
            if admin_success and 'access_token' in admin_response:
                # Try to delete role as admin (should fail - only super admin can delete)
                old_token = self.auth_token
                self.auth_token = admin_response['access_token']
                
                success3, _ = self.run_test(
                    "Error Handling - Forbidden (403)", "DELETE", 
                    f"roles/{self.test_role_id}", 403
                )
                
                # Restore super admin token
                self.auth_token = old_token
                
                return success1 and success2 and success3
        
        return success1 and success2

    # ============== INTEGRATION TESTS ==============
    
    def test_end_to_end_workflow(self):
        """Test end-to-end workflow integration"""
        print("\n🔄 Testing End-to-End Workflow...")
        
        # 1. Create a lead
        lead_data = {
            "name": "E2E Test Customer",
            "phone": "9876543214",
            "email": "e2e.test@example.com",
            "budget": 100000,
            "source": "Integration Test"
        }
        
        success1, response1 = self.run_test(
            "E2E - Create Lead", "POST", "leads", 200, data=lead_data
        )
        
        if not success1 or 'id' not in response1:
            return False
        
        lead_id = response1['id']
        
        # 2. Execute action on lead
        action_data = {
            'action_type': 'call',
            'duration': 180,
            'notes': 'Initial consultation call',
            'outcome': 'qualified'
        }
        
        success2, _ = self.run_test(
            "E2E - Execute Lead Action", "POST", f"leads/{lead_id}/actions", 200, 
            data=action_data
        )
        
        # 3. Add remark to lead
        remark_data = {
            'type': 'text',
            'content': 'Customer is ready to proceed with project planning'
        }
        
        success3, _ = self.run_test(
            "E2E - Add Lead Remark", "POST", f"leads/{lead_id}/remarks", 200, 
            data=remark_data
        )
        
        # 4. Queue offline operation
        offline_data = {
            'operation_data': {
                'lead_id': lead_id,
                'status': 'Qualified'
            },
            'entity_type': 'leads',
            'operation_type': 'update'
        }
        
        success4, _ = self.run_test(
            "E2E - Queue Offline Operation", "POST", "offline/queue", 200, 
            data=offline_data
        )
        
        return success1 and success2 and success3 and success4

    def run_all_tests(self):
        """Run all enhanced backend tests"""
        print("🚀 Starting Enhanced Aavana Greens Backend Services Testing")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed, stopping tests")
            return 1
        
        # Test 1: Health Check
        print("\n🏥 Testing Health Check Services...")
        self.test_health_check_services()
        
        # Test 2: Service Initialization
        self.test_service_initialization()
        
        # Test 3: File Upload Service
        print("\n📁 Testing File Upload Service...")
        self.test_file_upload_single()
        self.test_file_upload_multiple()
        self.test_presigned_url_generation()
        
        # Test 4: Role Management Service
        print("\n👥 Testing Role Management Service...")
        self.test_get_roles()
        self.test_create_role()
        self.test_update_role()
        self.test_get_departments()
        self.test_create_department()
        self.test_get_user_permissions()
        
        # Test 5: Enhanced Lead Management
        print("\n🎯 Testing Enhanced Lead Management...")
        self.create_test_lead()
        self.test_get_leads_with_actions()
        self.test_execute_lead_action_call()
        self.test_execute_lead_action_whatsapp()
        self.test_execute_lead_action_email()
        self.test_get_lead_actions()
        self.test_add_lead_remark()
        self.test_get_lead_remarks()
        
        # Test 6: Voice STT Service
        print("\n🎤 Testing Voice STT Service...")
        self.test_voice_transcribe()
        self.test_voice_remark()
        self.test_voice_extract_tasks()
        self.test_get_voice_transcriptions()
        self.test_get_voice_tasks()
        
        # Test 7: Offline Sync Service
        print("\n🔄 Testing Offline Sync Service...")
        self.test_queue_offline_operation()
        self.test_autosave_data()
        self.test_get_autosaved_data()
        self.test_get_sync_status()
        self.test_get_sync_conflicts()
        
        # Test 8: Authentication & Authorization
        self.test_role_based_access_control()
        self.test_authentication_failures()
        
        # Test 9: Data Persistence
        self.test_data_persistence()
        
        # Test 10: Error Handling
        self.test_error_handling()
        
        # Test 11: Integration Testing
        self.test_end_to_end_workflow()
        
        # Final Results
        print("\n" + "=" * 70)
        print(f"📊 ENHANCED BACKEND TESTING RESULTS")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All enhanced backend services are working correctly!")
            return 0
        else:
            print("⚠️ Some tests failed. Please check the enhanced backend implementation.")
            return 1

def main():
    tester = EnhancedBackendTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())