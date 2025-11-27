def main():
    import redis

    # 1. 创建一个连接池
    pool = redis.ConnectionPool(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )

    # 2. 从连接池中获取 Redis 实例
    r = redis.Redis(connection_pool=pool)

    r.set('username', 'Alice')
    print("SET 操作完成。")

    # 设置一个键 'views'，值为 100
    r.set('views', 100)

    # 获取 'username' 的值
    name = r.get('username')
    print(f"获取 'username'：{name}")  # 结果是 'Alice' (如果 decode_responses=True)

    # 获取 'views' 的值
    views = r.get('views')
    print(f"获取 'views'：{views}")  # 结果是 '100'

    r.setex('temp_key', 300, 'this will expire soon')
    print("SETEX 操作完成。")

    # 设置 'views' 键 60 秒后过期
    r.expire('views', 60)
    print("EXPIRE 操作完成。")


if __name__ == "__main__":
    main()
