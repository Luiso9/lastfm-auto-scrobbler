import httpx
import asyncio
import json

async def main():
    async with httpx.AsyncClient() as client:
        res = await client.get("http://54.254.230.226:8080")
        pretty = res.json()
        queue = [(item["artist"], item["track"]) for item in pretty["queue"]]
        print(pretty)

asyncio.run(main())
