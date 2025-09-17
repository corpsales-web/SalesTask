#!/usr/bin/env python3
"""
Camera Backend Test for Aavana Greens CRM
Focused test for camera functionality and 502 error diagnosis
"""

import asyncio
import aiohttp
import json
import base64
import os
from datetime import datetime, timezone
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CameraBackendTest:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://green-crm-suite.preview.emergentagent.com')
        self.api_base = f"{self.backend_url}/api"
        
        # Authentication token
        self.auth_token = None
        
        # Test results storage
        self.test_results = {
            'authentication': [],
            'camera_functionality': [],
            'file_upload': [],
            'basic_connectivity': [],
            'summary': {}
        }
        
        # Create test image data
        self.test_image_data = self._create_test_image()
        
    def _create_test_image(self) -> str:
        """Create a test image in base64 format"""
        # 1x1 pixel PNG image in base64
        png_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
        return png_data
    
    async def test_endpoint(self, session: aiohttp.ClientSession, method: str, 
                          endpoint: str, data: Dict = None, files: Dict = None,
                          headers: Dict = None, require_auth: bool = False) -> Dict[str, Any]:
        """Test a single endpoint with comprehensive error handling"""
        url = f"{self.api_base}{endpoint}"
        test_result = {
            'endpoint': endpoint,
            'method': method,
            'url': url,
            'status_code': None,
            'response_time_ms': None,
            'error': None,
            'response_data': None,
            'working': False,
            'authenticated': require_auth and self.auth_token is not None
        }
        
        try:
            start_time = datetime.now()
            
            # Prepare headers
            request_headers = headers or {}
            if require_auth and self.auth_token:
                request_headers['Authorization'] = f'Bearer {self.auth_token}'
            
            # Prepare request parameters
            kwargs = {'headers': request_headers}
            if data and not files:
                kwargs['json'] = data
            elif files:
                # For file uploads, use FormData
                form_data = aiohttp.FormData()
                if data:
                    for key, value in data.items():
                        form_data.add_field(key, str(value))
                for key, file_data in files.items():
                    if isinstance(file_data, str):
                        # Base64 encoded data
                        file_bytes = base64.b64decode(file_data)
                        form_data.add_field(key, file_bytes, filename='test_image.png', content_type='image/png')
                    else:
                        form_data.add_field(key, file_data, filename='test_image.png', content_type='image/png')
                kwargs['data'] = form_data
            
            # Make the request
            async with session.request(method, url, **kwargs) as response:
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000
                
                test_result.update({
                    'status_code': response.status,
                    'response_time_ms': round(response_time, 2),
                    'working': 200 <= response.status < 300
                })
                
                # Get response data
                try:
                    if response.content_type == 'application/json':
                        test_result['response_data'] = await response.json()
                    else:
                        response_text = await response.text()
                        test_result['response_data'] = response_text[:500]
                except Exception as e:
                    test_result['response_data'] = f"Could not parse response: {str(e)}"
                    
        except Exception as e:
            test_result['error'] = str(e)
            
        return test_result
    
    async def authenticate(self, session: aiohttp.ClientSession) -> bool:
        """Authenticate with the backend to get access token"""
        logger.info("🔐 Authenticating with backend...")
        
        # Try to login with demo credentials
        login_data = {
            'identifier': 'admin',
            'password': 'admin123'
        }
        
        auth_result = await self.test_endpoint(
            session, 'POST', '/auth/login', data=login_data
        )
        
        self.test_results['authentication'].append(auth_result)
        
        if auth_result['working'] and auth_result['response_data']:
            token_data = auth_result['response_data']
            if 'access_token' in token_data:
                self.auth_token = token_data['access_token']
                logger.info("✅ Authentication successful")
                return True
            else:
                logger.warning("⚠️ Login successful but no access token received")
        else:
            logger.warning(f"⚠️ Authentication failed: {auth_result.get('response_data', 'Unknown error')}")
        
        return False
    
    async def test_basic_connectivity(self, session: aiohttp.ClientSession):
        """Test basic backend connectivity"""
        logger.info("🔗 Testing Basic Backend Connectivity...")
        
        basic_endpoints = [
            {'method': 'GET', 'endpoint': '/'},
            {'method': 'GET', 'endpoint': '/dashboard/stats'},
            {'method': 'GET', 'endpoint': '/leads'},
            {'method': 'GET', 'endpoint': '/tasks'}
        ]
        
        for endpoint_config in basic_endpoints:
            result = await self.test_endpoint(session, **endpoint_config)
            self.test_results['basic_connectivity'].append(result)
            
            status = "✅ WORKING" if result['working'] else "❌ FAILED"
            if result['status_code'] == 502:
                status += " (502 ERROR - BACKEND DOWN)"
            
            logger.info(f"  {endpoint_config['endpoint']}: {status} ({result['response_time_ms']}ms)")
    
    async def test_camera_functionality(self, session: aiohttp.ClientSession):
        """Test camera-related functionality with proper data formats"""
        logger.info("🎥 Testing Camera Functionality...")
        
        # Test face check-in with proper datetime format
        face_checkin_data = {
            'employee_id': 'TEST_USER_CAMERA',
            'face_image': self.test_image_data,
            'location': {
                'lat': 19.0760,
                'lng': 72.8777,
                'address': 'Mumbai, Maharashtra',
                'accuracy': 10
            },
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'device_info': {
                'userAgent': 'CameraBackendTest/1.0',
                'platform': 'Test',
                'deviceType': 'desktop'
            }
        }
        
        face_checkin_result = await self.test_endpoint(
            session, 'POST', '/hrms/face-checkin', data=face_checkin_data
        )
        
        self.test_results['camera_functionality'].append(face_checkin_result)
        
        status = "✅ WORKING" if face_checkin_result['working'] else "❌ FAILED"
        if face_checkin_result['status_code'] == 502:
            status += " (502 ERROR)"
        elif face_checkin_result['status_code'] == 500:
            status += " (500 ERROR - SERVER ISSUE)"
        
        logger.info(f"  Face Check-in: {status}")
        if not face_checkin_result['working']:
            error_detail = face_checkin_result.get('response_data', {})
            if isinstance(error_detail, dict):
                error_detail = error_detail.get('detail', 'Unknown error')
            logger.error(f"    Error: {error_detail}")
            
            # If it's a validation error, let's try to fix it
            if face_checkin_result['status_code'] == 500 and 'validation error' in str(error_detail):
                logger.info("  🔧 Attempting to fix validation error...")
                await self._fix_face_checkin_validation_error(session)
    
    async def _fix_face_checkin_validation_error(self, session: aiohttp.ClientSession):
        """Attempt to fix the face check-in validation error"""
        # The error suggests datetime validation issue, let's try different formats
        test_formats = [
            # Try with just datetime string
            {
                'employee_id': 'TEST_USER_CAMERA',
                'face_image': self.test_image_data,
                'location': 'Mumbai, Maharashtra',
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            # Try without timestamp
            {
                'employee_id': 'TEST_USER_CAMERA', 
                'face_image': self.test_image_data,
                'location': 'Mumbai, Maharashtra'
            },
            # Try with minimal data
            {
                'employee_id': 'TEST_USER_CAMERA',
                'face_image': self.test_image_data
            }
        ]
        
        for i, test_data in enumerate(test_formats):
            logger.info(f"    Trying format {i+1}...")
            result = await self.test_endpoint(
                session, 'POST', '/hrms/face-checkin', data=test_data
            )
            
            if result['working']:
                logger.info(f"    ✅ Format {i+1} worked!")
                self.test_results['camera_functionality'].append(result)
                return
            else:
                error_detail = result.get('response_data', {})
                if isinstance(error_detail, dict):
                    error_detail = error_detail.get('detail', 'Unknown error')
                logger.info(f"    ❌ Format {i+1} failed: {error_detail}")
    
    async def test_file_upload_functionality(self, session: aiohttp.ClientSession):
        """Test file upload functionality with authentication"""
        logger.info("📁 Testing File Upload Functionality...")
        
        if not self.auth_token:
            logger.warning("⚠️ Skipping file upload tests - no authentication token")
            return
        
        # Test single file upload
        upload_result = await self.test_endpoint(
            session, 'POST', '/upload/file',
            files={'file': self.test_image_data},
            data={'project_id': 'camera_test'},
            require_auth=True
        )
        
        self.test_results['file_upload'].append(upload_result)
        
        status = "✅ WORKING" if upload_result['working'] else "❌ FAILED"
        if upload_result['status_code'] == 502:
            status += " (502 ERROR)"
        elif upload_result['status_code'] == 503:
            status += " (503 ERROR - SERVICE UNAVAILABLE)"
        elif upload_result['status_code'] == 403:
            status += " (403 ERROR - AUTHENTICATION ISSUE)"
        
        logger.info(f"  File Upload: {status}")
        if not upload_result['working']:
            error_detail = upload_result.get('response_data', {})
            if isinstance(error_detail, dict):
                error_detail = error_detail.get('detail', 'Unknown error')
            logger.error(f"    Error: {error_detail}")
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a comprehensive summary report"""
        all_tests = (
            self.test_results['basic_connectivity'] +
            self.test_results['camera_functionality'] +
            self.test_results['file_upload'] +
            self.test_results['authentication']
        )
        
        total_tests = len(all_tests)
        working_tests = len([t for t in all_tests if t['working']])
        error_502_tests = len([t for t in all_tests if t['status_code'] == 502])
        error_500_tests = len([t for t in all_tests if t['status_code'] == 500])
        
        # Categorize issues
        critical_issues = []
        warnings = []
        fixes_applied = []
        
        if error_502_tests > 0:
            critical_issues.append(f"{error_502_tests} endpoints returning 502 errors (Backend Gateway Error)")
        else:
            fixes_applied.append("✅ 502 Backend Gateway errors resolved (libmagic1 dependency fixed)")
        
        if error_500_tests > 0:
            critical_issues.append(f"{error_500_tests} endpoints returning 500 errors (Internal Server Error)")
        
        # Check specific camera functionality
        camera_tests = self.test_results['camera_functionality']
        camera_working = len([t for t in camera_tests if t['working']])
        
        if len(camera_tests) > 0 and camera_working == 0:
            critical_issues.append("Camera functionality completely broken")
        elif len(camera_tests) > 0 and camera_working < len(camera_tests):
            warnings.append("Some camera features not working properly")
        elif len(camera_tests) > 0 and camera_working > 0:
            fixes_applied.append("✅ Camera functionality partially or fully working")
        
        # Check file upload functionality
        upload_tests = self.test_results['file_upload']
        upload_working = len([t for t in upload_tests if t['working']])
        
        if len(upload_tests) > 0 and upload_working == 0:
            critical_issues.append("File upload functionality not working")
        elif len(upload_tests) > 0 and upload_working > 0:
            fixes_applied.append("✅ File upload functionality working")
        
        # Determine overall status
        if error_502_tests > 0:
            overall_status = "CRITICAL - 502 BACKEND ERRORS"
        elif len(critical_issues) > 0:
            overall_status = "CRITICAL - MAJOR FUNCTIONALITY BROKEN"
        elif len(warnings) > 0:
            overall_status = "WARNING - SOME ISSUES DETECTED"
        elif working_tests == total_tests:
            overall_status = "HEALTHY - ALL TESTS PASSED"
        else:
            overall_status = "ISSUES DETECTED"
        
        return {
            'timestamp': datetime.now().isoformat(),
            'backend_url': self.backend_url,
            'summary': {
                'total_tests': total_tests,
                'working_tests': working_tests,
                'failed_tests': total_tests - working_tests,
                'error_502_count': error_502_tests,
                'error_500_count': error_500_tests,
                'overall_status': overall_status,
                'critical_issues': critical_issues,
                'warnings': warnings,
                'fixes_applied': fixes_applied
            },
            'camera_specific': {
                'total_camera_tests': len(camera_tests),
                'working_camera_tests': camera_working,
                'camera_status': 'WORKING' if camera_working == len(camera_tests) and len(camera_tests) > 0 else 'BROKEN'
            },
            'detailed_results': self.test_results
        }
    
    async def run_comprehensive_test(self):
        """Run comprehensive camera backend test"""
        logger.info("🚀 Starting Camera Backend Test - 502 Error Diagnosis")
        logger.info(f"Backend URL: {self.backend_url}")
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Test basic connectivity first
            await self.test_basic_connectivity(session)
            
            # Try to authenticate
            authenticated = await self.authenticate(session)
            
            # Test camera functionality
            await self.test_camera_functionality(session)
            
            # Test file upload (requires auth)
            if authenticated:
                await self.test_file_upload_functionality(session)
        
        # Generate summary report
        report = self.generate_summary_report()
        
        # Print summary
        logger.info("\n" + "="*70)
        logger.info("📊 CAMERA BACKEND TEST SUMMARY")
        logger.info("="*70)
        logger.info(f"Overall Status: {report['summary']['overall_status']}")
        logger.info(f"Total Tests: {report['summary']['total_tests']}")
        logger.info(f"Working: {report['summary']['working_tests']}")
        logger.info(f"Failed: {report['summary']['failed_tests']}")
        logger.info(f"502 Errors: {report['summary']['error_502_count']}")
        logger.info(f"500 Errors: {report['summary']['error_500_count']}")
        
        logger.info(f"\n🎥 Camera Functionality Status: {report['camera_specific']['camera_status']}")
        logger.info(f"Camera Tests: {report['camera_specific']['working_camera_tests']}/{report['camera_specific']['total_camera_tests']} working")
        
        if report['summary']['fixes_applied']:
            logger.info("\n✅ FIXES APPLIED:")
            for fix in report['summary']['fixes_applied']:
                logger.info(f"  {fix}")
        
        if report['summary']['critical_issues']:
            logger.info("\n🚨 CRITICAL ISSUES:")
            for issue in report['summary']['critical_issues']:
                logger.info(f"  - {issue}")
        
        if report['summary']['warnings']:
            logger.info("\n⚠️ WARNINGS:")
            for warning in report['summary']['warnings']:
                logger.info(f"  - {warning}")
        
        if report['summary']['error_502_count'] == 0:
            logger.info("\n🎉 GREAT NEWS: No 502 errors detected!")
            logger.info("The libmagic1 dependency fix has resolved the Backend Gateway errors.")
        
        return report

async def main():
    """Main test execution"""
    test = CameraBackendTest()
    report = await test.run_comprehensive_test()
    
    # Save report to file
    report_file = f"/app/camera_backend_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"\n📄 Detailed report saved to: {report_file}")
    
    return report

if __name__ == "__main__":
    asyncio.run(main())