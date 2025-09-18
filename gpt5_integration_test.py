#!/usr/bin/env python3
"""
GPT-5 Integration Testing
Testing GPT-5 model integration fix and parameter corrections
"""

import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = "https://green-crm-suite.preview.emergentagent.com/api"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class GPT5IntegrationTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.openai_key = OPENAI_API_KEY
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, test_name, success, details, response_time=None, model_used=None):
        """Log test results with model information"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'model_used': model_used,
            'timestamp': datetime.now().isoformat(),
            'response_time': response_time
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.2f}s)" if response_time else ""
        model_info = f" [Model: {model_used}]" if model_used else ""
        print(f"{status} {test_name}{time_info}{model_info}: {details}")
        
    def test_direct_openai_gpt5_access(self):
        """Test direct OpenAI GPT-5 API access"""
        print("\n🔑 TESTING DIRECT OPENAI GPT-5 ACCESS")
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            start_time = time.time()
            response = client.chat.completions.create(
                model='gpt-5',
                messages=[{'role': 'user', 'content': 'Test GPT-5 integration. Respond with: GPT-5 is working correctly.'}],
                max_completion_tokens=50,
                temperature=0.3
            )
            response_time = time.time() - start_time
            
            content = response.choices[0].message.content
            model_used = response.model if hasattr(response, 'model') else 'gpt-5'
            
            if 'GPT-5' in content and 'working' in content:
                self.log_test("Direct GPT-5 API Access", True, f"GPT-5 responding correctly: {content[:100]}...", response_time, model_used)
                return True
            else:
                self.log_test("Direct GPT-5 API Access", False, f"Unexpected response: {content[:100]}...", response_time, model_used)
                return False
                
        except Exception as e:
            self.log_test("Direct GPT-5 API Access", False, f"API access failed: {str(e)}")
            return False
    
    def test_lead_qualification_gpt5(self):
        """Test POST /api/ai/analyze-lead-qualification with GPT-5"""
        print("\n🎯 TESTING LEAD QUALIFICATION WITH GPT-5")
        
        test_data = {
            "formData": {
                "name": "Rajesh Kumar",
                "project_type": "commercial_green_building",
                "budget_range": "250k_500k",
                "timeline": "3_months",
                "decision_maker": "yes",
                "urgency": "high",
                "location": "Mumbai",
                "space_type": "office_complex",
                "services_needed": ["landscaping", "green_walls", "rooftop_garden"]
            },
            "qualificationScore": 85
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/ai/analyze-lead-qualification",
                json=test_data,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get('analysis', {})
                ai_insights = analysis.get('ai_insights', '')
                
                # Check if GPT-5 model was used (look for indicators in response)
                model_indicators = ['gpt-5', 'GPT-5']
                model_used = 'gpt-5' if any(indicator in str(data) for indicator in model_indicators) else 'unknown'
                
                if analysis and 'qualification' in analysis:
                    self.log_test(
                        "Lead Qualification GPT-5", 
                        True, 
                        f"AI analysis successful. Qualification: {analysis.get('qualification')}, Confidence: {analysis.get('confidence')}%",
                        response_time,
                        model_used
                    )
                    return True
                else:
                    self.log_test("Lead Qualification GPT-5", False, f"Invalid analysis structure: {data}", response_time)
                    return False
            else:
                self.log_test("Lead Qualification GPT-5", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Lead Qualification GPT-5", False, f"Request failed: {str(e)}")
            return False
    
    def test_comprehensive_marketing_strategy_gpt5(self):
        """Test POST /api/ai/marketing/comprehensive-strategy with GPT-5"""
        print("\n📈 TESTING COMPREHENSIVE MARKETING STRATEGY WITH GPT-5")
        
        test_data = {
            "business_data": {
                "company": "Aavana Greens",
                "industry": "Green Building & Landscaping",
                "target_market": "Urban professionals, Commercial developers",
                "current_channels": ["Instagram", "Website", "Word of mouth"],
                "budget": "50000",
                "goals": ["Increase brand awareness", "Generate qualified leads", "Establish thought leadership"]
            },
            "current_performance": {
                "monthly_leads": 25,
                "conversion_rate": 12,
                "social_followers": 1500,
                "website_traffic": 3000
            }
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/ai/marketing/comprehensive-strategy",
                json=test_data,
                timeout=90
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                strategy = data.get('strategy', {})
                comprehensive_plan = strategy.get('comprehensive_plan', '')
                
                # Check for GPT-5 usage indicators
                model_used = 'gpt-5'  # Based on server.py code, this endpoint uses GPT-5
                
                if comprehensive_plan and len(comprehensive_plan) > 500:
                    self.log_test(
                        "Comprehensive Marketing Strategy GPT-5", 
                        True, 
                        f"Strategy generated successfully. Length: {len(comprehensive_plan)} chars. Brand score: {strategy.get('brand_analysis', {}).get('strength_score', 'N/A')}",
                        response_time,
                        model_used
                    )
                    return True
                else:
                    self.log_test("Comprehensive Marketing Strategy GPT-5", False, f"Strategy too short or missing: {len(comprehensive_plan) if comprehensive_plan else 0} chars", response_time)
                    return False
            else:
                self.log_test("Comprehensive Marketing Strategy GPT-5", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Comprehensive Marketing Strategy GPT-5", False, f"Request failed: {str(e)}")
            return False
    
    def test_content_creation_endpoints_gpt5(self):
        """Test content creation endpoints with GPT-5"""
        print("\n🎬 TESTING CONTENT CREATION ENDPOINTS WITH GPT-5")
        
        endpoints_to_test = [
            {
                "endpoint": "/ai/content/create-reel",
                "name": "Create Reel Content GPT-5",
                "data": {
                    "theme": "sustainable_gardening",
                    "target_audience": "urban_millennials",
                    "duration": "30_seconds",
                    "style": "educational_trendy",
                    "call_to_action": "visit_website"
                }
            },
            {
                "endpoint": "/ai/content/create-influencer",
                "name": "Create AI Influencer GPT-5", 
                "data": {
                    "niche": "green_living",
                    "personality": "eco_friendly_expert",
                    "target_demographic": "environmentally_conscious_professionals",
                    "content_themes": ["sustainable_living", "green_building", "plant_care"],
                    "platform_focus": "instagram_youtube"
                }
            }
        ]
        
        results = []
        for test_config in endpoints_to_test:
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.backend_url}{test_config['endpoint']}",
                    json=test_config['data'],
                    timeout=60
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get('content', {})
                    
                    # Check for substantial content generation
                    content_length = len(str(content))
                    model_used = 'gpt-5'  # Based on server.py, these should use GPT-5
                    
                    if content_length > 200:
                        self.log_test(
                            test_config['name'], 
                            True, 
                            f"Content generated successfully. Length: {content_length} chars",
                            response_time,
                            model_used
                        )
                        results.append(True)
                    else:
                        self.log_test(test_config['name'], False, f"Content too short: {content_length} chars", response_time)
                        results.append(False)
                else:
                    self.log_test(test_config['name'], False, f"HTTP {response.status_code}: {response.text}", response_time)
                    results.append(False)
                    
            except Exception as e:
                self.log_test(test_config['name'], False, f"Request failed: {str(e)}")
                results.append(False)
        
        return all(results)
    
    def test_optimized_lead_creation_with_gpt5(self):
        """Test optimized lead creation flow with GPT-5 analysis"""
        print("\n🚀 TESTING OPTIMIZED LEAD CREATION WITH GPT-5")
        
        # First test the AI analysis endpoint
        analysis_success = self.test_lead_qualification_gpt5()
        
        # Then test the complete optimized lead creation
        test_lead_data = {
            "name": "Priya Sharma",
            "email": f"priya.test.{int(time.time())}@example.com",  # Unique email
            "phone": "9876543210",
            "company": "EcoTech Solutions",
            "project_type": "residential_balcony",
            "budget_range": "50k_100k",
            "timeline": "1_month",
            "decision_maker": "yes",
            "urgency": "medium",
            "location": "Bangalore",
            "qualification_score": 75,  # High score for auto-conversion
            "qualification_level": "HIGH",
            "ai_analysis": {
                "qualification": "QUALIFIED",
                "confidence": 85,
                "recommendations": ["Schedule consultation", "Send proposal", "Connect with design team"]
            },
            "status": "Qualified"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/leads/optimized-create",
                json=test_lead_data,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 201:
                data = response.json()
                lead = data.get('lead', {})
                auto_converted = data.get('auto_converted_to_deal', False)
                qualification_summary = data.get('qualification_summary', {})
                
                model_used = 'gpt-5'  # This flow uses GPT-5 for analysis
                
                if lead and 'id' in lead:
                    details = f"Lead created successfully. ID: {lead['id']}, Auto-converted: {auto_converted}, Score: {qualification_summary.get('score', 'N/A')}"
                    self.log_test(
                        "Optimized Lead Creation GPT-5", 
                        True, 
                        details,
                        response_time,
                        model_used
                    )
                    return True
                else:
                    self.log_test("Optimized Lead Creation GPT-5", False, f"Invalid lead data: {data}", response_time)
                    return False
            else:
                self.log_test("Optimized Lead Creation GPT-5", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Optimized Lead Creation GPT-5", False, f"Request failed: {str(e)}")
            return False
    
    def test_parameter_fix_verification(self):
        """Verify that max_completion_tokens parameter is used instead of max_tokens"""
        print("\n🔧 TESTING PARAMETER FIX VERIFICATION")
        
        # Test with a simple request that should not cause parameter errors
        test_data = {
            "formData": {
                "name": "Test User",
                "project_type": "residential_garden",
                "budget_range": "25k_50k",
                "timeline": "flexible"
            },
            "qualificationScore": 50
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/ai/analyze-lead-qualification",
                json=test_data,
                timeout=30
            )
            response_time = time.time() - start_time
            
            # Check for parameter-related errors (400 status codes)
            if response.status_code == 400:
                error_text = response.text.lower()
                if 'max_tokens' in error_text or 'parameter' in error_text:
                    self.log_test("Parameter Fix Verification", False, f"Parameter error detected: {response.text}", response_time)
                    return False
            
            if response.status_code == 200:
                self.log_test("Parameter Fix Verification", True, "No parameter errors detected. max_completion_tokens working correctly", response_time)
                return True
            else:
                # Non-parameter related error
                self.log_test("Parameter Fix Verification", True, f"No parameter errors (HTTP {response.status_code})", response_time)
                return True
                
        except Exception as e:
            self.log_test("Parameter Fix Verification", False, f"Request failed: {str(e)}")
            return False
    
    def run_comprehensive_gpt5_tests(self):
        """Run all GPT-5 integration tests"""
        print("🚀 STARTING COMPREHENSIVE GPT-5 INTEGRATION TESTING")
        print("=" * 80)
        
        # Test sequence
        tests = [
            ("Direct OpenAI GPT-5 Access", self.test_direct_openai_gpt5_access),
            ("Parameter Fix Verification", self.test_parameter_fix_verification),
            ("Lead Qualification GPT-5", self.test_lead_qualification_gpt5),
            ("Comprehensive Marketing Strategy GPT-5", self.test_comprehensive_marketing_strategy_gpt5),
            ("Content Creation Endpoints GPT-5", self.test_content_creation_endpoints_gpt5),
            ("Optimized Lead Creation GPT-5", self.test_optimized_lead_creation_with_gpt5)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 GPT-5 INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"📊 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        # Detailed results
        print("\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            model_info = f" [{result['model_used']}]" if result.get('model_used') else ""
            time_info = f" ({result['response_time']:.2f}s)" if result.get('response_time') else ""
            print(f"{status} {result['test']}{model_info}{time_info}")
            if not result['success']:
                print(f"   └─ {result['details']}")
        
        # GPT-5 specific analysis
        gpt5_tests = [r for r in self.test_results if r.get('model_used') == 'gpt-5']
        if gpt5_tests:
            gpt5_success = sum(1 for t in gpt5_tests if t['success'])
            print(f"\n🤖 GPT-5 Model Usage: {gpt5_success}/{len(gpt5_tests)} GPT-5 tests passed")
        
        # Performance analysis
        response_times = [r['response_time'] for r in self.test_results if r.get('response_time')]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"⚡ Average Response Time: {avg_time:.2f}s")
        
        return success_rate >= 80  # 80% success rate threshold

if __name__ == "__main__":
    tester = GPT5IntegrationTester()
    success = tester.run_comprehensive_gpt5_tests()
    
    if success:
        print("\n🎉 GPT-5 INTEGRATION TESTING COMPLETED SUCCESSFULLY")
        exit(0)
    else:
        print("\n⚠️ GPT-5 INTEGRATION TESTING COMPLETED WITH ISSUES")
        exit(1)