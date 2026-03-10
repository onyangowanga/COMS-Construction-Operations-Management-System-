#!/usr/bin/env python
"""
Test JWT Authentication endpoints
"""
import json
import requests

BASE_URL = "http://localhost:8000"

def test_login():
    """Test login endpoint"""
    print("=" * 60)
    print("TEST 1: Login with email and password")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/auth/login/"
    data = {
        "email": "admin@test.com",
        "password": "TestPass123!"
    }
    
    response = requests.post(url, json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Check cookies
    print("\nCookies received:")
    for cookie in response.cookies:
        print(f"  - {cookie.name}: {cookie.value[:50]}...")
        print(f"    httponly: {cookie.has_nonstandard_attr('HttpOnly')}")
        print(f"    secure: {cookie.secure}")
        print(f"    samesite: {cookie.get_nonstandard_attr('SameSite', 'Not set')}")
        print(f"    path: {cookie.path}")
        print(f"    max-age: {cookie.get_nonstandard_attr('Max-Age', 'Not set')}")
    
    return response.cookies


def test_get_profile(cookies):
    """Test authenticated endpoint"""
    print("\n" + "=" * 60)
    print("TEST 2: Get user profile (authenticated with cookies)")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/auth/me/"
    
    response = requests.get(url, cookies=cookies)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def test_refresh_token(cookies):
    """Test token refresh"""
    print("\n" + "=" * 60)
    print("TEST 3: Refresh access token")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/auth/token/refresh/"
    
    response = requests.post(url, cookies=cookies)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Check for new cookies
    if response.cookies:
        print("\nNew cookies received:")
        for cookie in response.cookies:
            print(f"  - {cookie.name}: {cookie.value[:50]}...")
    
    return response.cookies if response.cookies else cookies


def test_logout(cookies):
    """Test logout"""
    print("\n" + "=" * 60)
    print("TEST 4: Logout (blacklist token and clear cookies)")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/auth/logout/"
    
    response = requests.post(url, cookies=cookies)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Check if cookies are cleared
    print("\nCookies after logout:")
    for cookie in response.cookies:
        print(f"  - {cookie.name}: {cookie.value if cookie.value else '(empty)'}")
    

def test_access_after_logout(cookies):
    """Test that access is denied after logout"""
    print("\n" + "=" * 60)
    print("TEST 5: Try to access profile after logout")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/auth/me/"
    
    response = requests.get(url, cookies=cookies)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")


if __name__ == "__main__":
    print("\n🔐 JWT COOKIE-BASED AUTHENTICATION TESTS\n")
    
    try:
        # Test 1: Login
        cookies = test_login()
        
        # Test 2: Get profile (authenticated)
        test_get_profile(cookies)
        
        # Test 3: Refresh token
        new_cookies = test_refresh_token(cookies)
        
        # Test 4: Logout
        test_logout(new_cookies)
        
        # Test 5: Access after logout should fail
        test_access_after_logout(new_cookies)
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server at http://localhost:8000")
        print("Make sure Docker containers are running: docker-compose up")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
