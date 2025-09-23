#!/usr/bin/env python3
"""
Simple API Test Script
"""

import requests
import json

def test_chat_api():
    print("Testing Chat API")

    url = "http://localhost:8001/chat"
    headers = {"Content-Type": "application/json"}
    data = {"message": "Hello, what services do you offer?"}

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        print("Chat API test completed successfully")
    except requests.exceptions.Timeout:
        print("Request timed out")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chat_api()