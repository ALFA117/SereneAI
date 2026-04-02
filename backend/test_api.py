"""Quick test — run with: python test_api.py"""
import asyncio, os, httpx
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

KEY = os.getenv("OXLO_API_KEY")
BASE = os.getenv("OXLO_BASE_URL", "https://api.oxlo.ai/v1")

async def main():
    headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    print(f"Testing key: {KEY[:12]}...")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{BASE}/embeddings",
            headers=headers,
            json={"model": "bge-large", "input": "prueba de embedding"},
        )
        print(f"Status: {resp.status_code}")
        data = resp.json()
        if resp.status_code == 200:
            vec = data["data"][0]["embedding"]
            print(f"OK — vector dims: {len(vec)}")
        else:
            print(f"ERROR: {data}")

asyncio.run(main())
