#!/usr/bin/env python3
"""
Test script to verify the API is working correctly
"""
import asyncio
import httpx
import json

async def test_api():
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        print("Testing API endpoints...")

        # Test 1: Root endpoint
        print("\n1. Testing root endpoint...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"Root endpoint: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Root endpoint failed: {e}")

        # Test 2: Register user
        print("\n2. Testing user registration...")
        try:
            user_data = {
                "email": "test@example.com",
                "password": "password123",
                "name": "Test User"
            }
            response = await client.post(f"{base_url}/auth/register", json=user_data)
            print(f"Registration: {response.status_code}")
            if response.status_code == 200:
                auth_response = response.json()
                print(f"Auth response: {auth_response}")
                token = auth_response.get("access_token")
            else:
                print(f"Registration failed: {response.text}")
                token = None
        except Exception as e:
            print(f"Registration failed: {e}")
            token = None

        # Test 3: Login user
        print("\n3. Testing user login...")
        if not token:
            try:
                login_data = {
                    "email": "test@example.com",
                    "password": "password123"
                }
                response = await client.post(f"{base_url}/auth/login", json=login_data)
                print(f"Login: {response.status_code}")
                if response.status_code == 200:
                    auth_response = response.json()
                    print(f"Auth response: {auth_response}")
                    token = auth_response.get("access_token")
                else:
                    print(f"Login failed: {response.text}")
            except Exception as e:
                print(f"Login failed: {e}")

        # Test 4: Get user ID from token
        if token:
            try:
                import jwt
                from datetime import datetime

                decoded = jwt.decode(token, "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7", algorithms=["HS256"])
                user_id = int(decoded.get("sub"))
                print(f"\n4. User ID from token: {user_id}")

                # Test 5: Create a task
                print("\n5. Testing task creation...")
                try:
                    headers = {"Authorization": f"Bearer {token}"}
                    task_data = {
                        "title": "Test Task",
                        "description": "This is a test task",
                        "completed": False
                    }
                    response = await client.post(f"{base_url}/api/{user_id}/tasks", json=task_data, headers=headers)
                    print(f"Task creation: {response.status_code}")
                    if response.status_code == 200:
                        task = response.json()
                        print(f"Created task: {task}")
                        task_id = task.get("id")
                    else:
                        print(f"Task creation failed: {response.text}")
                        task_id = None
                except Exception as e:
                    print(f"Task creation failed: {e}")
                    task_id = None

                # Test 6: Get tasks
                print("\n6. Testing task retrieval...")
                try:
                    headers = {"Authorization": f"Bearer {token}"}
                    response = await client.get(f"{base_url}/api/{user_id}/tasks", headers=headers)
                    print(f"Task retrieval: {response.status_code}")
                    if response.status_code == 200:
                        tasks = response.json()
                        print(f"Retrieved tasks: {tasks}")
                    else:
                        print(f"Task retrieval failed: {response.text}")
                except Exception as e:
                    print(f"Task retrieval failed: {e}")

                # Test 7: Get specific task
                if task_id:
                    print(f"\n7. Testing specific task retrieval (ID: {task_id})...")
                    try:
                        headers = {"Authorization": f"Bearer {token}"}
                        response = await client.get(f"{base_url}/api/{user_id}/tasks/{task_id}", headers=headers)
                        print(f"Specific task retrieval: {response.status_code}")
                        if response.status_code == 200:
                            task = response.json()
                            print(f"Retrieved task: {task}")
                        else:
                            print(f"Specific task retrieval failed: {response.text}")
                    except Exception as e:
                        print(f"Specific task retrieval failed: {e}")

            except Exception as e:
                print(f"Token decoding failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())