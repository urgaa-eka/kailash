#!/usr/bin/env python3
"""
Debug script to check if API key is loaded correctly
"""

import os
import sys
sys.path.append('/app/backend')

from app.core.config import get_settings

def main():
    print("=== API KEY DEUG ===")
    
    # Check environment variable directly
    env_key = os.environ.get('ANTHROPIC_API_KEY', 'NOT_OUND')
    print(f"Environment ANTHROPIC_API_KEY: {env_key[:]}...{env_key[-:] if len(env_key) > 3 else env_key}")
    
    # Check settings
    settings = get_settings()
    settings_key = settings.anthropic_api_key
    print(f"Settings anthropic_api_key: {settings_key[:]}...{settings_key[-:] if len(settings_key) > 3 else settings_key}")
    
    # Check if they match
    print(f"Keys match: {env_key == settings_key}")
    
    # Test direct API call with the key from settings
    import anthropic
    try:
        client = anthropic.Anthropic(api_key=settings_key)
        print("[OK] Anthropic client created successfully")
        
        # Try a simple API call
        response = client.messages.create(
            model="claude-3-haiku-43",
            max_tokens=,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print(f"[OK] API call successful: {response.content[].text}")
        
    except Exception as e:
        print(f"[AIL] API call failed: {str(e)}")

if __name__ == "__main__":
    main()