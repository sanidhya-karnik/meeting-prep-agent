import asyncio
import httpx

async def test():
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.get('http://127.0.0.1:64582/v1/models')
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(test())
