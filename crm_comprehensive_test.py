#!/usr/bin/env python3
"""
CRM Backend Comprehensive QA Test Suite
Tests all CRM backend endpoints with emphasis on file access via /api/files/*
"""

import requests
import json
import time
import uuid
import os
import io
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Configuration - Use frontend env for backend URL
FRONTEND_ENV_PATH = "/app/frontend/.env"
def get_backend_url():
    try:
        with open(FRONTEND_ENV_PATH, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return "https://crm-visual-studio.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

class CRMComprehensiveTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_items = []  # Track created items for cleanup
        self.test_data = {}  # Store test data between tests
        
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
    
    def create_test_file_content(self, size_mb: int = 1) -> bytes:
        """Create test file content of specified size"""
        content = b"Test file content for CRM backend testing. " * (size_mb * 1024 * 24)  # Approximate 1MB
        return content[:size_mb * 1024 * 1024]  # Exact size
    
    # ========== BACKEND CONNECTIVITY CHECK ==========
    def test_backend_connectivity(self):
        """Test backend connectivity using leads endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/leads?limit=1", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "items" in data and "total" in data:
                    self.log_test("Backend Connectivity", True, f"Backend accessible, {data.get('total', 0)} leads in system")
                    return True
                else:
                    self.log_test("Backend Connectivity", False, "Invalid response format", data)
            else:
                self.log_test("Backend Connectivity", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Backend Connectivity", False, f"Connection error: {str(e)}")
        return False
    
    # ========== VISUAL UPGRADES ==========
    def test_visual_upgrades_render(self):
        """Test POST /api/visual-upgrades/render with image upload"""
        try:
            # Create test image content
            image_content = self.create_test_file_content(1)  # 1MB test image
            
            files = {
                'image': ('test_image.png', io.BytesIO(image_content), 'image/png')
            }
            data = {
                'prompt': 'Enhance this image with better lighting',
                'size': '1024x1024',
                'lead_id': str(uuid.uuid4()),
                'response_format': 'url'
            }
            
            response = self.session.post(
                f"{API_BASE}/visual-upgrades/render",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if (result.get("success") and 
                    "upgrade" in result and 
                    "result" in result["upgrade"] and
                    "url" in result["upgrade"]["result"]):
                    
                    upgrade = result["upgrade"]
                    self.test_data["visual_upgrade_id"] = upgrade.get("id")
                    self.test_data["visual_lead_id"] = upgrade.get("lead_id")
                    
                    # Verify the result URL is accessible via /api/files/*
                    result_url = upgrade["result"]["url"]
                    if "/api/files/visual/" in result_url:
                        self.log_test("Visual Upgrades Render", True, 
                                    f"Image processed, result URL: {result_url}")
                        return True
                    else:
                        self.log_test("Visual Upgrades Render", False, 
                                    f"Result URL not using /api/files/* pattern: {result_url}", result)
                else:
                    self.log_test("Visual Upgrades Render", False, "Invalid response format", result)
            else:
                self.log_test("Visual Upgrades Render", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Visual Upgrades Render", False, f"Error: {str(e)}")
        return False
    
    def test_visual_upgrades_list(self):
        """Test GET /api/visual-upgrades/list with lead_id filter"""
        try:
            lead_id = self.test_data.get("visual_lead_id")
            url = f"{API_BASE}/visual-upgrades/list"
            if lead_id:
                url += f"?lead_id={lead_id}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data and isinstance(data["items"], list):
                    # Verify no _id fields
                    has_mongo_id = any("_id" in item for item in data["items"] if isinstance(item, dict))
                    if not has_mongo_id:
                        self.log_test("Visual Upgrades List", True, 
                                    f"Retrieved {len(data['items'])} visual upgrades without _id")
                        return True
                    else:
                        self.log_test("Visual Upgrades List", False, "Contains _id fields", data)
                else:
                    self.log_test("Visual Upgrades List", False, "Invalid response format", data)
            else:
                self.log_test("Visual Upgrades List", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Visual Upgrades List", False, f"Error: {str(e)}")
        return False
    
    # ========== PROJECTS & ALBUMS ==========
    def test_create_project(self):
        """Test POST /api/projects"""
        try:
            project_data = {
                "name": "Test Project for Catalogue",
                "description": "Project created for comprehensive testing"
            }
            
            response = self.session.post(
                f"{API_BASE}/projects",
                json=project_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "project" in data and "id" in data["project"]:
                    project_id = data["project"]["id"]
                    self.test_data["project_id"] = project_id
                    self.created_items.append(("project", project_id))
                    self.log_test("Create Project", True, f"Created project: {project_id}")
                    return True
                else:
                    self.log_test("Create Project", False, "Invalid response format", data)
            else:
                self.log_test("Create Project", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Create Project", False, f"Error: {str(e)}")
        return False
    
    def test_create_album(self):
        """Test POST /api/albums"""
        try:
            project_id = self.test_data.get("project_id")
            if not project_id:
                self.log_test("Create Album", False, "No project_id available")
                return False
            
            album_data = {
                "project_id": project_id,
                "name": "Test Album for Catalogue",
                "description": "Album created for comprehensive testing"
            }
            
            response = self.session.post(
                f"{API_BASE}/albums",
                json=album_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "album" in data and "id" in data["album"]:
                    album_id = data["album"]["id"]
                    self.test_data["album_id"] = album_id
                    self.created_items.append(("album", album_id))
                    self.log_test("Create Album", True, f"Created album: {album_id}")
                    return True
                else:
                    self.log_test("Create Album", False, "Invalid response format", data)
            else:
                self.log_test("Create Album", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Create Album", False, f"Error: {str(e)}")
        return False
    
    # ========== CATALOGUE CHUNKED UPLOAD ==========
    def test_catalogue_upload_init(self):
        """Test POST /api/uploads/catalogue/init"""
        try:
            project_id = self.test_data.get("project_id")
            album_id = self.test_data.get("album_id")
            
            init_data = {
                "filename": "test_catalogue_file.pdf",
                "file_size": 2097152,  # 2MB
                "chunk_size": 1048576,  # 1MB chunks
                "total_chunks": 2,
                "category": "document",
                "tags": "test,catalogue,comprehensive",
                "project_id": project_id,
                "album_id": album_id
            }
            
            response = self.session.post(
                f"{API_BASE}/uploads/catalogue/init",
                json=init_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "upload_id" in data:
                    upload_id = data["upload_id"]
                    self.test_data["upload_id"] = upload_id
                    self.log_test("Catalogue Upload Init", True, f"Initialized upload: {upload_id}")
                    return True
                else:
                    self.log_test("Catalogue Upload Init", False, "Invalid response format", data)
            else:
                self.log_test("Catalogue Upload Init", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Catalogue Upload Init", False, f"Error: {str(e)}")
        return False
    
    def test_catalogue_upload_chunks(self):
        """Test POST /api/uploads/catalogue/chunk (upload 2 chunks)"""
        try:
            upload_id = self.test_data.get("upload_id")
            if not upload_id:
                self.log_test("Catalogue Upload Chunks", False, "No upload_id available")
                return False
            
            # Upload chunk 0
            chunk_0_content = self.create_test_file_content(1)  # 1MB
            files = {'chunk': ('chunk_0', io.BytesIO(chunk_0_content), 'application/octet-stream')}
            data = {'upload_id': upload_id, 'index': 0, 'total': 2}
            
            response = self.session.post(
                f"{API_BASE}/uploads/catalogue/chunk",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_test("Catalogue Upload Chunks", False, 
                            f"Chunk 0 failed: HTTP {response.status_code}", response.text)
                return False
            
            # Upload chunk 1
            chunk_1_content = self.create_test_file_content(1)  # 1MB
            files = {'chunk': ('chunk_1', io.BytesIO(chunk_1_content), 'application/octet-stream')}
            data = {'upload_id': upload_id, 'index': 1, 'total': 2}
            
            response = self.session.post(
                f"{API_BASE}/uploads/catalogue/chunk",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                self.log_test("Catalogue Upload Chunks", True, "Uploaded 2 chunks successfully")
                return True
            else:
                self.log_test("Catalogue Upload Chunks", False, 
                            f"Chunk 1 failed: HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Catalogue Upload Chunks", False, f"Error: {str(e)}")
        return False
    
    def test_catalogue_upload_state(self):
        """Test GET /api/uploads/catalogue/state"""
        try:
            upload_id = self.test_data.get("upload_id")
            if not upload_id:
                self.log_test("Catalogue Upload State", False, "No upload_id available")
                return False
            
            response = self.session.get(
                f"{API_BASE}/uploads/catalogue/state?upload_id={upload_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("exists") and 
                    data.get("parts") == 2 and 
                    data.get("status") == "uploading"):
                    self.log_test("Catalogue Upload State", True, 
                                f"State correct: {data['parts']} parts, status: {data['status']}")
                    return True
                else:
                    self.log_test("Catalogue Upload State", False, "Invalid state", data)
            else:
                self.log_test("Catalogue Upload State", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Catalogue Upload State", False, f"Error: {str(e)}")
        return False
    
    def test_catalogue_upload_complete(self):
        """Test POST /api/uploads/catalogue/complete"""
        try:
            upload_id = self.test_data.get("upload_id")
            project_id = self.test_data.get("project_id")
            album_id = self.test_data.get("album_id")
            
            if not upload_id:
                self.log_test("Catalogue Upload Complete", False, "No upload_id available")
                return False
            
            complete_data = {
                "upload_id": upload_id,
                "filename": "test_catalogue_file.pdf",
                "category": "document",
                "tags": "test,catalogue,comprehensive",
                "project_id": project_id,
                "album_id": album_id,
                "title": "Test Catalogue File",
                "description": "File uploaded for comprehensive testing"
            }
            
            response = self.session.post(
                f"{API_BASE}/uploads/catalogue/complete",
                json=complete_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and 
                    "file" in data and 
                    "url" in data["file"]):
                    
                    file_info = data["file"]
                    file_url = file_info["url"]
                    
                    # Verify URL uses /api/files/catalogue/* pattern
                    if "/api/files/catalogue/" in file_url:
                        self.test_data["catalogue_file_url"] = file_url
                        self.test_data["catalogue_file_id"] = file_info.get("id")
                        self.log_test("Catalogue Upload Complete", True, 
                                    f"File completed, URL: {file_url}")
                        return True
                    else:
                        self.log_test("Catalogue Upload Complete", False, 
                                    f"URL not using /api/files/catalogue/* pattern: {file_url}", data)
                else:
                    self.log_test("Catalogue Upload Complete", False, "Invalid response format", data)
            else:
                self.log_test("Catalogue Upload Complete", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Catalogue Upload Complete", False, f"Error: {str(e)}")
        return False
    
    def test_catalogue_list(self):
        """Test GET /api/uploads/catalogue/list with project_id and album_id"""
        try:
            project_id = self.test_data.get("project_id")
            album_id = self.test_data.get("album_id")
            
            url = f"{API_BASE}/uploads/catalogue/list"
            params = []
            if project_id:
                params.append(f"project_id={project_id}")
            if album_id:
                params.append(f"album_id={album_id}")
            
            if params:
                url += "?" + "&".join(params)
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "catalogues" in data and isinstance(data["catalogues"], list):
                    catalogues = data["catalogues"]
                    
                    # Verify our uploaded file is in the list
                    our_file = None
                    for cat in catalogues:
                        if cat.get("id") == self.test_data.get("catalogue_file_id"):
                            our_file = cat
                            break
                    
                    if our_file and "/api/files/catalogue/" in our_file.get("url", ""):
                        self.log_test("Catalogue List", True, 
                                    f"Found {len(catalogues)} catalogues, our file accessible via /api/files/*")
                        return True
                    else:
                        self.log_test("Catalogue List", False, 
                                    f"Our file not found or URL incorrect in {len(catalogues)} catalogues", data)
                else:
                    self.log_test("Catalogue List", False, "Invalid response format", data)
            else:
                self.log_test("Catalogue List", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Catalogue List", False, f"Error: {str(e)}")
        return False
    
    def test_catalogue_file_download(self):
        """Test direct file access via /api/files/catalogue/*"""
        try:
            file_url = self.test_data.get("catalogue_file_url")
            if not file_url:
                self.log_test("Catalogue File Download", False, "No file URL available")
                return False
            
            response = self.session.get(file_url, timeout=30)
            
            if response.status_code == 200:
                content_length = len(response.content)
                if content_length > 0:
                    self.log_test("Catalogue File Download", True, 
                                f"File downloadable via /api/files/*, size: {content_length} bytes")
                    return True
                else:
                    self.log_test("Catalogue File Download", False, "File is empty")
            else:
                self.log_test("Catalogue File Download", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Catalogue File Download", False, f"Error: {str(e)}")
        return False
    
    # ========== TRAINING PDF UPLOAD ==========
    def test_training_upload(self):
        """Test POST /api/training/upload with PDF"""
        try:
            # Create test PDF content
            pdf_content = self.create_test_file_content(1)  # 1MB test PDF
            
            files = {
                'file': ('test_training.pdf', io.BytesIO(pdf_content), 'application/pdf')
            }
            data = {
                'title': 'Comprehensive Test Training Module',
                'feature': 'testing'
            }
            
            response = self.session.post(
                f"{API_BASE}/training/upload",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if ("module" in result and 
                    "url" in result["module"] and
                    "/api/files/training/" in result["module"]["url"]):
                    
                    module = result["module"]
                    self.test_data["training_module_id"] = module.get("id")
                    self.test_data["training_file_url"] = module["url"]
                    
                    self.log_test("Training Upload", True, 
                                f"PDF uploaded, URL: {module['url']}")
                    return True
                else:
                    self.log_test("Training Upload", False, "Invalid response or URL format", result)
            else:
                self.log_test("Training Upload", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Training Upload", False, f"Error: {str(e)}")
        return False
    
    def test_training_list_by_feature(self):
        """Test GET /api/training/modules with feature filter"""
        try:
            response = self.session.get(f"{API_BASE}/training/modules?feature=testing", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data and isinstance(data["items"], list):
                    items = data["items"]
                    
                    # Find our uploaded module
                    our_module = None
                    for item in items:
                        if item.get("id") == self.test_data.get("training_module_id"):
                            our_module = item
                            break
                    
                    if our_module and "/api/files/training/" in our_module.get("url", ""):
                        self.log_test("Training List by Feature", True, 
                                    f"Found {len(items)} training modules, our module accessible via /api/files/*")
                        return True
                    else:
                        self.log_test("Training List by Feature", False, 
                                    f"Our module not found or URL incorrect in {len(items)} modules", data)
                else:
                    self.log_test("Training List by Feature", False, "Invalid response format", data)
            else:
                self.log_test("Training List by Feature", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Training List by Feature", False, f"Error: {str(e)}")
        return False
    
    def test_training_file_download(self):
        """Test direct file access via /api/files/training/*"""
        try:
            file_url = self.test_data.get("training_file_url")
            if not file_url:
                self.log_test("Training File Download", False, "No training file URL available")
                return False
            
            response = self.session.get(file_url, timeout=30)
            
            if response.status_code == 200:
                content_length = len(response.content)
                if content_length > 0:
                    self.log_test("Training File Download", True, 
                                f"Training PDF downloadable via /api/files/*, size: {content_length} bytes")
                    return True
                else:
                    self.log_test("Training File Download", False, "Training file is empty")
            else:
                self.log_test("Training File Download", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Training File Download", False, f"Error: {str(e)}")
        return False
    
    # ========== WHATSAPP INTEGRATION ==========
    def test_whatsapp_webhook(self):
        """Test POST /api/whatsapp/webhook with demo payload"""
        try:
            demo_payload = {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "from": "919876543210",
                                "text": {"body": "Hello from comprehensive test 👋"},
                                "timestamp": str(int(time.time())),
                                "type": "text"
                            }]
                        }
                    }]
                }]
            }
            
            response = self.session.post(
                f"{API_BASE}/whatsapp/webhook",
                json=demo_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.test_data["whatsapp_contact"] = "919876543210"
                    self.log_test("WhatsApp Webhook", True, "Webhook processed demo payload successfully")
                    return True
                else:
                    self.log_test("WhatsApp Webhook", False, "Webhook did not return success", data)
            else:
                self.log_test("WhatsApp Webhook", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("WhatsApp Webhook", False, f"Error: {str(e)}")
        return False
    
    def test_whatsapp_conversations(self):
        """Test GET /api/whatsapp/conversations"""
        try:
            response = self.session.get(f"{API_BASE}/whatsapp/conversations", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    conversations = data
                    
                    # Verify required fields
                    valid_conversations = []
                    for conv in conversations:
                        if ("age_sec" in conv and 
                            "unread_count" in conv and
                            "contact" in conv):
                            valid_conversations.append(conv)
                    
                    if valid_conversations:
                        self.log_test("WhatsApp Conversations", True, 
                                    f"Retrieved {len(valid_conversations)} conversations with age_sec and unread_count")
                        return True
                    else:
                        self.log_test("WhatsApp Conversations", False, 
                                    f"No valid conversations found in {len(conversations)} items", data)
                else:
                    self.log_test("WhatsApp Conversations", False, "Response is not a list", data)
            else:
                self.log_test("WhatsApp Conversations", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("WhatsApp Conversations", False, f"Error: {str(e)}")
        return False
    
    def test_whatsapp_send(self):
        """Test POST /api/whatsapp/send"""
        try:
            contact = self.test_data.get("whatsapp_contact", "919876543210")
            
            send_payload = {
                "to": contact,
                "text": "Test message from comprehensive backend testing"
            }
            
            response = self.session.post(
                f"{API_BASE}/whatsapp/send",
                json=send_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("WhatsApp Send", True, "Message sent successfully")
                    return True
                else:
                    self.log_test("WhatsApp Send", False, "Send did not return success", data)
            else:
                self.log_test("WhatsApp Send", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("WhatsApp Send", False, f"Error: {str(e)}")
        return False
    
    def test_whatsapp_send_media(self):
        """Test POST /api/whatsapp/send_media"""
        try:
            contact = self.test_data.get("whatsapp_contact", "919876543210")
            
            media_payload = {
                "to": contact,
                "media_url": "https://example.com/test_image.jpg",
                "media_type": "image"
            }
            
            response = self.session.post(
                f"{API_BASE}/whatsapp/send_media",
                json=media_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("WhatsApp Send Media", True, "Media message sent successfully")
                    return True
                else:
                    self.log_test("WhatsApp Send Media", False, "Send media did not return success", data)
            else:
                self.log_test("WhatsApp Send Media", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("WhatsApp Send Media", False, f"Error: {str(e)}")
        return False
    
    def test_whatsapp_link_lead(self):
        """Test POST /api/whatsapp/conversations/{contact}/link_lead"""
        try:
            contact = self.test_data.get("whatsapp_contact", "919876543210")
            
            # First create a lead to link to
            lead_data = {"name": "WhatsApp Test Lead", "phone": contact}
            lead_response = self.session.post(f"{API_BASE}/leads", json=lead_data, timeout=10)
            
            if lead_response.status_code != 200:
                self.log_test("WhatsApp Link Lead", False, "Failed to create test lead")
                return False
            
            lead_id = lead_response.json()["lead"]["id"]
            
            # Now link the conversation to the lead
            link_payload = {"lead_id": lead_id}
            
            response = self.session.post(
                f"{API_BASE}/whatsapp/conversations/{contact}/link_lead",
                json=link_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "link" in data:
                    self.log_test("WhatsApp Link Lead", True, 
                                f"Conversation linked to lead: {lead_id}")
                    return True
                else:
                    self.log_test("WhatsApp Link Lead", False, "Link did not return success", data)
            else:
                self.log_test("WhatsApp Link Lead", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("WhatsApp Link Lead", False, f"Error: {str(e)}")
        return False
    
    def test_whatsapp_contact_messages(self):
        """Test GET /api/whatsapp/contact_messages"""
        try:
            contact = self.test_data.get("whatsapp_contact", "919876543210")
            
            response = self.session.get(
                f"{API_BASE}/whatsapp/contact_messages?contact={contact}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data and isinstance(data["items"], list):
                    messages = data["items"]
                    self.log_test("WhatsApp Contact Messages", True, 
                                f"Retrieved {len(messages)} messages for contact")
                    return True
                else:
                    self.log_test("WhatsApp Contact Messages", False, "Invalid response format", data)
            else:
                self.log_test("WhatsApp Contact Messages", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("WhatsApp Contact Messages", False, f"Error: {str(e)}")
        return False
    
    # ========== LEADS CRUD ==========
    def test_leads_crud(self):
        """Test complete Leads CRUD operations"""
        try:
            # CREATE
            lead_data = {
                "name": "Comprehensive Test Lead",
                "email": "test@comprehensive.com",
                "phone": "9876543210",  # Will be normalized to +919876543210
                "source": "comprehensive_test",
                "notes": "Created during comprehensive backend testing"
            }
            
            create_response = self.session.post(f"{API_BASE}/leads", json=lead_data, timeout=10)
            if create_response.status_code != 200:
                self.log_test("Leads CRUD", False, f"CREATE failed: {create_response.status_code}")
                return False
            
            lead = create_response.json()["lead"]
            lead_id = lead["id"]
            self.created_items.append(("lead", lead_id))
            
            # Verify phone normalization
            if lead.get("phone") != "+919876543210":
                self.log_test("Leads CRUD", False, f"Phone not normalized: {lead.get('phone')}")
                return False
            
            # READ
            read_response = self.session.get(f"{API_BASE}/leads/{lead_id}", timeout=10)
            if read_response.status_code != 200:
                self.log_test("Leads CRUD", False, f"READ failed: {read_response.status_code}")
                return False
            
            # UPDATE
            update_data = {"status": "Qualified", "notes": "Updated during comprehensive test"}
            update_response = self.session.put(f"{API_BASE}/leads/{lead_id}", json=update_data, timeout=10)
            if update_response.status_code != 200:
                self.log_test("Leads CRUD", False, f"UPDATE failed: {update_response.status_code}")
                return False
            
            updated_lead = update_response.json()["lead"]
            if updated_lead.get("status") != "Qualified":
                self.log_test("Leads CRUD", False, "UPDATE did not change status")
                return False
            
            # LIST
            list_response = self.session.get(f"{API_BASE}/leads?limit=10", timeout=10)
            if list_response.status_code != 200:
                self.log_test("Leads CRUD", False, f"LIST failed: {list_response.status_code}")
                return False
            
            list_data = list_response.json()
            if not ("items" in list_data and "total" in list_data):
                self.log_test("Leads CRUD", False, "LIST response missing pagination fields")
                return False
            
            # Verify no _id fields
            has_mongo_id = any("_id" in item for item in list_data["items"] if isinstance(item, dict))
            if has_mongo_id:
                self.log_test("Leads CRUD", False, "LIST response contains _id fields")
                return False
            
            self.log_test("Leads CRUD", True, "All CRUD operations successful with proper validation")
            return True
            
        except Exception as e:
            self.log_test("Leads CRUD", False, f"Error: {str(e)}")
        return False
    
    def test_leads_search(self):
        """Test GET /api/leads/search with phone matching"""
        try:
            # Search by phone (last 10 digits)
            response = self.session.get(f"{API_BASE}/leads/search?q=9876543210", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if ("items" in data and 
                    "total" in data and 
                    isinstance(data["items"], list)):
                    
                    # Verify no _id fields
                    has_mongo_id = any("_id" in item for item in data["items"] if isinstance(item, dict))
                    if not has_mongo_id:
                        self.log_test("Leads Search", True, 
                                    f"Search returned {len(data['items'])} results without _id fields")
                        return True
                    else:
                        self.log_test("Leads Search", False, "Search results contain _id fields")
                else:
                    self.log_test("Leads Search", False, "Invalid search response format", data)
            else:
                self.log_test("Leads Search", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Leads Search", False, f"Error: {str(e)}")
        return False
    
    # ========== AI CHAT ENDPOINTS ==========
    def test_ai_specialized_chat(self):
        """Test POST /api/ai/specialized-chat"""
        try:
            chat_payload = {
                "message": "Test message for specialized chat",
                "session_id": str(uuid.uuid4()),
                "language": "en",
                "context": {"test": "comprehensive"}
            }
            
            response = self.session.post(
                f"{API_BASE}/ai/specialized-chat",
                json=chat_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["message_id", "message", "timestamp", "actions", "metadata"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("AI Specialized Chat", True, 
                                f"Chat response valid with message: {data.get('message', '')[:50]}...")
                    return True
                else:
                    self.log_test("AI Specialized Chat", False, 
                                f"Missing fields: {missing_fields}", data)
            else:
                self.log_test("AI Specialized Chat", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("AI Specialized Chat", False, f"Error: {str(e)}")
        return False
    
    def test_aavana2_enhanced_chat(self):
        """Test POST /api/aavana2/enhanced-chat"""
        try:
            chat_payload = {
                "message": "Test message for enhanced chat",
                "session_id": str(uuid.uuid4())
            }
            
            response = self.session.post(
                f"{API_BASE}/aavana2/enhanced-chat",
                json=chat_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Aavana2 Enhanced Chat", True, 
                                f"Enhanced chat response: {data.get('message', '')[:50]}...")
                    return True
                else:
                    self.log_test("Aavana2 Enhanced Chat", False, "No message in response", data)
            else:
                self.log_test("Aavana2 Enhanced Chat", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Aavana2 Enhanced Chat", False, f"Error: {str(e)}")
        return False
    
    def test_aavana2_chat(self):
        """Test POST /api/aavana2/chat"""
        try:
            chat_payload = {
                "message": "Test message for standard chat",
                "provider": "openai",
                "model": "gpt-4o"
            }
            
            response = self.session.post(
                f"{API_BASE}/aavana2/chat",
                json=chat_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Aavana2 Chat", True, 
                                f"Standard chat response: {data.get('message', '')[:50]}...")
                    return True
                else:
                    self.log_test("Aavana2 Chat", False, "No message in response", data)
            else:
                self.log_test("Aavana2 Chat", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Aavana2 Chat", False, f"Error: {str(e)}")
        return False
    
    # ========== HRMS ENDPOINTS ==========
    def test_hrms_endpoints(self):
        """Test HRMS today/checkin/checkout/summary"""
        try:
            # Test today
            today_response = self.session.get(f"{API_BASE}/hrms/today", timeout=10)
            if today_response.status_code != 200:
                self.log_test("HRMS Endpoints", False, f"TODAY failed: {today_response.status_code}")
                return False
            
            # Test checkin
            checkin_response = self.session.post(f"{API_BASE}/hrms/checkin", timeout=10)
            if checkin_response.status_code != 200:
                self.log_test("HRMS Endpoints", False, f"CHECKIN failed: {checkin_response.status_code}")
                return False
            
            # Test checkout
            checkout_response = self.session.post(f"{API_BASE}/hrms/checkout", timeout=10)
            if checkout_response.status_code != 200:
                self.log_test("HRMS Endpoints", False, f"CHECKOUT failed: {checkout_response.status_code}")
                return False
            
            # Test summary
            summary_response = self.session.get(f"{API_BASE}/hrms/summary?days=7", timeout=10)
            if summary_response.status_code != 200:
                self.log_test("HRMS Endpoints", False, f"SUMMARY failed: {summary_response.status_code}")
                return False
            
            summary_data = summary_response.json()
            if "items" in summary_data and isinstance(summary_data["items"], list):
                self.log_test("HRMS Endpoints", True, 
                            f"All HRMS endpoints working, summary has {len(summary_data['items'])} days")
                return True
            else:
                self.log_test("HRMS Endpoints", False, "SUMMARY invalid format", summary_data)
                
        except Exception as e:
            self.log_test("HRMS Endpoints", False, f"Error: {str(e)}")
        return False
    
    # ========== ADMIN ENDPOINTS ==========
    def test_admin_endpoints(self):
        """Test Admin settings GET/PUT and roles"""
        try:
            # Test GET settings
            get_response = self.session.get(f"{API_BASE}/admin/settings", timeout=10)
            if get_response.status_code != 200:
                self.log_test("Admin Endpoints", False, f"GET settings failed: {get_response.status_code}")
                return False
            
            original_settings = get_response.json()
            
            # Test PUT settings
            update_settings = {"sla_minutes": 600, "test_setting": "comprehensive_test"}
            put_response = self.session.put(f"{API_BASE}/admin/settings", json=update_settings, timeout=10)
            if put_response.status_code != 200:
                self.log_test("Admin Endpoints", False, f"PUT settings failed: {put_response.status_code}")
                return False
            
            # Test roles
            roles_response = self.session.get(f"{API_BASE}/admin/roles", timeout=10)
            if roles_response.status_code != 200:
                self.log_test("Admin Endpoints", False, f"GET roles failed: {roles_response.status_code}")
                return False
            
            roles_data = roles_response.json()
            if "items" in roles_data and isinstance(roles_data["items"], list):
                self.log_test("Admin Endpoints", True, 
                            f"Admin endpoints working, {len(roles_data['items'])} roles available")
                return True
            else:
                self.log_test("Admin Endpoints", False, "Roles invalid format", roles_data)
                
        except Exception as e:
            self.log_test("Admin Endpoints", False, f"Error: {str(e)}")
        return False
    
    # ========== MAIN TEST RUNNER ==========
    def run_all_tests(self):
        """Run comprehensive backend test suite"""
        print("🚀 Starting CRM Backend Comprehensive QA Test Suite")
        print("=" * 70)
        print(f"🎯 Testing backend at: {BASE_URL}")
        print("🔍 Focus: File access via /api/files/* for Training and Catalogue downloads")
        print("=" * 70)
        
        # Test 1: Backend Connectivity Check
        print("\n1️⃣ Testing Backend Connectivity...")
        if not self.test_backend_connectivity():
            print("❌ Backend connectivity failed - aborting tests")
            return False
        
        # Test 2: Visual Upgrades
        print("\n2️⃣ Testing Visual Upgrades...")
        self.test_visual_upgrades_render()
        self.test_visual_upgrades_list()
        
        # Test 3: Projects & Albums Setup
        print("\n3️⃣ Testing Projects & Albums...")
        self.test_create_project()
        self.test_create_album()
        
        # Test 4: Catalogue Chunked Upload (MAIN FOCUS)
        print("\n4️⃣ Testing Catalogue Chunked Upload with /api/files/* access...")
        self.test_catalogue_upload_init()
        self.test_catalogue_upload_chunks()
        self.test_catalogue_upload_state()
        self.test_catalogue_upload_complete()
        self.test_catalogue_list()
        self.test_catalogue_file_download()  # KEY TEST: /api/files/catalogue/*
        
        # Test 5: Training PDF Upload (MAIN FOCUS)
        print("\n5️⃣ Testing Training PDF Upload with /api/files/* access...")
        self.test_training_upload()
        self.test_training_list_by_feature()
        self.test_training_file_download()  # KEY TEST: /api/files/training/*
        
        # Test 6: WhatsApp Integration
        print("\n6️⃣ Testing WhatsApp Integration...")
        self.test_whatsapp_webhook()
        self.test_whatsapp_conversations()
        self.test_whatsapp_send()
        self.test_whatsapp_send_media()
        self.test_whatsapp_link_lead()
        self.test_whatsapp_contact_messages()
        
        # Test 7: Leads CRUD and Search
        print("\n7️⃣ Testing Leads CRUD and Search...")
        self.test_leads_crud()
        self.test_leads_search()
        
        # Test 8: AI Chat Endpoints
        print("\n8️⃣ Testing AI Chat Endpoints...")
        self.test_ai_specialized_chat()
        self.test_aavana2_enhanced_chat()
        self.test_aavana2_chat()
        
        # Test 9: HRMS Endpoints
        print("\n9️⃣ Testing HRMS Endpoints...")
        self.test_hrms_endpoints()
        
        # Test 10: Admin Endpoints
        print("\n🔟 Testing Admin Endpoints...")
        self.test_admin_endpoints()
        
        # Summary
        self.print_summary()
        
        return self.get_overall_success()
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("📊 CRM BACKEND COMPREHENSIVE QA SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show failed tests with details
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
                if test.get('response_data'):
                    print(f"    Response: {json.dumps(test['response_data'], indent=4)}")
        
        # Show key file access results
        file_access_tests = [
            "Catalogue File Download",
            "Training File Download"
        ]
        
        print("\n🔍 KEY FILE ACCESS RESULTS (/api/files/*):")
        for test_name in file_access_tests:
            test_result = next((r for r in self.test_results if r["test"] == test_name), None)
            if test_result:
                status = "✅ PASS" if test_result["success"] else "❌ FAIL"
                print(f"  {status} {test_name}: {test_result['details']}")
        
        # Show created items
        if self.created_items:
            print(f"\n📝 Created {len(self.created_items)} test items in database")
        
        print(f"\n🎯 Backend URL tested: {BASE_URL}")
    
    def get_overall_success(self):
        """Get overall test success status"""
        if not self.test_results:
            return False
        
        # Critical tests that must pass
        critical_tests = [
            "Backend Connectivity",
            "Catalogue Upload Complete",
            "Catalogue File Download",  # KEY: /api/files/catalogue/*
            "Training Upload", 
            "Training File Download",   # KEY: /api/files/training/*
            "Leads CRUD",
            "WhatsApp Webhook"
        ]
        
        critical_passed = all(
            any(result["test"] == test and result["success"] for result in self.test_results)
            for test in critical_tests
        )
        
        return critical_passed

def main():
    """Main test execution"""
    tester = CRMComprehensiveTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ CRM Backend comprehensive QA completed successfully!")
        print("🔍 File access via /api/files/* verified for Training and Catalogue downloads")
        exit(0)
    else:
        print("\n❌ CRM Backend comprehensive QA had critical failures!")
        print("🔍 Check file access via /api/files/* and other critical endpoints")
        exit(1)

if __name__ == "__main__":
    main()