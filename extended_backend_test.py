import requests
import sys
import json
from datetime import datetime, timezone
import time

class ExtendedAavanaGreensTester:
    def __init__(self, base_url="https://aavana-crm-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

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
                        print(f"   Response: Large data object received")
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

    def test_ai_voice_to_task(self):
        """Test AI Voice-to-Task functionality"""
        voice_data = {
            "voice_input": "Call customer tomorrow for garden consultation",
            "context": {
                "user_role": "sales_manager",
                "current_time": datetime.now().isoformat()
            }
        }
        return self.run_test("AI Voice-to-Task", "POST", "ai/voice-to-task", 200, data=voice_data)

    def test_ai_insights(self):
        """Test AI Insights generation"""
        insight_data = {
            "type": "leads",
            "timeframe": "current"
        }
        return self.run_test("AI Insights Generation", "POST", "ai/insights", 200, data=insight_data)

    def test_ai_content_generation(self):
        """Test AI Content Generation"""
        content_data = {
            "type": "social_post",
            "topic": "Green building solutions and sustainable living",
            "brand_context": "Aavana Greens - Your partner in sustainable green solutions",
            "target_audience": "Homeowners and businesses interested in eco-friendly living"
        }
        return self.run_test("AI Content Generation", "POST", "ai/generate-content", 200, data=content_data)

    def test_erp_products(self):
        """Test ERP Products endpoint"""
        return self.run_test("ERP Products", "GET", "erp/products", 200)

    def test_erp_inventory_alerts(self):
        """Test ERP Inventory Alerts"""
        return self.run_test("ERP Inventory Alerts", "GET", "erp/inventory-alerts", 200)

    def test_erp_invoices(self):
        """Test ERP Invoices"""
        return self.run_test("ERP Invoices", "GET", "erp/invoices", 200)

    def test_erp_projects(self):
        """Test ERP Projects Gallery"""
        return self.run_test("ERP Projects Gallery", "GET", "erp/projects", 200)

    def test_analytics_executive_dashboard(self):
        """Test Analytics Executive Dashboard"""
        return self.run_test("Analytics Executive Dashboard", "GET", "analytics/executive-dashboard", 200)

    def test_hrms_payroll_report(self):
        """Test HRMS Payroll Report"""
        current_date = datetime.now()
        params = {
            "month": current_date.month,
            "year": current_date.year
        }
        return self.run_test("HRMS Payroll Report", "GET", "hrms/payroll-report", 200, params=params)

    def test_admin_system_stats(self):
        """Test Admin System Stats"""
        return self.run_test("Admin System Stats", "GET", "admin/system-stats", 200)

def main():
    print("🚀 Starting Extended Aavana Greens CRM API Tests")
    print("Testing AI, ERP, HRMS, and Analytics endpoints")
    print("=" * 60)
    
    tester = ExtendedAavanaGreensTester()

    # Test AI Endpoints
    print("\n🤖 Testing AI Integration Endpoints...")
    
    print("\n   Testing Voice-to-Task (may take a few seconds)...")
    success, response = tester.test_ai_voice_to_task()
    if success:
        print("   ✨ Voice-to-Task AI is working!")
    
    time.sleep(2)  # Brief pause between AI calls
    
    print("\n   Testing AI Insights Generation...")
    success, response = tester.test_ai_insights()
    if success:
        print("   🧠 AI Insights generation is working!")
    
    time.sleep(2)  # Brief pause between AI calls
    
    print("\n   Testing AI Content Generation...")
    success, response = tester.test_ai_content_generation()
    if success:
        print("   🎨 AI Content generation is working!")

    # Test ERP Endpoints
    print("\n📦 Testing ERP Management Endpoints...")
    tester.test_erp_products()
    tester.test_erp_inventory_alerts()
    tester.test_erp_invoices()
    tester.test_erp_projects()

    # Test Analytics Endpoints
    print("\n📊 Testing Analytics Endpoints...")
    tester.test_analytics_executive_dashboard()

    # Test HRMS Endpoints
    print("\n👥 Testing HRMS Endpoints...")
    tester.test_hrms_payroll_report()

    # Test Admin Endpoints
    print("\n⚙️ Testing Admin Endpoints...")
    tester.test_admin_system_stats()

    # Final Results
    print("\n" + "=" * 60)
    print(f"📊 EXTENDED TEST RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All extended tests passed! All backend endpoints are working correctly.")
        return 0
    else:
        print("⚠️ Some extended tests failed. Check the specific endpoints.")
        return 1

if __name__ == "__main__":
    sys.exit(main())