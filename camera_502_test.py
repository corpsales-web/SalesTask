#!/usr/bin/env python3
"""
Camera 502 Error Diagnostic Test for Aavana Greens CRM
Tests all camera-related endpoints and file upload functionality
"""

import asyncio
import aiohttp
import json
import base64
import io
import os
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Camera502DiagnosticTest:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://green-crm-suite.preview.emergentagent.com')
        self.api_base = f"{self.backend_url}/api"
        
        # Test results storage
        self.test_results = {
            'camera_endpoints': [],
            'file_upload_endpoints': [],
            'image_processing_endpoints': [],
            'cors_tests': [],
            'authentication_tests': [],
            'overall_status': 'UNKNOWN'
        }
        
        # Create a simple test image (1x1 pixel PNG)
        self.test_image_data = self._create_test_image()
        
    def _create_test_image(self) -> bytes:
        """Create a minimal test image for upload testing"""
        # 1x1 pixel PNG image in base64
        png_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
        return base64.b64decode(png_data)
    
    async def test_endpoint(self, session: aiohttp.ClientSession, method: str, 
                          endpoint: str, data: Dict = None, files: Dict = None,
                          headers: Dict = None) -> Dict[str, Any]:
        """Test a single endpoint and return detailed results"""
        url = f"{self.api_base}{endpoint}"
        test_result = {
            'endpoint': endpoint,
            'method': method,
            'url': url,
            'status_code': None,
            'response_time_ms': None,
            'error': None,
            'response_data': None,
            'headers_received': None,
            'is_502_error': False,
            'working': False
        }
        
        try:
            start_time = datetime.now()
            
            # Prepare request parameters
            kwargs = {}
            if headers:
                kwargs['headers'] = headers
            if data and not files:
                kwargs['json'] = data
            elif files:
                # For file uploads, use FormData
                form_data = aiohttp.FormData()
                if data:
                    for key, value in data.items():
                        form_data.add_field(key, str(value))
                for key, file_data in files.items():
                    form_data.add_field(key, file_data, filename='test_image.png', content_type='image/png')
                kwargs['data'] = form_data
            
            # Make the request
            async with session.request(method, url, **kwargs) as response:
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000
                
                test_result.update({
                    'status_code': response.status,
                    'response_time_ms': round(response_time, 2),
                    'headers_received': dict(response.headers),
                    'is_502_error': response.status == 502,
                    'working': 200 <= response.status < 300
                })
                
                # Try to get response data
                try:
                    if response.content_type == 'application/json':
                        test_result['response_data'] = await response.json()
                    else:
                        response_text = await response.text()
                        test_result['response_data'] = response_text[:500]  # Limit response size
                except Exception as e:
                    test_result['response_data'] = f"Could not parse response: {str(e)}"
                    
        except aiohttp.ClientError as e:
            test_result['error'] = f"Client error: {str(e)}"
        except asyncio.TimeoutError:
            test_result['error'] = "Request timeout"
        except Exception as e:
            test_result['error'] = f"Unexpected error: {str(e)}"
            
        return test_result
    
    async def test_camera_endpoints(self, session: aiohttp.ClientSession):
        """Test all camera-related endpoints"""
        logger.info("🎥 Testing Camera-Related Endpoints...")
        
        camera_endpoints = [
            # Face check-in endpoint (main camera functionality)
            {
                'method': 'POST',
                'endpoint': '/hrms/face-checkin',
                'data': {
                    'employee_id': 'TEST_USER',
                    'face_image': base64.b64encode(self.test_image_data).decode('utf-8'),
                    'location': {
                        'lat': 19.0760,
                        'lng': 72.8777,
                        'address': 'Mumbai, Maharashtra',
                        'accuracy': 10
                    },
                    'timestamp': datetime.now().isoformat(),
                    'device_info': {
                        'userAgent': 'Camera502Test/1.0',
                        'platform': 'Test',
                        'deviceType': 'desktop'
                    }
                }
            }
        ]
        
        for endpoint_config in camera_endpoints:
            result = await self.test_endpoint(session, **endpoint_config)
            self.test_results['camera_endpoints'].append(result)
            
            status = "✅ WORKING" if result['working'] else "❌ FAILED"
            if result['is_502_error']:
                status += " (502 ERROR)"
            
            logger.info(f"  {endpoint_config['endpoint']}: {status}")
            if result['error']:
                logger.error(f"    Error: {result['error']}")
    
    async def test_file_upload_endpoints(self, session: aiohttp.ClientSession):
        """Test file upload endpoints that camera might use"""
        logger.info("📁 Testing File Upload Endpoints...")
        
        upload_endpoints = [
            # Single file upload
            {
                'method': 'POST',
                'endpoint': '/upload/file',
                'files': {'file': self.test_image_data},
                'data': {'project_id': 'camera_test'}
            },
            # Multiple file upload
            {
                'method': 'POST',
                'endpoint': '/upload/multiple',
                'files': {'files': self.test_image_data},
                'data': {'project_id': 'camera_test'}
            },
            # Presigned URL generation
            {
                'method': 'POST',
                'endpoint': '/upload/presigned-url',
                'data': {
                    'filename': 'camera_capture.png',
                    'content_type': 'image/png'
                }
            }
        ]
        
        for endpoint_config in upload_endpoints:
            result = await self.test_endpoint(session, **endpoint_config)
            self.test_results['file_upload_endpoints'].append(result)
            
            status = "✅ WORKING" if result['working'] else "❌ FAILED"
            if result['is_502_error']:
                status += " (502 ERROR)"
                
            logger.info(f"  {endpoint_config['endpoint']}: {status}")
            if result['error']:
                logger.error(f"    Error: {result['error']}")
    
    async def test_image_processing_endpoints(self, session: aiohttp.ClientSession):
        """Test any image processing or media-related endpoints"""
        logger.info("🖼️ Testing Image Processing Endpoints...")
        
        # Test AI endpoints that might process images
        ai_endpoints = [
            {
                'method': 'POST',
                'endpoint': '/ai/generate-content',
                'data': {
                    'type': 'image_analysis',
                    'content': 'Analyze this camera capture for face recognition',
                    'context': {'image_data': base64.b64encode(self.test_image_data).decode('utf-8')}
                }
            }
        ]
        
        for endpoint_config in ai_endpoints:
            result = await self.test_endpoint(session, **endpoint_config)
            self.test_results['image_processing_endpoints'].append(result)
            
            status = "✅ WORKING" if result['working'] else "❌ FAILED"
            if result['is_502_error']:
                status += " (502 ERROR)"
                
            logger.info(f"  {endpoint_config['endpoint']}: {status}")
            if result['error']:
                logger.error(f"    Error: {result['error']}")
    
    async def test_cors_configuration(self, session: aiohttp.ClientSession):
        """Test CORS configuration for camera requests"""
        logger.info("🌐 Testing CORS Configuration...")
        
        # Test preflight request
        cors_test = await self.test_endpoint(
            session, 
            'OPTIONS', 
            '/hrms/face-checkin',
            headers={
                'Origin': 'https://green-crm-suite.preview.emergentagent.com',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        )
        
        self.test_results['cors_tests'].append(cors_test)
        
        status = "✅ WORKING" if cors_test['working'] or cors_test['status_code'] == 200 else "❌ FAILED"
        logger.info(f"  CORS Preflight: {status}")
        
        # Check CORS headers
        if cors_test['headers_received']:
            cors_headers = {k: v for k, v in cors_test['headers_received'].items() 
                          if k.lower().startswith('access-control')}
            if cors_headers:
                logger.info(f"  CORS Headers: {cors_headers}")
            else:
                logger.warning("  No CORS headers found in response")
    
    async def test_authentication_requirements(self, session: aiohttp.ClientSession):
        """Test authentication requirements for camera endpoints"""
        logger.info("🔐 Testing Authentication Requirements...")
        
        # Test without authentication
        unauth_test = await self.test_endpoint(
            session,
            'POST',
            '/hrms/face-checkin',
            data={'employee_id': 'TEST_USER', 'face_image': 'test'}
        )
        
        self.test_results['authentication_tests'].append(unauth_test)
        
        if unauth_test['status_code'] == 401:
            logger.info("  ✅ Authentication required (401) - Security working")
        elif unauth_test['status_code'] == 502:
            logger.error("  ❌ 502 Error - Backend not responding")
        else:
            logger.info(f"  ℹ️ Unexpected status: {unauth_test['status_code']}")
    
    async def test_basic_connectivity(self, session: aiohttp.ClientSession):
        """Test basic backend connectivity"""
        logger.info("🔗 Testing Basic Backend Connectivity...")
        
        basic_endpoints = [
            {'method': 'GET', 'endpoint': '/'},
            {'method': 'GET', 'endpoint': '/dashboard/stats'},
            {'method': 'GET', 'endpoint': '/leads'},
            {'method': 'GET', 'endpoint': '/tasks'}
        ]
        
        connectivity_results = []
        for endpoint_config in basic_endpoints:
            result = await self.test_endpoint(session, **endpoint_config)
            connectivity_results.append(result)
            
            status = "✅ WORKING" if result['working'] else "❌ FAILED"
            if result['is_502_error']:
                status += " (502 ERROR)"
                
            logger.info(f"  {endpoint_config['endpoint']}: {status}")
        
        return connectivity_results
    
    def analyze_502_errors(self):
        """Analyze all 502 errors found during testing"""
        logger.info("🔍 Analyzing 502 Errors...")
        
        all_results = (
            self.test_results['camera_endpoints'] +
            self.test_results['file_upload_endpoints'] +
            self.test_results['image_processing_endpoints'] +
            self.test_results['cors_tests'] +
            self.test_results['authentication_tests']
        )
        
        error_502_endpoints = [r for r in all_results if r['is_502_error']]
        
        if error_502_endpoints:
            logger.error(f"Found {len(error_502_endpoints)} endpoints with 502 errors:")
            for result in error_502_endpoints:
                logger.error(f"  - {result['method']} {result['endpoint']}")
                if result['response_data']:
                    logger.error(f"    Response: {result['response_data']}")
        else:
            logger.info("✅ No 502 errors found!")
        
        return error_502_endpoints
    
    def generate_diagnostic_report(self) -> Dict[str, Any]:
        """Generate comprehensive diagnostic report"""
        all_results = (
            self.test_results['camera_endpoints'] +
            self.test_results['file_upload_endpoints'] +
            self.test_results['image_processing_endpoints']
        )
        
        total_tests = len(all_results)
        working_tests = len([r for r in all_results if r['working']])
        error_502_tests = len([r for r in all_results if r['is_502_error']])
        
        # Determine overall status
        if error_502_tests > 0:
            overall_status = "CRITICAL - 502 ERRORS DETECTED"
        elif working_tests == total_tests:
            overall_status = "HEALTHY - ALL TESTS PASSED"
        elif working_tests > total_tests * 0.7:
            overall_status = "WARNING - SOME ISSUES DETECTED"
        else:
            overall_status = "CRITICAL - MULTIPLE FAILURES"
        
        self.test_results['overall_status'] = overall_status
        
        return {
            'timestamp': datetime.now().isoformat(),
            'backend_url': self.backend_url,
            'summary': {
                'total_tests': total_tests,
                'working_tests': working_tests,
                'failed_tests': total_tests - working_tests,
                'error_502_count': error_502_tests,
                'overall_status': overall_status
            },
            'detailed_results': self.test_results
        }
    
    async def run_comprehensive_test(self):
        """Run all camera-related tests"""
        logger.info("🚀 Starting Comprehensive Camera 502 Error Diagnostic Test")
        logger.info(f"Backend URL: {self.backend_url}")
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Test basic connectivity first
            connectivity_results = await self.test_basic_connectivity(session)
            
            # Test camera-specific functionality
            await self.test_camera_endpoints(session)
            await self.test_file_upload_endpoints(session)
            await self.test_image_processing_endpoints(session)
            await self.test_cors_configuration(session)
            await self.test_authentication_requirements(session)
        
        # Analyze results
        error_502_endpoints = self.analyze_502_errors()
        report = self.generate_diagnostic_report()
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("📊 CAMERA 502 ERROR DIAGNOSTIC SUMMARY")
        logger.info("="*60)
        logger.info(f"Overall Status: {report['summary']['overall_status']}")
        logger.info(f"Total Tests: {report['summary']['total_tests']}")
        logger.info(f"Working: {report['summary']['working_tests']}")
        logger.info(f"Failed: {report['summary']['failed_tests']}")
        logger.info(f"502 Errors: {report['summary']['error_502_count']}")
        
        if error_502_endpoints:
            logger.info("\n🚨 CRITICAL FINDINGS:")
            logger.info("The following endpoints are returning 502 errors:")
            for result in error_502_endpoints:
                logger.info(f"  - {result['method']} {result['endpoint']}")
            logger.info("\nRECOMMENDATIONS:")
            logger.info("1. Check backend service status: sudo supervisorctl status backend")
            logger.info("2. Check backend logs: tail -f /var/log/supervisor/backend.*.log")
            logger.info("3. Verify all dependencies are installed")
            logger.info("4. Check if file upload service is properly configured")
        
        return report

async def main():
    """Main test execution"""
    test = Camera502DiagnosticTest()
    report = await test.run_comprehensive_test()
    
    # Save report to file
    report_file = f"/app/camera_502_diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"\n📄 Detailed report saved to: {report_file}")
    
    return report

if __name__ == "__main__":
    asyncio.run(main())