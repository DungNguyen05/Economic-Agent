#!/usr/bin/env python
"""
OpenAI Compatible API Test Script

This script tests the OpenAI compatibility endpoints to ensure they
are working correctly for Mattermost integration.
"""

import requests
import json
import os
import time
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_openai_endpoints(base_url, api_key):
    """Test the OpenAI compatibility endpoints"""
    # Colors for console output
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    
    print(f"\n{YELLOW}Testing OpenAI compatible endpoints at {base_url}{RESET}\n")
    
    # Test 1: Check if server is reachable
    print("Test 1: Checking if server is reachable...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"{GREEN}✓ Server is reachable{RESET}")
        else:
            print(f"{RED}✗ Server responded with status code {response.status_code}{RESET}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ Failed to connect to server: {e}{RESET}")
        return
    
    # Test 2: Check models endpoint
    print("\nTest 2: Testing /v1/models endpoint...")
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{base_url}/v1/models", headers=headers, timeout=5)
        
        if response.status_code == 200:
            print(f"{GREEN}✓ Models endpoint is working{RESET}")
            models = response.json()
            print(f"Available models: {[model['id'] for model in models.get('data', [])]}")
        else:
            print(f"{RED}✗ Models endpoint returned status code {response.status_code}{RESET}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ Failed to connect to models endpoint: {e}{RESET}")
    
    # Test 3: Test chat completions endpoint
    print("\nTest 3: Testing /v1/chat/completions endpoint...")
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "economic-chatbot",
            "messages": [
                {"role": "user", "content": "What is the current price of Bitcoin?"}
            ],
            "temperature": 0.3
        }
        
        start_time = time.time()
        response = requests.post(f"{base_url}/v1/chat/completions", 
                                headers=headers, 
                                json=payload, 
                                timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"{GREEN}✓ Chat completions endpoint is working{RESET}")
            print(f"Response time: {end_time - start_time:.2f} seconds")
            
            completion = response.json()
            content = completion.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            print(f"\nResponse content: {YELLOW}{content[:200]}...{RESET}" if len(content) > 200 else f"\nResponse content: {YELLOW}{content}{RESET}")
            
            # Print token usage if available
            if 'usage' in completion:
                print(f"\nToken usage:")
                print(f"  Prompt tokens: {completion['usage']['prompt_tokens']}")
                print(f"  Completion tokens: {completion['usage']['completion_tokens']}")
                print(f"  Total tokens: {completion['usage']['total_tokens']}")
        else:
            print(f"{RED}✗ Chat completions endpoint returned status code {response.status_code}{RESET}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ Failed to connect to chat completions endpoint: {e}{RESET}")
    
    # Test 4: Test the fallback /chat/completions endpoint (without v1 prefix)
    print("\nTest 4: Testing fallback /chat/completions endpoint...")
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "economic-chatbot",
            "messages": [
                {"role": "user", "content": "What is inflation?"}
            ],
            "temperature": 0.3
        }
        
        response = requests.post(f"{base_url}/chat/completions", 
                                headers=headers, 
                                json=payload, 
                                timeout=30)
        
        if response.status_code == 200:
            print(f"{GREEN}✓ Fallback chat completions endpoint is working{RESET}")
        else:
            print(f"{RED}✗ Fallback chat completions endpoint returned status code {response.status_code}{RESET}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ Failed to connect to fallback chat completions endpoint: {e}{RESET}")
    
    # Test 5: Test authentication
    print("\nTest 5: Testing authentication...")
    try:
        headers = {
            "Authorization": f"Bearer invalid_key",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "economic-chatbot",
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        
        response = requests.post(f"{base_url}/v1/chat/completions", 
                                headers=headers, 
                                json=payload, 
                                timeout=5)
        
        if response.status_code == 401:
            print(f"{GREEN}✓ Authentication is working correctly{RESET}")
        else:
            print(f"{RED}✗ Authentication test failed. Expected 401, got {response.status_code}{RESET}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ Failed during authentication test: {e}{RESET}")
    
    print(f"\n{YELLOW}Testing complete!{RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test OpenAI compatibility endpoints")
    parser.add_argument("--url", default="http://localhost:8000",
                        help="Base URL of the server (default: http://localhost:8000)")
    parser.add_argument("--key", default=os.getenv("OPENAI_API_KEY"),
                        help="API key for authentication (default: from .env file)")
    
    args = parser.parse_args()
    
    if not args.key:
        print("Error: No API key provided. Set it with --key or in the .env file.")
        exit(1)
    
    test_openai_endpoints(args.url, args.key)