import redis

def get_redis_client(redis_host, redis_port, redis_user="default", redis_pw="N/A"):
    redis_port = int(redis_port)
    if redis_pw == "N/A":
        r = redis.Redis(host=redis_host, port=redis_port)
    else:
        r = redis.Redis(host=redis_host, port=redis_port, username=redis_user, password=redis_pw, decode_responses=True)
    return r

def get_index_list(r):
    return r.execute_command("FT._LIST")