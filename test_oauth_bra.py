#!/usr/bin/env python3
"""Test BRA API with OAuth2 token."""
import asyncio
import sys
import aiohttp

async def test_bra_oauth(token: str):
    """Test BRA API with OAuth2 Bearer token."""
    print("Testing BRA API with OAuth2...")
    
    url = "https://public-api.meteofrance.fr/public/DPBRA/v1/massif/BRA"
    params = {"id-massif": 1, "format": "xml"}
    headers = {"Authorization": f"Bearer {token}"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            print(f"Status: {response.status}")
            if response.status == 200:
                xml = await response.text()
                print(f"✓ SUCCESS! Received {len(xml)} bytes")
                print(f"\nFirst 500 chars:\n{xml[:500]}")
                return True
            else:
                error = await response.text()
                print(f"✗ FAILED: {error}")
                return False

if __name__ == "__main__":
    token = sys.argv[1] if len(sys.argv) > 1 else ""
    asyncio.run(test_bra_oauth(token))
