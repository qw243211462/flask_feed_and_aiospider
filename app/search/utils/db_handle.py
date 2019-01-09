import time
from functools import wraps

from application import redis_conn


#搜索记录存储到redis
def save_search_history_to_redis(user_id, target_name):
    user_search_key = "recent_search_" + str(user_id)
    pipline = redis_conn.pipeline(True)
    pipline.lrem(user_search_key, 1, str(target_name))
    pipline.lpush(user_search_key, target_name)
    pipline.ltrim(user_search_key, 0, 9)
    pipline.execute()


#读取搜索历史
def get_search_history_from_redis(user_id, prefix):
    user_search_key = "recent_search_" + str(user_id)
    all_history = redis_conn.lrange(user_search_key, 0 ,-1)
    count = 1
    match = {}
    if all_history == None:
        return False
    if (prefix != None) & (len(prefix) > 0):
        for history in all_history:
            if history.lower().startswith(prefix.encode('utf8')):
                match["{}".format(count)] = history.decode('utf8')
                count = count + 1
        return match
    else:
        for history in all_history:
            match["{}".format(count)] = history.decode('utf8')
            count = count + 1
        return match

#限制用户访问次数
def limit_user_visit(user_id):

    """
    LIMIT_TIME：在多长的时间范围内
    LIMIT_TIMES：最多访问多少次
    """

    LIMIT_TIMES = 3
    LIMIT_TIME = 60

    key_name = "login:times:%s" % user_id
    n = int(redis_conn.llen(key_name))
    if n < LIMIT_TIMES:
        redis_conn.lpush(key_name, time.time())
        return True
    else:
        now = time.time()
        recent_visit_time = float(redis_conn.lrange(key_name, 2, 2)[0])
        if now - recent_visit_time < LIMIT_TIME:
            return False
        else:
            redis_conn.rpop(key_name)
            redis_conn.lpush(key_name,now)
            return True





