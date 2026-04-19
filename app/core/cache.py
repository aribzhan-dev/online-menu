import json
from functools import wraps
from app.core.redis import redis_client

def redis_cache(expire: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            try:
                cached = await redis_client.get(key)
                if cached:
                    return json.loads(cached)
            except:
                pass

            result = await func(*args, **kwargs)

            try:
                await redis_client.set(key, json.dumps(result), ex=expire)
            except:
                pass

            return result

        return wrapper
    return decorator