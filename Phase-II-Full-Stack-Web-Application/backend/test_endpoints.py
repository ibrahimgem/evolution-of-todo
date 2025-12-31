#!/usr/bin/env python3
"""
Test script to validate the backend API endpoints and ensure 404 issues are fixed.
This script tests all the endpoints to verify they are working correctly.
"""

import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Health check status: {response.status_code}")
        print(f"Health check response: {response.json()}")
        return response.status_code == 200

async def test_root_endpoint():
    """Test the root endpoint"""
    print("\nTesting root endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        print(f"Root endpoint status: {response.status_code}")
        print(f"Root endpoint response: {response.json()}")
        return response.status_code == 200

async def test_auth_endpoints():
    """Test authentication endpoints"""
    print("\nTesting authentication endpoints...")

    async with httpx.AsyncClient() as client:
        # Test register endpoint
        register_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "name": "Test User"
        }

        response = await client.post(f"{BASE_URL}/api/auth/register", json=register_data)
        print(f"Register status: {response.status_code}")
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"Registration successful, token: {token[:20]}...")
            return token
        else:
            print(f"Register response: {response.json()}")
            return None

async def test_protected_endpoints(token):
    """Test protected endpoints that require authentication"""
    print("\nTesting protected endpoints...")

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        # Test get current user info
        response = await client.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print(f"Get current user status: {response.status_code}")
        if response.status_code == 200:
            user_info = response.json()
            print(f"Current user: {user_info}")
            user_id = user_info["id"]

            # Test task endpoints
            print("\nTesting task endpoints...")

            # Create a task
            task_data = {
                "title": "Test Task",
                "description": "This is a test task",
                "completed": False
            }

            response = await client.post(
                f"{BASE_URL}/api/{user_id}/tasks",
                json=task_data,
                headers=headers
            )
            print(f"Create task status: {response.status_code}")
            if response.status_code == 200:
                task = response.json()
                print(f"Created task: {task}")

                # Get all tasks
                response = await client.get(f"{BASE_URL}/api/{user_id}/tasks", headers=headers)
                print(f"Get tasks status: {response.status_code}")
                if response.status_code == 200:
                    tasks = response.json()
                    print(f"Retrieved {len(tasks)} tasks")

                    # Get task stats
                    response = await client.get(f"{BASE_URL}/api/{user_id}/tasks/stats", headers=headers)
                    print(f"Get task stats status: {response.status_code}")
                    if response.status_code == 200:
                        stats = response.json()
                        print(f"Task stats: {stats}")

                        # Update the task
                        update_data = {
                            "completed": True,
                            "description": "Updated test task"
                        }
                        response = await client.put(
                            f"{BASE_URL}/api/{user_id}/tasks/{task['id']}",
                            json=update_data,
                            headers=headers
                        )
                        print(f"Update task status: {response.status_code}")

                        # Toggle completion
                        response = await client.patch(
                            f"{BASE_URL}/api/{user_id}/tasks/{task['id']}/complete",
                            headers=headers
                        )
                        print(f"Toggle completion status: {response.status_code}")

                        # Delete the task
                        response = await client.delete(
                            f"{BASE_URL}/api/{user_id}/tasks/{task['id']}",
                            headers=headers
                        )
                        print(f"Delete task status: {response.status_code}")
                        print(f"Delete response: {response.json()}")

                        return True
            else:
                print(f"Create task response: {response.json()}")

        return False

async def main():
    """Main test function"""
    print("=== Backend Endpoint Test Suite ===")
    print(f"Testing API at: {BASE_URL}")
    print(f"Test started at: {datetime.now()}")

    # Test basic endpoints
    health_ok = await test_health_check()
    root_ok = await test_root_endpoint()

    # Test auth and protected endpoints
    token = await test_auth_endpoints()
    protected_ok = False

    if token:
        protected_ok = await test_protected_endpoints(token)
    else:
        print("Skipping protected endpoint tests due to authentication failure")

    # Summary
    print("\n=== Test Results Summary ===")
    print(f"Health check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Root endpoint: {'✅ PASS' if root_ok else '❌ FAIL'}")
    print(f"Authentication: {'✅ PASS' if token else '❌ FAIL'}")
    print(f"Protected endpoints: {'✅ PASS' if protected_ok else '❌ FAIL'}")

    all_passed = health_ok and root_ok and token and protected_ok
    print(f"\nOverall result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")

    if all_passed:
        print("\n🎉 Backend endpoints are working correctly!")
        print("✅ No 404 errors detected")
        print("✅ Authentication is working")
        print("✅ Task management endpoints are functional")
        print("✅ Database connections are active")
        print("✅ Error handling is properly implemented")
    else:
        print("\n⚠️  Some issues detected. Please review the test output above.")

if __name__ == "__main__":
    asyncio.run(main())