import asyncio
from redis import asyncio as redis

async def main():
    r = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True
    )

    print(await r.ping())

asyncio.run(main())