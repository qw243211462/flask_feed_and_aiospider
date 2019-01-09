from flask import current_app, jsonify
from sqlalchemy import func

from application import db, redis_conn
from app.mq.models import User_friend_follow, System_message, User_message
from app.user.models import  User
from app.response_code import RET


#添加好友
def save_user_friendship(user_id, friend_id):
    user_friend_follow = User_friend_follow()
    user_friend_follow.user_id = user_id
    user_friend_follow.friend_id = friend_id
    try:
        db.session.add(user_friend_follow)
        db.session.commit()
        current_app.logger.info("add friendship is success")
        return True
    except Exception as e:
        current_app.logger.info("add friendship is failed, reason is %s", e)
        db.session.rollback()
        return False

#删除用户好友
def delete_user_friendship(user_id, friend_id):
    try:
        db.session.query(User_friend_follow).filter(User_friend_follow.user_id == user_id , User_friend_follow.friend_id == friend_id).delete()
        db.session.commit()
        current_app.logger.info("delete friendship is success, user_id is %s, friend_id is %s", user_id, friend_id)
        return True
    except Exception as e:
        current_app.logger.error("delete friendship is failed, reason is %s", e)
        return False

#获取用户好友的名字和数量
def get_user_friendship(user_id):
    #friends = db.session.query(User_friend_follow.friend_id).filter(user_id == user_id).all()
    #friends1 = db.session.query(User_friend_follow, User).filter(User_friend_follow.friend_id == User.id).filter(User_friend_follow.user_id == user_id).all()
    friends = db.session.query(User).join(User_friend_follow, User.id == User_friend_follow.friend_id).filter(User_friend_follow.user_id == user_id).all()
    count_friends = len(friends)
    friends_names = {}
    count = 0
    for friend in friends:
        friends_names[count] = friend.nickname
        count += 1

    return friends_names, count_friends

#获得用户好友的所有id
def get_user_friend_id(user_id):
    friend_ids = db.session.query(User_friend_follow.friend_id).filter(User_friend_follow.user_id == user_id).all()
    friend_ids_list = []
    for friend in friend_ids:
        friend_ids_list.append(friend[0])
    return friend_ids_list


#将系统消息存储到mysql
def save_system_message(content):
    system_message = System_message(content = content)
    try:
        db.session.add(system_message)
        db.session.commit()
        current_app.logger.info("add systemt message is success, message id is %s", system_message.id)
    except Exception as e:
        current_app.logger.error("add systemt message is failed, reason is %s", e)
        db.session.rollback()
    return system_message.id

#将用户动态存储到mysql
def save_user_message_to_db(user_id, content):
    user_message = User_message(content=content)
    try:
        db.session.add(user_message)
        db.session.commit()
        current_app.logger.info("save user_message is success")
    except Exception as e:
        current_app.logger.error("save user_message is failed, reason is %s", e)
        db.session.rollback()
    return user_message.id

#用户拉取动态消息
def pull_message(user_id):
    #从消息流汇总获得用户动态id
    user_message_key = "user{}:receive:user_message".format(user_id)
    user_message_info = {}
    count = 1
    user_message_ids = redis_conn.zrange(user_message_key, -10, -1, withscores=True)
    for user_message_id in user_message_ids:
        user_info = {}
        query_info = db.session.query(func.date_format(User_message.created, "%Y-%m-%d %H:%i:%s"), User_message.content).filter(User_message.id == int(user_message_id[1])).all()
        user_info["created_time"] = query_info[0][0]
        user_info["content"] = query_info[0][1]
        user_message_info.setdefault("{}".format(count), user_info)
        count = count + 1
    current_app.logger.info("get user_message_info result is success, result is {}".format(user_message_info))
    return user_message_info