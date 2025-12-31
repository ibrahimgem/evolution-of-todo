#!/usr/bin/env python3
"""
Simple test script for the Todo API
"""
import asyncio
import httpx
import sys

BASE_URL = "http://localhost:8000"

async def test_endpoint(endpoint, method="GET", data=None, headers=None):
    """Test a single endpoint"""
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(f"{BASE_URL}{endpoint}", headers=headers)
            elif method == "POST":
                response = await client.post(f"{BASE_URL}{endpoint}", json=data, headers=headers)
            elif method == "PUT":
                response = await client.put(f"{BASE_URL}{endpoint}", json=data, headers=headers)
            elif method == "DELETE":
                response = await client.delete(f"{BASE_URL}{endpoint}", headers=headers)

            return {
                "status": response.status_code,
                "text": response.text,
                "json": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
            }
        except Exception as e:
            return {"error": str(e)}

async def main():
    print("Testing Todo API...")

    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    result = await test_endpoint("/")
    print(f"Status: {result['status']}")
    if 'json' in result and result['json']:
        print(f"Response: {result['json']}")
    else:
        print(f"Response: {result.get('text', 'No response')}")

    # Test 2: Register a user
    print("\n2. Testing user registration...")
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword123"
    }
    result = await test_endpoint("/auth/register", "POST", user_data)
    print(f"Status: {result['status']}")
    if result['status'] in [200, 201]:
        print(f"Registration successful")
    else:
        print(f"Registration failed: {result.get('text', 'Unknown error')}")

    # Test 3: Login
    print("\n3. Testing user login...")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    result = await test_endpoint("/auth/login", "POST", login_data)
    print(f"Status: {result['status']}")

    if result['status'] == 200 and result.get('json'):
        auth_response = result['json']
        token = auth_response.get("access_token")
        print(f"Login successful, got token: {token[:20]}...")
        return token
    else:
        print(f"Login failed: {result.get('text', 'Unknown error')}")
        return None

if __name__ == "__main__":
    try:
        token = asyncio.run(main())
        if token:
            print(f"\n✓ API is working! Got JWT token: {token[:20]}...")
        else:
            print("\n✗ API tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test script failed: {e}")
        sys.exit(1)