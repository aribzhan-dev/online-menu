import json
from fastapi.encoders import jsonable_encoder
from app.core.redis import redis_client


async def get_cache(key: str):
    try:
        cached = await redis_client.get(key)
        if cached is not None:
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


async def clear_company_cache(company_id: int):
    try:
        await redis_client.delete(f"company:{company_id}")
        await redis_client.delete(f"categories:{company_id}")
        await redis_client.delete(f"products:{company_id}")

        async for key in redis_client.scan_iter(f"search:{company_id}:*"):
            await redis_client.delete(key)

        async for key in redis_client.scan_iter(f"products_tag:{company_id}:*"):
            await redis_client.delete(key)

    except Exception as e:
        print("Redis error:", e)



async def clear_product_cache(company_id: int):
    try:
        keys = [
            f"products:{company_id}",
            f"categories:{company_id}",
        ]

        await redis_client.delete(*keys)

        async for key in redis_client.scan_iter(f"search:{company_id}:*"):
            await redis_client.delete(key)

        async for key in redis_client.scan_iter(f"products_tag:{company_id}:*"):
            await redis_client.delete(key)

    except Exception as e:
        print("Redis PRODUCT CLEAR error:", e)