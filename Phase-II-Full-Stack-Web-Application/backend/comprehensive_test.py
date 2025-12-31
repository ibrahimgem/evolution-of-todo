#!/usr/bin/env python3
"""
Comprehensive test script for the Todo API
Run this script after starting the backend server
"""
import asyncio
import httpx
import json
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"

async def test_endpoint(endpoint, method="GET", data=None, headers=None, expected_status=200):
    """Test a single endpoint and return results"""
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

            is_json = response.headers.get("content-type", "").startswith("application/json")
            result = {
                "status": response.status_code,
                "text": response.text,
                "json": response.json() if is_json else None,
                "headers": dict(response.headers),
                "expected": expected_status,
                "success": response.status_code == expected_status
            }

            return result

        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "expected": expected_status
            }

async def run_tests():
    """Run all tests and return results"""
    results = []

    print("🧪 Running comprehensive Todo API tests...")
    print("=" * 60)

    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    result = await test_endpoint("/", "GET", expected_status=200)
    results.append(("Root endpoint", result))
    print(f"   Status: {result['status']} {'✓' if result['success'] else '✗'}")
    if result.get('json'):
        print(f"   Response: {result['json']}")

    # Test 2: User registration
    print("\n2. Testing user registration...")
    user_data = {
        "email": f"test_{int(datetime.now().timestamp())}@example.com",
        "name": "Test User",
        "password": "testpassword123"
    }
    result = await test_endpoint("/auth/register", "POST", user_data, expected_status=200)
    results.append(("User registration", result))
    print(f"   Status: {result['status']} {'✓' if result['success'] else '✗'}")

    # Store user data for login
    test_user = user_data

    # Test 3: User login
    print("\n3. Testing user login...")
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    result = await test_endpoint("/auth/login", "POST", login_data, expected_status=200)
    results.append(("User login", result))
    print(f"   Status: {result['status']} {'✓' if result['success'] else '✗'}")

    token = None
    if result['success'] and result.get('json'):
        auth_response = result['json']
        token = auth_response.get("access_token")
        print(f"   Token: {token[:20]}..." if token else "No token received")

    # Test 4: Tasks API without auth (should fail)
    print("\n4. Testing tasks API without auth (should fail)...")
    result = await test_endpoint("/api/1/tasks", "GET", expected_status=401)
    results.append(("Tasks without auth", result))
    print(f"   Status: {result['status']} {'✓' if result['success'] else '✗'} (expected 401)")

    # Test 5: Tasks API with auth
    if token:
        print("\n5. Testing tasks API with auth...")
        headers = {"Authorization": f"Bearer {token}"}
        result = await test_endpoint("/api/1/tasks", "GET", headers=headers, expected_status=200)
        results.append(("Tasks with auth", result))
        print(f"   Status: {result['status']} {'✓' if result['success'] else '✗'}")

        # Test 6: Create a task
        print("\n6. Testing task creation...")
        task_data = {
            "title": "Test task from API",
            "description": "This is a test task created via API",
            "completed": False
        }
        result = await test_endpoint("/api/1/tasks", "POST", task_data, headers=headers, expected_status=200)
        results.append(("Create task", result))
        print(f"   Status: {result['status']} {'✓' if result['success'] else '✗'}")

        # Test 7: Get tasks again
        print("\n7. Testing get tasks after creation...")
        result = await test_endpoint("/api/1/tasks", "GET", headers=headers, expected_status=200)
        results.append(("Get tasks after creation", result))
        print(f"   Status: {result['status']} {'✓' if result['success'] else '✗'}")

        if result['success'] and result.get('json'):
            tasks = result['json']
            print(f"   Tasks count: {len(tasks)}")
            if tasks:
                print(f"   First task: {tasks[0]}")

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result['success'])
    total = len(results)

    for test_name, result in results:
        status_icon = "✓" if result['success'] else "✗"
        expected = result.get('expected', 'N/A')
        actual = result.get('status', 'N/A')
        print(f"{status_icon} {test_name}: Expected {expected}, Got {actual}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the details above.")

    # CORS Check
    print("\n🌐 CORS HEADER CHECK")
    print("-" * 30)
    if results:
        sample_result = results[0][1]  # Get first result
        if 'headers' in sample_result:
            headers = sample_result['headers']
            cors_headers = {k: v for k, v in headers.items() if 'cors' in k.lower() or 'origin' in k.lower()}
            if cors_headers:
                print("CORS headers found:")
                for k, v in cors_headers.items():
                    print(f"  {k}: {v}")
            else:
                print("No specific CORS headers found in response")

    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(run_tests())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test script failed: {e}")
        exit(1)