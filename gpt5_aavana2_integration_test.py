#!/usr/bin/env python3
"""
GPT-5 Integration Testing for Aavana 2.0 CRM System
Comprehensive testing of GPT-5 model integration with CRM-specific functionality
Focus: Performance analysis, context understanding, and feature-specific testing
"""

import requests
import json
import time
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://aavana-greens.preview.emergentagent.com/api"
TIMEOUT = 45  # Increased timeout for AI processing
MAX_RETRIES = 3

class GPT5Aavana2Tester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.response_times = []
        self.session_id = str(uuid.uuid4())
        
    def log_result(self, test_name, status, details="", response_time=0, ai_response=""):
        """Log test result with AI response details"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            print(f"✅ {test_name}: {status} ({response_time:.2f}s)")
            if ai_response:
                print(f"   🤖 AI Response Preview: {ai_response[:100]}...")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: {status} - {details}")
        
        if response_time > 0:
            self.response_times.append(response_time)
        
        self.results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": response_time,
            "ai_response": ai_response[:200] if ai_response else "",
            "timestamp": datetime.now().isoformat()
        })
    
    def test_aavana2_chat(self, message, test_name, expected_keywords=None, max_response_time=10):
        """Test Aavana 2.0 chat endpoint with GPT-5"""
        url = f"{BACKEND_URL}/aavana2/chat"
        
        payload = {
            "message": message,
            "session_id": self.session_id,
            "language": "en",
            "channel": "web",
            "user_context": {
                "role": "sales_executive",
                "department": "sales",
                "company": "Aavana Greens"
            }
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(url, json=payload, timeout=TIMEOUT)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                ai_message = data.get('message', '')
                
                # Check for expected keywords if provided
                keyword_check = True
                if expected_keywords:
                    keyword_check = any(keyword.lower() in ai_message.lower() for keyword in expected_keywords)
                
                # Check response time
                time_check = response_time <= max_response_time
                
                if keyword_check and time_check:
                    self.log_result(test_name, "PASS", 
                                  f"Response time: {response_time:.2f}s, Keywords found: {keyword_check}", 
                                  response_time, ai_message)
                    return data
                else:
                    issues = []
                    if not keyword_check:
                        issues.append("Expected keywords not found")
                    if not time_check:
                        issues.append(f"Response time {response_time:.2f}s > {max_response_time}s")
                    
                    self.log_result(test_name, "PARTIAL", 
                                  f"Issues: {', '.join(issues)}", 
                                  response_time, ai_message)
                    return data
            else:
                self.log_result(test_name, "FAIL", 
                              f"HTTP {response.status_code}: {response.text[:200]}", 
                              response_time)
                return None
                
        except requests.exceptions.Timeout:
            self.log_result(test_name, "FAIL", f"Request timeout after {TIMEOUT}s")
            return None
        except Exception as e:
            self.log_result(test_name, "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_lead_management_queries(self):
        """Test GPT-5 responses for lead management queries"""
        print("\n👥 TESTING LEAD MANAGEMENT AI RESPONSES")
        print("=" * 50)
        
        test_cases = [
            {
                "message": "Help me create a lead for a green building project in Mumbai with a budget of ₹5 lakhs",
                "test_name": "Lead Creation Guidance",
                "keywords": ["lead", "create", "green building", "Mumbai", "budget"],
                "max_time": 8
            },
            {
                "message": "How do I convert prospects into customers for landscaping services?",
                "test_name": "Lead Conversion Strategy",
                "keywords": ["convert", "prospects", "customers", "landscaping", "strategy"],
                "max_time": 8
            },
            {
                "message": "Analyze my lead conversion rate and suggest improvements",
                "test_name": "Lead Analytics & Insights",
                "keywords": ["conversion rate", "analyze", "improvements", "leads"],
                "max_time": 10
            },
            {
                "message": "What's the best way to follow up with a qualified lead interested in balcony gardens?",
                "test_name": "Lead Follow-up Guidance",
                "keywords": ["follow up", "qualified lead", "balcony", "garden"],
                "max_time": 8
            }
        ]
        
        for case in test_cases:
            self.test_aavana2_chat(
                case["message"], 
                case["test_name"], 
                case["keywords"], 
                case["max_time"]
            )
            time.sleep(1)  # Brief pause between requests
    
    def test_hrms_attendance_queries(self):
        """Test GPT-5 responses for HRMS and attendance queries"""
        print("\n👨‍💼 TESTING HRMS & ATTENDANCE AI RESPONSES")
        print("=" * 50)
        
        test_cases = [
            {
                "message": "Guide me through the employee check-in process using face recognition",
                "test_name": "Face Check-in Guidance",
                "keywords": ["check-in", "face recognition", "employee", "process"],
                "max_time": 8
            },
            {
                "message": "How do I manage leave requests for my team members?",
                "test_name": "Leave Management Help",
                "keywords": ["leave requests", "manage", "team members"],
                "max_time": 8
            },
            {
                "message": "Explain the difference between face check-in and GPS check-in",
                "test_name": "Check-in Methods Explanation",
                "keywords": ["face check-in", "GPS check-in", "difference"],
                "max_time": 8
            },
            {
                "message": "Help me track attendance patterns and generate reports",
                "test_name": "Attendance Analytics",
                "keywords": ["attendance", "patterns", "reports", "track"],
                "max_time": 10
            }
        ]
        
        for case in test_cases:
            self.test_aavana2_chat(
                case["message"], 
                case["test_name"], 
                case["keywords"], 
                case["max_time"]
            )
            time.sleep(1)
    
    def test_task_management_queries(self):
        """Test GPT-5 responses for task management queries"""
        print("\n📋 TESTING TASK MANAGEMENT AI RESPONSES")
        print("=" * 50)
        
        test_cases = [
            {
                "message": "Create a follow-up task for a high-priority lead interested in rooftop gardens",
                "test_name": "Task Creation for Leads",
                "keywords": ["task", "follow-up", "high-priority", "rooftop gardens"],
                "max_time": 8
            },
            {
                "message": "How do I organize my daily tasks efficiently?",
                "test_name": "Task Organization Tips",
                "keywords": ["organize", "daily tasks", "efficiently"],
                "max_time": 8
            },
            {
                "message": "Set up automated task reminders for client follow-ups",
                "test_name": "Automated Reminders Setup",
                "keywords": ["automated", "reminders", "client", "follow-ups"],
                "max_time": 8
            },
            {
                "message": "Help me prioritize tasks based on lead value and urgency",
                "test_name": "Task Prioritization Strategy",
                "keywords": ["prioritize", "lead value", "urgency", "tasks"],
                "max_time": 8
            }
        ]
        
        for case in test_cases:
            self.test_aavana2_chat(
                case["message"], 
                case["test_name"], 
                case["keywords"], 
                case["max_time"]
            )
            time.sleep(1)
    
    def test_digital_marketing_queries(self):
        """Test GPT-5 responses for digital marketing queries"""
        print("\n📱 TESTING DIGITAL MARKETING AI RESPONSES")
        print("=" * 50)
        
        test_cases = [
            {
                "message": "Create a marketing campaign for landscaping services targeting Mumbai residents",
                "test_name": "Marketing Campaign Creation",
                "keywords": ["marketing campaign", "landscaping", "Mumbai", "targeting"],
                "max_time": 10
            },
            {
                "message": "Help me with social media content strategy for green building promotion",
                "test_name": "Social Media Strategy",
                "keywords": ["social media", "content strategy", "green building"],
                "max_time": 10
            },
            {
                "message": "Generate content for promoting balcony garden services on Instagram",
                "test_name": "Instagram Content Generation",
                "keywords": ["content", "balcony garden", "Instagram", "promote"],
                "max_time": 10
            },
            {
                "message": "What's the best way to reach customers interested in sustainable living?",
                "test_name": "Sustainable Living Marketing",
                "keywords": ["customers", "sustainable living", "reach"],
                "max_time": 8
            }
        ]
        
        for case in test_cases:
            self.test_aavana2_chat(
                case["message"], 
                case["test_name"], 
                case["keywords"], 
                case["max_time"]
            )
            time.sleep(1)
    
    def test_training_support_queries(self):
        """Test GPT-5 responses for training and support queries"""
        print("\n🎓 TESTING TRAINING & SUPPORT AI RESPONSES")
        print("=" * 50)
        
        test_cases = [
            {
                "message": "How do I use the sales pipeline feature in Aavana Greens CRM?",
                "test_name": "Sales Pipeline Training",
                "keywords": ["sales pipeline", "Aavana Greens", "CRM", "feature"],
                "max_time": 8
            },
            {
                "message": "Train me on the workflow automation system",
                "test_name": "Workflow Automation Training",
                "keywords": ["workflow", "automation", "system", "train"],
                "max_time": 8
            },
            {
                "message": "Explain the analytics dashboard and how to interpret the data",
                "test_name": "Analytics Dashboard Training",
                "keywords": ["analytics", "dashboard", "interpret", "data"],
                "max_time": 8
            },
            {
                "message": "What are the best practices for using AI features in the CRM?",
                "test_name": "AI Features Best Practices",
                "keywords": ["best practices", "AI features", "CRM"],
                "max_time": 8
            }
        ]
        
        for case in test_cases:
            self.test_aavana2_chat(
                case["message"], 
                case["test_name"], 
                case["keywords"], 
                case["max_time"]
            )
            time.sleep(1)
    
    def test_context_understanding(self):
        """Test GPT-5's understanding of Aavana Greens CRM context"""
        print("\n🧠 TESTING CONTEXT UNDERSTANDING")
        print("=" * 40)
        
        # Multi-turn conversation to test context retention
        context_tests = [
            {
                "message": "I have a lead interested in a 3 BHK balcony garden with a budget of ₹75,000",
                "test_name": "Context Setup - Lead Information",
                "keywords": ["3 BHK", "balcony garden", "75,000"],
                "max_time": 8
            },
            {
                "message": "What services should I recommend for this lead?",
                "test_name": "Context Retention - Service Recommendations",
                "keywords": ["services", "recommend", "balcony", "budget"],
                "max_time": 8
            },
            {
                "message": "Create a follow-up task for this lead",
                "test_name": "Context Application - Task Creation",
                "keywords": ["follow-up", "task", "lead"],
                "max_time": 8
            },
            {
                "message": "What's the typical timeline for completing such projects?",
                "test_name": "Context-Aware Timeline Query",
                "keywords": ["timeline", "projects", "completing"],
                "max_time": 8
            }
        ]
        
        for case in context_tests:
            self.test_aavana2_chat(
                case["message"], 
                case["test_name"], 
                case["keywords"], 
                case["max_time"]
            )
            time.sleep(1)
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks for GPT-5 responses"""
        print("\n⚡ TESTING PERFORMANCE BENCHMARKS")
        print("=" * 40)
        
        # Quick response tests
        quick_tests = [
            "Hello, how can you help me today?",
            "What is Aavana Greens?",
            "Show me the main features",
            "Thank you for your help"
        ]
        
        for i, message in enumerate(quick_tests, 1):
            self.test_aavana2_chat(
                message, 
                f"Quick Response Test {i}", 
                None, 
                3  # Expect quick responses under 3 seconds
            )
            time.sleep(0.5)
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n🛡️ TESTING ERROR HANDLING")
        print("=" * 35)
        
        error_tests = [
            {
                "message": "",  # Empty message
                "test_name": "Empty Message Handling",
                "keywords": None,
                "max_time": 5
            },
            {
                "message": "x" * 1000,  # Very long message
                "test_name": "Long Message Handling",
                "keywords": None,
                "max_time": 15
            },
            {
                "message": "What is the weather like today?",  # Off-topic query
                "test_name": "Off-topic Query Handling",
                "keywords": ["Aavana", "CRM", "help"],
                "max_time": 8
            }
        ]
        
        for case in error_tests:
            self.test_aavana2_chat(
                case["message"], 
                case["test_name"], 
                case["keywords"], 
                case["max_time"]
            )
            time.sleep(1)
    
    def run_comprehensive_gpt5_test(self):
        """Run all GPT-5 integration tests"""
        print("🚀 GPT-5 INTEGRATION TESTING FOR AAVANA 2.0 CRM")
        print("=" * 55)
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"⏰ Timeout: {TIMEOUT}s")
        print(f"🆔 Session ID: {self.session_id}")
        print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test different CRM functionality areas
        self.test_lead_management_queries()
        self.test_hrms_attendance_queries()
        self.test_task_management_queries()
        self.test_digital_marketing_queries()
        self.test_training_support_queries()
        self.test_context_understanding()
        self.test_performance_benchmarks()
        self.test_error_handling()
        
        # Print comprehensive summary
        self.print_comprehensive_summary()
    
    def print_comprehensive_summary(self):
        """Print detailed test summary with performance analysis"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE GPT-5 INTEGRATION TEST SUMMARY")
        print("=" * 70)
        
        # Basic stats
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"⚠️ Partial: {len([r for r in self.results if r['status'] == 'PARTIAL'])}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📈 Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")
        
        # Performance analysis
        if self.response_times:
            avg_time = sum(self.response_times) / len(self.response_times)
            max_time = max(self.response_times)
            min_time = min(self.response_times)
            
            print(f"\n⚡ PERFORMANCE ANALYSIS:")
            print(f"   📊 Average Response Time: {avg_time:.2f}s")
            print(f"   🚀 Fastest Response: {min_time:.2f}s")
            print(f"   🐌 Slowest Response: {max_time:.2f}s")
            
            # Performance categories
            fast_responses = len([t for t in self.response_times if t <= 3])
            medium_responses = len([t for t in self.response_times if 3 < t <= 8])
            slow_responses = len([t for t in self.response_times if t > 8])
            
            print(f"   🟢 Fast (≤3s): {fast_responses} tests")
            print(f"   🟡 Medium (3-8s): {medium_responses} tests")
            print(f"   🔴 Slow (>8s): {slow_responses} tests")
        
        # Feature-specific results
        print(f"\n🎯 FEATURE-SPECIFIC RESULTS:")
        
        categories = {
            "Lead Management": ["Lead Creation", "Lead Conversion", "Lead Analytics", "Lead Follow-up"],
            "HRMS & Attendance": ["Face Check-in", "Leave Management", "Check-in Methods", "Attendance Analytics"],
            "Task Management": ["Task Creation", "Task Organization", "Automated Reminders", "Task Prioritization"],
            "Digital Marketing": ["Marketing Campaign", "Social Media", "Instagram Content", "Sustainable Living"],
            "Training & Support": ["Sales Pipeline", "Workflow Automation", "Analytics Dashboard", "AI Features"],
            "Context Understanding": ["Context Setup", "Context Retention", "Context Application", "Context-Aware"],
            "Performance": ["Quick Response", "Performance"],
            "Error Handling": ["Empty Message", "Long Message", "Off-topic"]
        }
        
        for category, keywords in categories.items():
            category_results = [r for r in self.results if any(kw in r['test'] for kw in keywords)]
            if category_results:
                passed = len([r for r in category_results if r['status'] == 'PASS'])
                total = len(category_results)
                print(f"   {category}: {passed}/{total} passed ({(passed/total*100):.0f}%)")
        
        # Critical findings
        print(f"\n🔍 CRITICAL FINDINGS:")
        
        # Check for consistent failures
        failed_tests = [r for r in self.results if r['status'] == 'FAIL']
        if failed_tests:
            print(f"🚨 FAILED TESTS ({len(failed_tests)}):")
            for result in failed_tests:
                print(f"   ❌ {result['test']}: {result['details']}")
        
        # Check for slow responses
        slow_tests = [r for r in self.results if r['response_time'] > 10]
        if slow_tests:
            print(f"⏰ SLOW RESPONSES (>10s) ({len(slow_tests)}):")
            for result in slow_tests:
                print(f"   🐌 {result['test']}: {result['response_time']:.2f}s")
        
        # Context understanding assessment
        context_tests = [r for r in self.results if 'Context' in r['test']]
        context_passed = len([r for r in context_tests if r['status'] == 'PASS'])
        if context_tests:
            context_rate = (context_passed / len(context_tests)) * 100
            print(f"🧠 CONTEXT UNDERSTANDING: {context_rate:.0f}% ({context_passed}/{len(context_tests)})")
        
        # CRM-specific functionality assessment
        crm_keywords = ['Lead', 'Task', 'HRMS', 'Marketing', 'Pipeline', 'Analytics']
        crm_tests = [r for r in self.results if any(kw in r['test'] for kw in crm_keywords)]
        crm_passed = len([r for r in crm_tests if r['status'] == 'PASS'])
        if crm_tests:
            crm_rate = (crm_passed / len(crm_tests)) * 100
            print(f"🏢 CRM FUNCTIONALITY: {crm_rate:.0f}% ({crm_passed}/{len(crm_tests)})")
        
        # Final assessment
        print(f"\n🏆 FINAL ASSESSMENT:")
        overall_score = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        if overall_score >= 90:
            print("🟢 EXCELLENT: GPT-5 integration is working exceptionally well")
        elif overall_score >= 75:
            print("🟡 GOOD: GPT-5 integration is working well with minor issues")
        elif overall_score >= 60:
            print("🟠 FAIR: GPT-5 integration has some issues that need attention")
        else:
            print("🔴 POOR: GPT-5 integration has significant issues requiring immediate attention")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if avg_time > 8:
            print("   ⚡ Consider optimizing response times for better user experience")
        if failed_tests:
            print("   🔧 Address failed test cases to improve reliability")
        if slow_tests:
            print("   🚀 Optimize slow-responding queries for better performance")
        
        print("   ✅ Continue monitoring GPT-5 performance in production")
        print("   📊 Consider A/B testing with different AI models for comparison")

if __name__ == "__main__":
    print("🚀 Starting GPT-5 Integration Testing for Aavana 2.0...")
    tester = GPT5Aavana2Tester()
    tester.run_comprehensive_gpt5_test()
    
    # Exit with appropriate code
    if tester.failed_tests > 0:
        print(f"\n⚠️ Testing completed with {tester.failed_tests} failures")
        sys.exit(1)
    else:
        print(f"\n🎉 All tests passed successfully!")
        sys.exit(0)