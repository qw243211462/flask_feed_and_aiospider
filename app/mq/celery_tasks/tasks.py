from flask import current_app
from datetime import datetime

from celery.utils.log import get_task_logger
from application import celery
from app.mq.models import User_message
from application import db, redis_conn
from app.mq.utils.db import get_user_friend_id
from app.user.models import User

logger = get_task_logger(__name__)


print(celery.conf)

#采用mysql方式进行存储
# @celery.task(bind=True, default_retry_delay=300, max_retries=5,queue="for_push_announce")
# def push_announce(self,content, sender):
#     time_begin=datetime.now()
#     notify = Notify(content = content, sender = sender, type = 1)
#     try:
#         db.session.add(notify)
#         db.session.commit()
#         logger.info('user "%s" push announce "%s"', sender, content)
#     except Exception as exc:
#         retries = self.request.retries
#         if retries < self.max_retries:
#             delta_second = (datetime.now() - time_begin).seconds
#             if delta_second < 5:
#                 return self.retry(exc=exc, countdown=5 - delta_second)
#             else:
#                 return self.retry(exc=exc, countdown=0)
#     finally:
#         pass

#将消息存入redis
#发送公告
@celery.task(bind=True, default_retry_delay=300, max_retries=5,queue="for_push_announce")
def push_announce(self, content):
    time_now = datetime.now()

#用户发送动态
@celery.task(bind=True, default_retry_delay=300, max_retries=5,queue="for_user_push_message")
def push_message(self, message_id, uid):
    #将用户动态存入mysql中，并且拿到id，并将id存入到SortedSet中，将该动态id存储到粉丝的收feed中
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #将消息id存入用户自己的发送feed流中
    redis_conn.zadd("user{}:send:user_message".format(uid), message_id, time_now)
    user_friends = get_user_friend_id(uid)
    for user_friend in user_friends:
        #将该消息id存入用户粉丝的未读feed流中
        redis_conn.zadd("user{}:receive:user_message".format(user_friend), message_id, time_now)


#将系统消息id添加到用户未读的消息队列中
@celery.task(bind=True, default_retry_delay=300, max_retries=5,queue="for_system_message")
def save_system_message_to_redis(self, system_message_id):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_ids = db.session.query(User.id).all()
    for user_id in user_ids:
        redis_conn.zadd("user{}:system_message".format(user_id[0]), system_message_id, time_now)


#用户取消关注后，删除在该用户feed流中对应用户的消息id
@celery.task(bind=True, default_retry_delay=300, max_retries=5,queue="for_delete_user_message")
def delete_user_message(self, uid, delete_uid):
    #delete_user_message_ids_list = []
    delete_user_message_read_key = "user{}:send:user_message".format(delete_uid)
    user_message_receive_key = "user{}:receive:user_message".format(uid)
    redis_conn.zinterstore("user{}:delete_user_message:user{}".format(uid, delete_uid), (delete_user_message_read_key, user_message_receive_key),
                           aggregate="MIN")
    delete_infos = redis_conn.zrange("user{}:delete_user_message:user{}".format(uid, delete_uid), 0, -1, withscores=True)
    logger.info("*********", delete_infos)
    #在取消关注用户的feed流中删除对应的被删除者消息id
    for delete_info in delete_infos:
        redis_conn.zrem(user_message_receive_key, str(delete_info[0].decode('utf8')))

