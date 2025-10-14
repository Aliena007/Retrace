#!/usr/bin/env python3
"""
Backend API Testing for Campus Lost & Found System
Tests Django REST API endpoints for lost/found items with AI analysis
"""

import requests
import sys
import json
import os
from datetime import datetime
from pathlib import Path

class CampusLostFoundAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def test_api_health(self):
        """Test if API is accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/ai/lost/", timeout=10)
            success = response.status_code in [200, 404]  # 404 is ok for empty list
            self.log_test("API Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("API Health Check", False, str(e))
            return False

    def test_lost_items_list(self):
        """Test GET /api/ai/lost/ endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/ai/lost/", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                self.log_test("Lost Items List", True, f"Found {len(data)} items")
            else:
                self.log_test("Lost Items List", False, f"Status: {response.status_code}")
            return success, response.json() if success else []
        except Exception as e:
            self.log_test("Lost Items List", False, str(e))
            return False, []

    def test_found_items_list(self):
        """Test GET /api/ai/found/ endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/ai/found/", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                self.log_test("Found Items List", True, f"Found {len(data)} items")
            else:
                self.log_test("Found Items List", False, f"Status: {response.status_code}")
            return success, response.json() if success else []
        except Exception as e:
            self.log_test("Found Items List", False, str(e))
            return False, []

    def test_create_lost_item(self):
        """Test POST /api/ai/lost/ endpoint"""
        test_data = {
            "name": "Test Lost Laptop",
            "description": "Black MacBook Pro 13 inch with stickers",
            "date_lost": "2024-01-15",
            "location_lost": "Library Study Room 3",
            "contact_info": "test@campus.edu"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/ai/lost/",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            success = response.status_code in [200, 201]
            if success:
                data = response.json()
                item_id = data.get('id')
                self.log_test("Create Lost Item", True, f"Created item ID: {item_id}")
                return success, item_id
            else:
                self.log_test("Create Lost Item", False, f"Status: {response.status_code}, Response: {response.text}")
                return False, None
        except Exception as e:
            self.log_test("Create Lost Item", False, str(e))
            return False, None

    def test_create_found_item(self):
        """Test POST /api/ai/found/ endpoint"""
        test_data = {
            "name": "Test Found Phone",
            "description": "iPhone 12 with blue case",
            "date_found": "2024-01-16",
            "location_found": "Cafeteria Table 5",
            "contact_info": "finder@campus.edu"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/ai/found/",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            success = response.status_code in [200, 201]
            if success:
                data = response.json()
                item_id = data.get('id')
                self.log_test("Create Found Item", True, f"Created item ID: {item_id}")
                return success, item_id
            else:
                self.log_test("Create Found Item", False, f"Status: {response.status_code}, Response: {response.text}")
                return False, None
        except Exception as e:
            self.log_test("Create Found Item", False, str(e))
            return False, None

    def test_create_lost_item_with_image(self):
        """Test POST /api/ai/lost/ with image upload"""
        # Create a simple test image file
        test_image_path = "/tmp/test_image.jpg"
        try:
            from PIL import Image
            import io
            
            # Create a simple test image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(test_image_path, 'JPEG')
            
            with open(test_image_path, 'rb') as img_file:
                files = {'image': ('test_image.jpg', img_file, 'image/jpeg')}
                data = {
                    "name": "Test Lost Item with Image",
                    "description": "Test item for image upload",
                    "date_lost": "2024-01-17",
                    "location_lost": "Test Location",
                    "contact_info": "test@example.com"
                }
                
                response = requests.post(
                    f"{self.base_url}/api/ai/lost/",
                    files=files,
                    data=data,
                    timeout=30  # Longer timeout for AI processing
                )
                
                success = response.status_code in [200, 201]
                if success:
                    result = response.json()
                    self.log_test("Create Lost Item with Image", True, f"Created with AI analysis")
                    return success, result.get('id')
                else:
                    self.log_test("Create Lost Item with Image", False, f"Status: {response.status_code}")
                    return False, None
                    
        except ImportError:
            self.log_test("Create Lost Item with Image", False, "PIL not available for image creation")
            return False, None
        except Exception as e:
            self.log_test("Create Lost Item with Image", False, str(e))
            return False, None
        finally:
            # Clean up test image
            if os.path.exists(test_image_path):
                os.remove(test_image_path)

    def test_matches_endpoint(self):
        """Test GET /api/ai/matches/ endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/ai/matches/", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                self.log_test("Match Results List", True, f"Found {len(data)} matches")
            else:
                self.log_test("Match Results List", False, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Match Results List", False, str(e))
            return False

    def test_notifications_endpoint(self):
        """Test GET /api/ai/notifications/ endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/ai/notifications/", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                self.log_test("Notifications List", True, f"Found {len(data)} notifications")
            else:
                self.log_test("Notifications List", False, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Notifications List", False, str(e))
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Campus Lost & Found API Tests")
        print("=" * 50)
        
        # Basic connectivity
        if not self.test_api_health():
            print("❌ API is not accessible. Stopping tests.")
            return False
        
        # Test list endpoints
        self.test_lost_items_list()
        self.test_found_items_list()
        self.test_matches_endpoint()
        self.test_notifications_endpoint()
        
        # Test item creation
        self.test_create_lost_item()
        self.test_create_found_item()
        
        # Test image upload with AI analysis
        self.test_create_lost_item_with_image()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = CampusLostFoundAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": tester.tests_run,
        "passed_tests": tester.tests_passed,
        "success_rate": (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0,
        "test_details": tester.test_results
    }
    
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())