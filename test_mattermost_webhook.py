#!/usr/bin/env python
"""
Mattermost Webhook Integration Test Script

This script simulates Mattermost webhook requests to test the integration.
"""

import requests
import json
import os
import time
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_mattermost_webhook(base_url):
    """Test the Mattermost webhook integration"""
    # Colors for console output
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    
    print(f"\n{YELLOW}Testing Mattermost webhook integration at {base_url}/webhook/mattermost{RESET}\n")
    
    # Example webhook data from Mattermost
    webhook_data = {
        "token": "rkz9eqjnopdg7rbqmbsk8x1aue",
        "team_id": "cwnb3tatpjbkpcgjwtj67h9h5e",
        "team_domain": "sphoton",
        "channel_id": "e8y3bo7u5bnrdm3ogqmfmdp5hy",
        "channel_name": "test-chat-bot",
        "timestamp": int(time.time() * 1000),
        "user_id": "qubwiezhoib87xdgzdprdzgpwe",
        "user_name": "ducnt",
        "post_id": "9dyjyt31bfbwzf4kdwkkkdun1e",
        "text": "@vitest Xin chào",
        "trigger_word": "@vitest",
        "file_ids": ""
    }
    
    # Test 1: Basic webhook functionality
    print("Test 1: Basic webhook functionality...")
    try:
        response = requests.post(
            f"{base_url}/webhook/mattermost",
            data=webhook_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"{GREEN}✓ Webhook endpoint is responding{RESET}")
            try:
                result = response.json()
                if "text" in result:
                    print(f"{GREEN}✓ Response contains 'text' field as expected{RESET}")
                    print(f"\nResponse text: {YELLOW}{result['text'][:200]}...{RESET}" if len(result['text']) > 200 else f"\nResponse text: {YELLOW}{result['text']}{RESET}")
                else:
                    print(f"{RED}✗ Response is missing the 'text' field required by Mattermost{RESET}")
            except json.JSONDecodeError:
                print(f"{RED}✗ Response is not valid JSON: {response.text}{RESET}")
        else:
            print(f"{RED}✗ Webhook endpoint returned status code {response.status_code}{RESET}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ Failed to connect to webhook endpoint: {e}{RESET}")
    
    # Test 2: Test with different trigger word
    print("\nTest 2: Test with different trigger word...")
    webhook_data["trigger_word"] = "@economic-bot"
    webhook_data["text"] = "@economic-bot What is inflation?"
    
    try:
        response = requests.post(
            f"{base_url}/webhook/mattermost",
            data=webhook_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"{GREEN}✓ Webhook handles different trigger words{RESET}")
            try:
                result = response.json()
                if "text" in result:
                    print(f"\nResponse text: {YELLOW}{result['text'][:200]}...{RESET}" if len(result['text']) > 200 else f"\nResponse text: {YELLOW}{result['text']}{RESET}")
                else:
                    print(f"{RED}✗ Response is missing the 'text' field{RESET}")
            except json.JSONDecodeError:
                print(f"{RED}✗ Response is not valid JSON: {response.text}{RESET}")
        else:
            print(f"{RED}✗ Webhook endpoint returned status code {response.status_code}{RESET}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ Failed during trigger word test: {e}{RESET}")
    
    # Test 3: Empty message test
    print("\nTest 3: Empty message test...")
    webhook_data["text"] = "@economic-bot "
    
    try:
        response = requests.post(
            f"{base_url}/webhook/mattermost",
            data=webhook_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"{GREEN}✓ Webhook handles empty messages{RESET}")
            try:
                result = response.json()
                if "text" in result:
                    print(f"\nResponse text: {YELLOW}{result['text']}{RESET}")
                else:
                    print(f"{RED}✗ Response is missing the 'text' field{RESET}")
            except json.JSONDecodeError:
                print(f"{RED}✗ Response is not valid JSON: {response.text}{RESET}")
        else:
            print(f"{RED}✗ Webhook endpoint returned status code {response.status_code}{RESET}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ Failed during empty message test: {e}{RESET}")
    
    print(f"\n{YELLOW}Testing complete!{RESET}")
    print(f"\n{GREEN}Integration URL for Mattermost Outgoing Webhook:{RESET}")
    print(f"{GREEN}{base_url}/webhook/mattermost{RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Mattermost webhook integration")
    parser.add_argument("--url", default="http://localhost:8000",
                        help="Base URL of the server (default: http://localhost:8000)")
    
    args = parser.parse_args()
    test_mattermost_webhook(args.url)