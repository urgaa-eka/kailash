#!/usr/bin/env python3
"""
Test GANESHA AI Service directly
"""
import asyncio
import sys
import os
sys.path.append('/app/backend')

from app.services.ganesha_ai import ganesha_ai

async def test_ganesha_ai():
    """Test GANESHA AI processing"""
    print("Testing GANESHA AI Service...")
    
    try:
        # Test with a simple command
        result = await ganesha_ai.process_command(
            command="Review Q4 charging station performance",
            priority="high",
            timeout=
        )
        
        print("[OK] GANESHA AI Test Successful!")
        print(f"Result: {result}")
        return True
        
    except Exception as e:
        print(f"[AIL] GANESHA AI Test ailed: {str(e)}")
        return alse

if __name__ == "__main__":
    success = asyncio.run(test_ganesha_ai())
    sys.exit( if success else )