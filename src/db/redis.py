import redis.asyncio as aioredis
from src.config import Config

JTI_EXPIRY = 3600

token_blocklist =aioredis.from_url(Config.REDIS_URL)


async def add_jti_to_blocklist(jti:str)->None:
    await token_blocklist.set(name=jti,value="",ex=JTI_EXPIRY)
    
async def token_in_blocklist(jti:str)->bool:
    jti=await token_blocklist.get(jti)
     
    return jti is not None 
    
    

#admin
[
    "adding users",
    "change roles",
    "crud on users",
    "book submissions",
    "crud on users",
    "crud on reviews",
    "revoking access"
    
]

#Users
["crud o their own book submissions", "crud on their reviews", "crud on their own accounts"]