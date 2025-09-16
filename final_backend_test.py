import requests
import json
from datetime import datetime, timezone
import uuid

def test_endpoint(name, url, method="GET", data=None, timeout=15):
    """Test endpoint with local backend"""
    print(f"🔍 Testing {name}...")
    try:
        headers = {'Content-Type': 'application/json'}
        if method == "GET":
            response = requests.get(url, timeout=timeout, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout, headers=headers)
        
        if response.status_code == 200:
            print(f"   ✅ PASSED - Status: {response.status_code}")
            try:
                resp_data = response.json()
                if isinstance(resp_data, dict) and len(str(resp_data)) < 200:
                    print(f"   📄 Response: {resp_data}")
                elif isinstance(resp_data, list):
                    print(f"   📄 Response: List with {len(resp_data)} items")
                else:
                    print(f"   📄 Response: Data received successfully")
            except:
                print(f"   📄 Response: Non-JSON response")
            return True
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   🚨 Error: {error_data}")
            except:
                print(f"   🚨 Error: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print(f"   ⏰ TIMEOUT - Request took longer than {timeout} seconds")
        return False
    except Exception as e:
        print(f"   ❌ ERROR - {str(e)}")
        return False

def main():
    # Use external URL as specified in review request
    base_url = "https://greenstack-ai.preview.emergentagent.com/api"
    
    print("🎯 COMPREHENSIVE BACKEND TESTING FOR REVIEW REQUEST")
    print("=" * 80)
    print("Focus: Enhanced AI Endpoints, HRMS Camera, File Upload, Workflow Templates, Core CRM")
    print("=" * 80)
    
    results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "categories": {}
    }
    
    # 1. Enhanced AI Endpoints (8 new AI API endpoints)
    print("\n🤖 ENHANCED AI ENDPOINTS (8 NEW ENDPOINTS)")
    print("-" * 60)
    
    ai_endpoints = [
        ("AI Generate", f"{base_url}/ai/generate", "POST", {
            "prompt": "Generate a professional proposal for a 2 BHK balcony garden in Mumbai with ₹50,000 budget",
            "provider": "openai",
            "model": "gpt-5",
            "temperature": 0.7
        }),
        ("AI Smart Selection", f"{base_url}/ai/smart-selection", "POST", {
            "task_type": "business",
            "prompt": "Analyze lead conversion rate for green building consultancy"
        }),
        ("AI Analyze Conversation", f"{base_url}/ai/analyze-conversation", "POST", {
            "conversation": [
                {"speaker": "customer", "message": "Hi, I'm interested in balcony garden"},
                {"speaker": "agent", "message": "What's your budget and space size?"}
            ]
        }),
        ("AI Generate Proposal", f"{base_url}/ai/generate-proposal", "POST", {
            "lead_data": {
                "name": "Test Customer",
                "location": "Mumbai",
                "budget": 50000,
                "space_size": "2 BHK Balcony"
            },
            "service_type": "balcony_garden"
        }),
        ("AI Optimize Workflow", f"{base_url}/ai/optimize-workflow", "POST", {
            "workflow_name": "Lead Nurturing",
            "current_steps": ["Contact", "Qualify", "Propose", "Close"],
            "performance_metrics": {"conversion_rate": 25}
        }),
        ("AI Marketing Content", f"{base_url}/ai/marketing-content", "POST", {
            "campaign_type": "social_media",
            "target_audience": "urban_homeowners",
            "service": "balcony_gardens"
        }),
        ("AI Predict Deals", f"{base_url}/ai/predict-deals", "POST", [
            {
                "lead_id": "test_001",
                "name": "Test Lead",
                "budget": 75000,
                "engagement_score": 8
            }
        ]),
        ("AI Task Automation", f"{base_url}/ai/task-automation", "POST", {
            "task_type": "follow_up",
            "lead_data": {"name": "Customer", "status": "Qualified"},
            "context": "post_site_visit"
        })
    ]
    
    ai_passed = 0
    for name, url, method, data in ai_endpoints:
        results["total_tests"] += 1
        if test_endpoint(name, url, method, data, timeout=45):
            results["passed_tests"] += 1
            ai_passed += 1
        else:
            results["failed_tests"] += 1
    
    results["categories"]["Enhanced AI Endpoints"] = f"{ai_passed}/{len(ai_endpoints)}"
    
    # 2. HRMS Camera API (face check-in and GPS check-in)
    print("\n👤 HRMS CAMERA API")
    print("-" * 60)
    
    hrms_endpoints = [
        ("HRMS Face Check-in", f"{base_url}/hrms/face-checkin", "POST", {
            "employee_id": "emp_test_001",
            "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "location": {"latitude": 19.0760, "longitude": 72.8777},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }),
        ("HRMS GPS Check-in", f"{base_url}/hrms/gps-checkin", "POST", {
            "employee_id": "emp_test_001",
            "location": {"latitude": 19.0760, "longitude": 72.8777, "accuracy": 10},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "check_type": "check_in"
        })
    ]
    
    hrms_passed = 0
    for name, url, method, data in hrms_endpoints:
        results["total_tests"] += 1
        if test_endpoint(name, url, method, data):
            results["passed_tests"] += 1
            hrms_passed += 1
        else:
            results["failed_tests"] += 1
    
    results["categories"]["HRMS Camera API"] = f"{hrms_passed}/{len(hrms_endpoints)}"
    
    # 3. File Upload API (enhanced with chunked upload)
    print("\n📁 FILE UPLOAD API")
    print("-" * 60)
    
    file_endpoints = [
        ("File Upload", f"{base_url}/upload/file", "POST", {
            "file_name": "test_document.txt",
            "file_size": 100,
            "file_type": "text/plain",
            "chunk_index": 0,
            "total_chunks": 1,
            "file_data": "Test file content for upload testing",
            "upload_id": str(uuid.uuid4())
        })
    ]
    
    file_passed = 0
    for name, url, method, data in file_endpoints:
        results["total_tests"] += 1
        if test_endpoint(name, url, method, data):
            results["passed_tests"] += 1
            file_passed += 1
        else:
            results["failed_tests"] += 1
    
    results["categories"]["File Upload API"] = f"{file_passed}/{len(file_endpoints)}"
    
    # 4. Workflow Templates
    print("\n⚙️ WORKFLOW TEMPLATES")
    print("-" * 60)
    
    workflow_endpoints = [
        ("Get Workflow Templates", f"{base_url}/workflow-templates", "GET", None),
        ("Create Workflow Template", f"{base_url}/workflows", "POST", {
            "name": "Test Lead Qualification",
            "description": "Automated lead qualification workflow",
            "category": "lead_management",
            "steps": [
                {
                    "type": "ai_response",
                    "name": "Initial Assessment",
                    "config": {"prompt": "Assess lead quality", "model": "gpt-5"}
                }
            ]
        })
    ]
    
    workflow_passed = 0
    for name, url, method, data in workflow_endpoints:
        results["total_tests"] += 1
        if test_endpoint(name, url, method, data):
            results["passed_tests"] += 1
            workflow_passed += 1
        else:
            results["failed_tests"] += 1
    
    results["categories"]["Workflow Templates"] = f"{workflow_passed}/{len(workflow_endpoints)}"
    
    # 5. Core CRM APIs
    print("\n📊 CORE CRM APIs")
    print("-" * 60)
    
    crm_endpoints = [
        ("Get Leads", f"{base_url}/leads", "GET", None),
        ("Create Lead", f"{base_url}/leads", "POST", {
            "name": "Test Customer",
            "phone": "9876543210",
            "email": "test@example.com",
            "budget": 60000,
            "space_size": "3 BHK",
            "location": "Mumbai"
        }),
        ("Get Tasks", f"{base_url}/tasks", "GET", None),
        ("Create Task", f"{base_url}/tasks", "POST", {
            "title": "Follow up with test customer",
            "description": "Call to discuss requirements",
            "priority": "High"
        }),
        ("Auth Login", f"{base_url}/auth/login", "POST", {
            "identifier": "admin",
            "password": "admin123"
        })
    ]
    
    crm_passed = 0
    for name, url, method, data in crm_endpoints:
        results["total_tests"] += 1
        if test_endpoint(name, url, method, data):
            results["passed_tests"] += 1
            crm_passed += 1
        else:
            results["failed_tests"] += 1
    
    results["categories"]["Core CRM APIs"] = f"{crm_passed}/{len(crm_endpoints)}"
    
    # Final Results
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE BACKEND TEST RESULTS")
    print("=" * 80)
    
    success_rate = (results["passed_tests"] / results["total_tests"] * 100) if results["total_tests"] > 0 else 0
    
    print(f"📈 OVERALL STATISTICS:")
    print(f"   Total Tests: {results['total_tests']}")
    print(f"   Passed: {results['passed_tests']}")
    print(f"   Failed: {results['failed_tests']}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    print(f"\n📋 CATEGORY BREAKDOWN:")
    for category, result in results["categories"].items():
        print(f"   {category}: {result}")
    
    print(f"\n💡 ASSESSMENT:")
    if success_rate >= 90:
        print("   ✅ EXCELLENT - Backend is production-ready")
    elif success_rate >= 75:
        print("   ⚠️ GOOD - Minor issues to address")
    elif success_rate >= 50:
        print("   🔧 MODERATE - Significant issues need attention")
    else:
        print("   ❌ CRITICAL - Major issues require immediate fixes")
    
    return results

if __name__ == "__main__":
    main()