from src.RedisManager import RedisManager, REDIS_HOST, REDIS_PORT


REDIS_MANAGER = RedisManager(
    host=REDIS_HOST,
    port=REDIS_PORT
)

# Simulated original expensive calculation function
def expensive_db_calculation(user_id: int) -> List[dict]:
    """ Simulates a complex account total value calculation """
    print(f"--- ⚠️ Performing EXPENSIVE calculation for User ID: {user_id} ---")
    time.sleep(1)
    return [
        {
            "product": "DECUMULATOR",
            "cashflow": 1213213,
            "total": 122132131
        },
        {
            "product": "ACCUMULATOR",
            "total2": 2132131
        }
    ]


def get_product_with_cache(user_id: int) -> dict:
    """
    Application logic implementing the Cache-Aside pattern.
    """
    cache_key = f"account_value:{user_id}"
    EXPIRATION = 120  # 2 minutes

    # 1. Try to READ from cache
    product_data = CACHE_MANAGER.get(cache_key)

    if product_data is not None:
        # Cache Hit: directly return cached data
        print(f"--- 🎯 Cache HIT for User ID: {user_id} ---")
        return product_data

    # 2. Cache Miss: perform expensive calculation
    print(f"--- 🚫 Cache MISS for User ID: {user_id}. Loading from DB. ---")
    product_data = expensive_db_calculation(user_id)

    # 3. WRITE result back to cache
    success = CACHE_MANAGER.set(cache_key, product_data, EXPIRATION)

    if success:
        print(f"--- ✅ Data written to cache for User ID: {user_id} ---")
    else:
        # This occurs if Redis is down or write fails, the app still serves the DB data
        print(f"--- ⚠️ Failed to write to cache for User ID: {user_id}. ---")

    return product_data

def main():
    user_id = 1111

    # 第一次查询：Cache MISS -> DB 计算 -> 写入缓存
    print("\n--- First Query: Cache MISS ---")
    get_product_with_cache(user_id)

    # 第二次查询：Cache HIT -> 直接返回
    print("\n--- Second Query: Cache HIT ---")
    start_time = time.time()
    result = get_product_with_cache(user_id)
    end_time = time.time()

    print(f"Final Account Value: {result['total_value']}")
    print(f"Cache HIT retrieval time: {end_time - start_time:.4f} seconds.")

    # 演示主动失效
    print("\n--- Demo: Active Cache Invalidation ---")
    CACHE_MANAGER.delete(f"account_value:{user_id}")
    get_account_value_with_cache(user_id)  # 强制 MISS and SET


if __name__ == "__main__":
    main()
