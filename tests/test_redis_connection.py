import redis
import os


def test_redis_connection():
    # Get Redis URL from environment or use default
    redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")

    print(f"Attempting to connect to Redis at {redis_url}")

    try:
        # Create Redis client
        r = redis.Redis.from_url(redis_url)

        # Test connection with PING command
        response = r.ping()

        if response:
            print("✅ Successfully connected to Redis!")
            print("Redis server info:")
            info = r.info()
            print(f"  - Redis version: {info.get('redis_version')}")
            print(f"  - Connected clients: {info.get('connected_clients')}")
            print(f"  - Memory used: {info.get('used_memory_human')}")
            return True
        else:
            print("❌ Redis connection failed: PING returned False")
            return False

    except redis.exceptions.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
        print("Make sure Redis is running and accessible at the specified URL")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    test_redis_connection()
