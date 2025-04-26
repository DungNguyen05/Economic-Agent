#!/usr/bin/env python
"""
Mattermost Integration Test Script

This script sends requests in the exact format that Mattermost would use
to test compatibility with the OpenAI API format.
"""

import requests
import json
import os
import time
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_mattermost_format(base_url, api_key):
    """Test using the exact format Mattermost would use"""
    print("\n---Testing with exact Mattermost format---\n")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # This is the exact format Mattermost uses based on their documentation
    payload = {
        "model": "economic-chatbot",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the current price of Bitcoin?"}
        ],
        "temperature": 0.7,
        "top_p": 1,
        "n": 1,
        "stream": False,
        "max_tokens": 1000,
        "presence_penalty": 0,
        "frequency_penalty": 0
    }
    
    print(f"Sending request to: {base_url}/chat/completions")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("\nResponse JSON:")
                print(json.dumps(result, indent=2))
                
                # Check for important OpenAI fields that Mattermost might be expecting
                required_fields = ["id", "object", "created", "model", "choices"]
                missing = [field for field in required_fields if field not in result]
                
                if missing:
                    print(f"\n⚠️ Warning: Response is missing required fields: {missing}")
                else:
                    print("\n✅ Response has all required fields")
                
                # Check for choices array structure
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        print("\n✅ Response contains message content")
                        
                        content = choice["message"]["content"]
                        print(f"\nMessage content: {content}")
                    else:
                        print("\n⚠️ Warning: Response is missing message content in choices")
                else:
                    print("\n⚠️ Warning: Response is missing choices array or it's empty")
                
            except json.JSONDecodeError:
                print("\n❌ Error: Response is not valid JSON")
                print(f"Raw response: {response.text}")
        else:
            print(f"\n❌ Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")

def test_mattermost_variations(base_url, api_key):
    """Test various request formats that Mattermost might use"""
    variations = [
        # Standard format
        {
            "endpoint": "/chat/completions",
            "payload": {
                "model": "economic-chatbot",
                "messages": [
                    {"role": "user", "content": "What is inflation?"}
                ]
            }
        },
        # Using v1 prefix
        {
            "endpoint": "/v1/chat/completions",
            "payload": {
                "model": "economic-chatbot",
                "messages": [
                    {"role": "user", "content": "Tell me about economics"}
                ]
            }
        },
        # With user field
        {
            "endpoint": "/chat/completions",
            "payload": {
                "model": "economic-chatbot",
                "messages": [
                    {"role": "user", "content": "What are interest rates?"}
                ],
                "user": "test_user_id"
            }
        }
    ]
    
    print("\n---Testing variations of Mattermost requests---\n")
    
    for i, variation in enumerate(variations):
        print(f"\nTest {i+1}: {variation['endpoint']}")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{base_url}{variation['endpoint']}",
                headers=headers,
                json=variation['payload'],
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Just check if we got message content
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        content = choice["message"]["content"]
                        print(f"Response: {content[:100]}..." if len(content) > 100 else f"Response: {content}")
                        print("✅ Success")
                    else:
                        print("❌ Missing message content")
                else:
                    print("❌ Missing choices array")
                    print(f"Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Error: {response.text}")
        
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Mattermost integration")
    parser.add_argument("--url", default="http://localhost:8000",
                        help="Base URL of the server (default: http://localhost:8000)")
    parser.add_argument("--key", default=os.getenv("OPENAI_API_KEY"),
                        help="API key for authentication (default: from .env file)")
    
    args = parser.parse_args()
    
    if not args.key:
        print("Error: No API key provided. Set it with --key or in the .env file.")
        exit(1)
    
    test_mattermost_format(args.url, args.key)
    test_mattermost_variations(args.url, args.key)