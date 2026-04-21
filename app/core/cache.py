import json
from fastapi.encoders import jsonable_encoder
from app.core.redis import redis_client


async def get_cache(key: str):
    try:
        cached = await redis_client.get(key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        print("Redis GET error:", e)
    return None


async def set_cache(key: str, data, ttl: int = 60):
    try:
        await redis_client.set(
            key,
            json.dumps(jsonable_encoder(data), ensure_ascii=False),
            ex=ttl
        )
    except Exception as e:
        print("Redis SET error:", e)


async def clear_product_cache(company_id: int):
    try:
        keys = await redis_client.keys(f"*:{company_id}*")
        if keys:
            await redis_client.delete(*keys)
    except Exception as e:
        print("Redis CLEAR error:", e)


async def clear_company_cache(company_id: int):
    try:
        keys = await redis_client.keys(f"*:{company_id}*")
        if keys:
            await redis_client.delete(*keys)
    except Exception as e:
        print("Redis CLEAR error:", e)