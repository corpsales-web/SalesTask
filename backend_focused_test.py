#!/usr/bin/env python3
"""
CRM Backend Focused Test Suite
Tests specific areas requested in review:
1) Projects & Albums: create project and album, list albums by project
2) Catalogue upload: init (with project_id & album_id), chunk, state, complete; list filtered by project_id and album_id
3) Training: upload PDF via /api/training/upload and list by feature filter; confirm URLs are /api/files/training/*
"""

import requests
import json
import time
import uuid
import io
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Configuration - Use external URL from frontend .env
BASE_URL = "https://crm-visual-studio.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

class CRMFocusedTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_projects = []
        self.created_albums = []
        self.created_uploads = []
        self.created_training = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def create_test_pdf_content(self) -> bytes:
        """Create a simple PDF content for testing"""
        # Simple PDF header and content
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test PDF Content) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""
        return pdf_content

    # ========== PROJECTS & ALBUMS TESTS ==========
    
    def test_create_project(self):
        """Test POST /api/projects - create a new project"""
        try:
            project_data = {
                "name": f"Test Project {uuid.uuid4().hex[:8]}",
                "description": "Test project for backend testing"
            }
            
            response = self.session.post(
                f"{API_BASE}/projects",
                json=project_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "project" in data:
                    project = data["project"]
                    # Verify required fields
                    required_fields = ["id", "name", "created_at"]
                    missing_fields = [field for field in required_fields if field not in project]
                    
                    if not missing_fields:
                        # Verify UUID format
                        try:
                            uuid.UUID(project["id"])
                            self.created_projects.append(project["id"])
                            self.log_test("Create Project", True, 
                                        f"Created project with ID: {project['id']}")
                            return project["id"]
                        except ValueError:
                            self.log_test("Create Project", False, "Invalid UUID format", data)
                    else:
                        self.log_test("Create Project", False, 
                                    f"Missing fields: {missing_fields}", data)
                else:
                    self.log_test("Create Project", False, "No project in response", data)
            else:
                self.log_test("Create Project", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Create Project", False, f"Error: {str(e)}")
        return None
    
    def test_create_album(self, project_id: str):
        """Test POST /api/albums - create a new album for a project"""
        try:
            album_data = {
                "project_id": project_id,
                "name": f"Test Album {uuid.uuid4().hex[:8]}",
                "description": "Test album for backend testing"
            }
            
            response = self.session.post(
                f"{API_BASE}/albums",
                json=album_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "album" in data:
                    album = data["album"]
                    # Verify required fields
                    required_fields = ["id", "project_id", "name", "created_at"]
                    missing_fields = [field for field in required_fields if field not in album]
                    
                    if not missing_fields:
                        # Verify UUID format and project_id match
                        try:
                            uuid.UUID(album["id"])
                            if album["project_id"] == project_id:
                                self.created_albums.append(album["id"])
                                self.log_test("Create Album", True, 
                                            f"Created album with ID: {album['id']} for project: {project_id}")
                                return album["id"]
                            else:
                                self.log_test("Create Album", False, 
                                            f"Project ID mismatch: expected {project_id}, got {album['project_id']}", data)
                        except ValueError:
                            self.log_test("Create Album", False, "Invalid UUID format", data)
                    else:
                        self.log_test("Create Album", False, 
                                    f"Missing fields: {missing_fields}", data)
                else:
                    self.log_test("Create Album", False, "No album in response", data)
            else:
                self.log_test("Create Album", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Create Album", False, f"Error: {str(e)}")
        return None
    
    def test_list_albums_by_project(self, project_id: str):
        """Test GET /api/albums?project_id=X - list albums filtered by project"""
        try:
            response = self.session.get(
                f"{API_BASE}/albums?project_id={project_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data and isinstance(data["items"], list):
                    albums = data["items"]
                    # Verify all albums belong to the project
                    wrong_project = [album for album in albums 
                                   if isinstance(album, dict) and album.get("project_id") != project_id]
                    
                    if not wrong_project:
                        # Verify no _id fields
                        has_mongo_id = any("_id" in album for album in albums if isinstance(album, dict))
                        if not has_mongo_id:
                            self.log_test("List Albums by Project", True, 
                                        f"Retrieved {len(albums)} albums for project {project_id}")
                            return True
                        else:
                            self.log_test("List Albums by Project", False, 
                                        "Response contains _id fields", albums[:2])
                    else:
                        self.log_test("List Albums by Project", False, 
                                    f"Found {len(wrong_project)} albums with wrong project_id", wrong_project[:2])
                else:
                    self.log_test("List Albums by Project", False, "Invalid response format", data)
            else:
                self.log_test("List Albums by Project", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("List Albums by Project", False, f"Error: {str(e)}")
        return False

    # ========== CATALOGUE UPLOAD TESTS ==========
    
    def test_catalogue_upload_init(self, project_id: str, album_id: str):
        """Test POST /api/uploads/catalogue/init with project_id and album_id"""
        try:
            init_data = {
                "filename": "test_catalogue_file.jpg",
                "file_size": 2048000,  # 2MB
                "chunk_size": 1048576,  # 1MB chunks
                "total_chunks": 2,
                "category": "image",
                "tags": "test,catalogue",
                "project_id": project_id,
                "album_id": album_id
            }
            
            response = self.session.post(
                f"{API_BASE}/uploads/catalogue/init",
                json=init_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "upload_id" in data:
                    upload_id = data["upload_id"]
                    # Verify UUID format
                    try:
                        uuid.UUID(upload_id)
                        self.created_uploads.append(upload_id)
                        self.log_test("Catalogue Upload Init", True, 
                                    f"Initialized upload with ID: {upload_id}")
                        return upload_id
                    except ValueError:
                        self.log_test("Catalogue Upload Init", False, "Invalid upload_id UUID", data)
                else:
                    self.log_test("Catalogue Upload Init", False, "Invalid response format", data)
            else:
                self.log_test("Catalogue Upload Init", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Catalogue Upload Init", False, f"Error: {str(e)}")
        return None
    
    def test_catalogue_upload_chunk(self, upload_id: str, chunk_number: int, chunk_data: bytes):
        """Test POST /api/uploads/catalogue/chunk - upload a chunk"""
        try:
            files = {
                'chunk': ('chunk', io.BytesIO(chunk_data), 'application/octet-stream')
            }
            data = {
                'upload_id': upload_id,
                'chunk_number': str(chunk_number),
                'total': '2'
            }
            
            response = self.session.post(
                f"{API_BASE}/uploads/catalogue/chunk",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                resp_data = response.json()
                if resp_data.get("success") and "index" in resp_data:
                    if resp_data["index"] == chunk_number:
                        self.log_test(f"Catalogue Upload Chunk {chunk_number}", True, 
                                    f"Uploaded chunk {chunk_number} successfully")
                        return True
                    else:
                        self.log_test(f"Catalogue Upload Chunk {chunk_number}", False, 
                                    f"Index mismatch: expected {chunk_number}, got {resp_data['index']}", resp_data)
                else:
                    self.log_test(f"Catalogue Upload Chunk {chunk_number}", False, 
                                "Invalid response format", resp_data)
            else:
                self.log_test(f"Catalogue Upload Chunk {chunk_number}", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test(f"Catalogue Upload Chunk {chunk_number}", False, f"Error: {str(e)}")
        return False
    
    def test_catalogue_upload_state(self, upload_id: str):
        """Test GET /api/uploads/catalogue/state - check upload state"""
        try:
            response = self.session.get(
                f"{API_BASE}/uploads/catalogue/state?upload_id={upload_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["exists", "parts", "status"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    if data.get("exists") and data.get("parts") >= 0:
                        self.log_test("Catalogue Upload State", True, 
                                    f"State check: exists={data['exists']}, parts={data['parts']}, status={data['status']}")
                        return True
                    else:
                        self.log_test("Catalogue Upload State", False, 
                                    "Invalid state values", data)
                else:
                    self.log_test("Catalogue Upload State", False, 
                                f"Missing fields: {missing_fields}", data)
            else:
                self.log_test("Catalogue Upload State", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Catalogue Upload State", False, f"Error: {str(e)}")
        return False
    
    def test_catalogue_upload_complete(self, upload_id: str, project_id: str, album_id: str):
        """Test POST /api/uploads/catalogue/complete - complete the upload"""
        try:
            complete_data = {
                "upload_id": upload_id,
                "filename": "test_catalogue_file.jpg",
                "category": "image",
                "tags": "test,catalogue,completed",
                "project_id": project_id,
                "album_id": album_id,
                "title": "Test Catalogue Item",
                "description": "Test catalogue item for backend testing"
            }
            
            response = self.session.post(
                f"{API_BASE}/uploads/catalogue/complete",
                json=complete_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "file" in data:
                    file_info = data["file"]
                    required_fields = ["id", "upload_id", "filename", "url", "status", "created_at"]
                    missing_fields = [field for field in required_fields if field not in file_info]
                    
                    if not missing_fields:
                        # Verify UUID and URL format
                        try:
                            uuid.UUID(file_info["id"])
                            url = file_info["url"]
                            if "/api/files/catalogue/" in url and file_info["status"] == "completed":
                                self.log_test("Catalogue Upload Complete", True, 
                                            f"Completed upload: {file_info['id']}, URL: {url}")
                                return file_info["id"]
                            else:
                                self.log_test("Catalogue Upload Complete", False, 
                                            f"Invalid URL format or status: {url}, status: {file_info['status']}", data)
                        except ValueError:
                            self.log_test("Catalogue Upload Complete", False, "Invalid file ID UUID", data)
                    else:
                        self.log_test("Catalogue Upload Complete", False, 
                                    f"Missing fields: {missing_fields}", data)
                else:
                    self.log_test("Catalogue Upload Complete", False, "Invalid response format", data)
            else:
                self.log_test("Catalogue Upload Complete", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Catalogue Upload Complete", False, f"Error: {str(e)}")
        return None
    
    def test_catalogue_list_filtered(self, project_id: str, album_id: str):
        """Test GET /api/uploads/catalogue/list with project_id and album_id filters"""
        try:
            response = self.session.get(
                f"{API_BASE}/uploads/catalogue/list?project_id={project_id}&album_id={album_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "catalogues" in data and isinstance(data["catalogues"], list):
                    catalogues = data["catalogues"]
                    # Verify all items belong to the project and album
                    wrong_filters = [item for item in catalogues 
                                   if isinstance(item, dict) and 
                                   (item.get("project_id") != project_id or item.get("album_id") != album_id)]
                    
                    if not wrong_filters:
                        # Verify no _id fields and URLs are present
                        has_mongo_id = any("_id" in item for item in catalogues if isinstance(item, dict))
                        has_urls = all("url" in item for item in catalogues if isinstance(item, dict))
                        
                        if not has_mongo_id and has_urls:
                            self.log_test("Catalogue List Filtered", True, 
                                        f"Retrieved {len(catalogues)} catalogue items for project {project_id}, album {album_id}")
                            return True
                        else:
                            issues = []
                            if has_mongo_id: issues.append("contains _id fields")
                            if not has_urls: issues.append("missing URLs")
                            self.log_test("Catalogue List Filtered", False, 
                                        f"Issues: {', '.join(issues)}", catalogues[:2])
                    else:
                        self.log_test("Catalogue List Filtered", False, 
                                    f"Found {len(wrong_filters)} items with wrong filters", wrong_filters[:2])
                else:
                    self.log_test("Catalogue List Filtered", False, "Invalid response format", data)
            else:
                self.log_test("Catalogue List Filtered", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Catalogue List Filtered", False, f"Error: {str(e)}")
        return False

    # ========== TRAINING TESTS ==========
    
    def test_training_upload_pdf(self, feature: str = "crm"):
        """Test POST /api/training/upload - upload a PDF file"""
        try:
            pdf_content = self.create_test_pdf_content()
            
            files = {
                'file': ('test_training.pdf', io.BytesIO(pdf_content), 'application/pdf')
            }
            data = {
                'title': f'Test Training Module - {feature.upper()}',
                'feature': feature
            }
            
            response = self.session.post(
                f"{API_BASE}/training/upload",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                resp_data = response.json()
                if "module" in resp_data:
                    module = resp_data["module"]
                    required_fields = ["id", "title", "type", "url", "feature", "created_at"]
                    missing_fields = [field for field in required_fields if field not in module]
                    
                    if not missing_fields:
                        # Verify UUID, type, and URL format
                        try:
                            uuid.UUID(module["id"])
                            url = module["url"]
                            if (module["type"] == "pdf" and 
                                "/api/files/training/" in url and 
                                module["feature"] == feature):
                                self.created_training.append(module["id"])
                                self.log_test("Training Upload PDF", True, 
                                            f"Uploaded PDF: {module['id']}, URL: {url}")
                                return module["id"]
                            else:
                                issues = []
                                if module["type"] != "pdf": issues.append(f"wrong type: {module['type']}")
                                if "/api/files/training/" not in url: issues.append(f"wrong URL format: {url}")
                                if module["feature"] != feature: issues.append(f"wrong feature: {module['feature']}")
                                self.log_test("Training Upload PDF", False, 
                                            f"Validation issues: {', '.join(issues)}", resp_data)
                        except ValueError:
                            self.log_test("Training Upload PDF", False, "Invalid module ID UUID", resp_data)
                    else:
                        self.log_test("Training Upload PDF", False, 
                                    f"Missing fields: {missing_fields}", resp_data)
                else:
                    self.log_test("Training Upload PDF", False, "No module in response", resp_data)
            else:
                self.log_test("Training Upload PDF", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Training Upload PDF", False, f"Error: {str(e)}")
        return None
    
    def test_training_list_by_feature(self, feature: str = "crm"):
        """Test GET /api/training/modules?feature=X - list training modules by feature"""
        try:
            response = self.session.get(
                f"{API_BASE}/training/modules?feature={feature}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data and isinstance(data["items"], list):
                    modules = data["items"]
                    # Verify all modules have the correct feature
                    wrong_feature = [module for module in modules 
                                   if isinstance(module, dict) and module.get("feature") != feature]
                    
                    if not wrong_feature:
                        # Verify URLs for PDF modules contain /api/files/training/
                        pdf_modules = [module for module in modules 
                                     if isinstance(module, dict) and module.get("type") == "pdf"]
                        # Check for both http and https URLs since backend might return http
                        wrong_urls = [module for module in pdf_modules 
                                    if not (module.get("url", "").startswith(f"{BASE_URL}/api/files/training/") or
                                           module.get("url", "").startswith(f"{BASE_URL.replace('https://', 'http://')}/api/files/training/"))]
                        
                        if not wrong_urls:
                            self.log_test("Training List by Feature", True, 
                                        f"Retrieved {len(modules)} training modules for feature '{feature}', {len(pdf_modules)} PDFs with correct URLs")
                            return True
                        else:
                            self.log_test("Training List by Feature", False, 
                                        f"Found {len(wrong_urls)} PDF modules with incorrect URLs", wrong_urls[:2])
                    else:
                        self.log_test("Training List by Feature", False, 
                                    f"Found {len(wrong_feature)} modules with wrong feature", wrong_feature[:2])
                else:
                    self.log_test("Training List by Feature", False, "Invalid response format", data)
            else:
                self.log_test("Training List by Feature", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Training List by Feature", False, f"Error: {str(e)}")
        return False
    
    def test_training_url_accessibility(self):
        """Test that training PDF URLs are accessible"""
        if not self.created_training:
            self.log_test("Training URL Accessibility", False, "No training modules to test")
            return False
        
        try:
            # Get the latest training modules to find URLs
            response = self.session.get(f"{API_BASE}/training/modules", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                modules = data.get("items", [])
                pdf_modules = [module for module in modules 
                             if isinstance(module, dict) and 
                             module.get("type") == "pdf" and 
                             module.get("id") in self.created_training]
                
                if pdf_modules:
                    # Test accessibility of the first PDF URL
                    test_module = pdf_modules[0]
                    pdf_url = test_module.get("url")
                    
                    if pdf_url:
                        # Try HTTPS version first, then HTTP if 301 redirect
                        https_url = pdf_url.replace('http://', 'https://')
                        
                        # Make a HEAD request to check if URL is accessible
                        head_response = self.session.head(https_url, timeout=30, allow_redirects=True)
                        
                        if head_response.status_code == 200:
                            self.log_test("Training URL Accessibility", True, 
                                        f"PDF URL accessible: {https_url}")
                            return True
                        else:
                            # Try original URL if HTTPS fails
                            head_response2 = self.session.head(pdf_url, timeout=30, allow_redirects=True)
                            if head_response2.status_code == 200:
                                self.log_test("Training URL Accessibility", True, 
                                            f"PDF URL accessible: {pdf_url}")
                                return True
                            else:
                                self.log_test("Training URL Accessibility", False, 
                                            f"PDF URL not accessible: {pdf_url} (HTTP {head_response2.status_code}), HTTPS: {https_url} (HTTP {head_response.status_code})")
                    else:
                        self.log_test("Training URL Accessibility", False, "No URL found in module")
                else:
                    self.log_test("Training URL Accessibility", False, "No PDF modules found to test")
            else:
                self.log_test("Training URL Accessibility", False, 
                            f"Failed to get training modules: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Training URL Accessibility", False, f"Error: {str(e)}")
        return False

    # ========== MAIN TEST EXECUTION ==========
    
    def run_all_tests(self):
        """Run all focused tests in sequence"""
        print("🚀 Starting CRM Backend Focused Test Suite")
        print("=" * 70)
        print("📋 Testing: Projects & Albums, Catalogue Upload, Training")
        print("=" * 70)
        
        # Test 1: Projects & Albums
        print("\n1️⃣ Testing Projects & Albums...")
        project_id = self.test_create_project()
        if project_id:
            album_id = self.test_create_album(project_id)
            if album_id:
                self.test_list_albums_by_project(project_id)
            else:
                print("❌ Skipping album list test - album creation failed")
        else:
            print("❌ Skipping album tests - project creation failed")
        
        # Test 2: Catalogue Upload (requires project and album)
        print("\n2️⃣ Testing Catalogue Upload...")
        if project_id and album_id:
            upload_id = self.test_catalogue_upload_init(project_id, album_id)
            if upload_id:
                # Upload chunks
                chunk1_data = b"A" * 1048576  # 1MB of 'A's
                chunk2_data = b"B" * 1048576  # 1MB of 'B's
                
                chunk1_success = self.test_catalogue_upload_chunk(upload_id, 0, chunk1_data)
                chunk2_success = self.test_catalogue_upload_chunk(upload_id, 1, chunk2_data)
                
                if chunk1_success and chunk2_success:
                    self.test_catalogue_upload_state(upload_id)
                    file_id = self.test_catalogue_upload_complete(upload_id, project_id, album_id)
                    if file_id:
                        self.test_catalogue_list_filtered(project_id, album_id)
                else:
                    print("❌ Skipping upload completion - chunk upload failed")
            else:
                print("❌ Skipping catalogue upload tests - init failed")
        else:
            print("❌ Skipping catalogue upload tests - no project/album available")
        
        # Test 3: Training
        print("\n3️⃣ Testing Training...")
        training_features = ["crm", "sales", "general"]
        for feature in training_features:
            module_id = self.test_training_upload_pdf(feature)
            if module_id:
                self.test_training_list_by_feature(feature)
        
        # Test training URL accessibility
        self.test_training_url_accessibility()
        
        # Summary
        self.print_summary()
        
        return self.get_overall_success()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 FOCUSED TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        # Show created items
        print(f"\n📝 Created Items:")
        print(f"  • Projects: {len(self.created_projects)}")
        print(f"  • Albums: {len(self.created_albums)}")
        print(f"  • Uploads: {len(self.created_uploads)}")
        print(f"  • Training Modules: {len(self.created_training)}")
        
        # Check for 500 errors
        server_errors = [result for result in self.test_results 
                        if not result["success"] and "500" in result["details"]]
        if server_errors:
            print(f"\n⚠️  CRITICAL: Found {len(server_errors)} tests with 500 errors!")
            for error in server_errors:
                print(f"  • {error['test']}: {error['details']}")
        else:
            print("\n✅ NO 500 ERRORS DETECTED")
    
    def get_overall_success(self):
        """Get overall test success status"""
        if not self.test_results:
            return False
        
        # Critical tests that must pass
        critical_tests = [
            "Create Project",
            "Create Album", 
            "List Albums by Project",
            "Catalogue Upload Init",
            "Catalogue Upload Complete",
            "Catalogue List Filtered",
            "Training Upload PDF",
            "Training List by Feature"
        ]
        
        critical_passed = all(
            any(result["test"] == test and result["success"] for result in self.test_results)
            for test in critical_tests
        )
        
        # Check for any 500 errors
        has_500_errors = any("500" in result["details"] for result in self.test_results if not result["success"])
        
        return critical_passed and not has_500_errors

def main():
    """Main test execution"""
    tester = CRMFocusedTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ CRM Backend focused tests completed successfully!")
        exit(0)
    else:
        print("\n❌ CRM Backend focused tests had critical failures!")
        exit(1)

if __name__ == "__main__":
    main()