from flask import current_app
from flask import jsonify,request
from flask.views import MethodView
import json

from app.response_code import RET
from app.mq.celery_tasks.tasks import push_announce
from app.user.utils.check_in_user_status import login_required
from app.mq.utils.db import save_user_friendship, delete_user_friendship, \
                            save_system_message, get_user_friendship, \
                            save_user_message_to_db, pull_message
from app.mq.celery_tasks.tasks import push_message, save_system_message_to_redis,\
                                    delete_user_message

from celery import Celery



#发送公告

# class Push_announce(MethodView):
#
#     def get(self):
#         return jsonify(re_code = RET.METHODNOTALLOWERR, msg = '请求类型不正确，需要post方法')
#
#     #@login_required
#     def post(self):
#
#         content = request.json.get('content')
#         sender = request.json.get('sender')
#
#         push_announce.delay(content = content,
#                             sender = sender)
#
#         return jsonify(re_code=RET.OK, msg='公告发送成功')

#系统公告
class Push_system_message(MethodView):

    def get(self):
        return jsonify(re_code=RET.METHODNOTALLOWERR, msg='请求类型不正确，需要post方法')

    def post(self):

        content = request.json.get('content')

        system_id = save_system_message(content)
        save_system_message_to_redis.delay(system_id)
        if system_id:
            return jsonify(re_code=RET.OK, msg="添加系统消息成功")
        else:
            return jsonify(re_code=RET.DBERR, msg="添加系统消息失败")

#拉取系统公告
class Pull_system_message(MethodView):

    def get(self):
        return jsonify(re_code=RET.METHODNOTALLOWERR, msg='请求类型不正确，需要post方法')

    def post(self):

        user_id = request.json.get("user_id")


#私信
class Push_private_message(MethodView):

    def get(self):
        return jsonify(re_code=RET.METHODNOTALLOWERR, msg='请求类型不正确，需要post方法')

    def post(self):
        pass

#关注
class User_follow(MethodView):

    def get(self):
        return jsonify(re_code=RET.METHODNOTALLOWERR, msg='请求类型不正确，需要post方法')

    def post(self):

        user_id = request.json.get("user_id")
        friend_id = request.json.get("friend_id")
        result = save_user_friendship(user_id, friend_id)
        '''
         To do 
         将被关注用户动态添加到关注用户维护的消息队列中
        '''
        if result == False:
            return jsonify(re_code=RET.DBERR, msg="添加好友失败")
        else:
            return jsonify(re_code=RET.OK, msg="添加好友成功")


#取消关注
class User_not_follow(MethodView):

    def get(self):
        return jsonify(re_code=RET.METHODNOTALLOWERR, msg='请求类型不正确，需要post方法')

    def post(self):
        user_id = request.json.get("user_id")
        friend_id = request.json.get("friend_id")

        result = delete_user_friendship(user_id, friend_id)
        delete_user_message.delay(user_id, friend_id)
        if result == True:
            return  jsonify(re_code=RET.OK, msg="删除好友成功")
        else:
            return jsonify(re_code=RET.DBERR, msg="删除好友失败")

#发送动态
class Push_user_message(MethodView):


    def get(self):
        return jsonify(re_code=RET.METHODNOTALLOWERR, msg='请求类型不正确，需要post方法')

    def post(self):

        user_id = request.json.get("user_id")
        content = request.json.get("content")
        message_id = save_user_message_to_db(user_id, content)
        push_message.delay(message_id, user_id)
        if message_id:
            return jsonify(re_code=RET.OK, msg="发送动态成功")
        else:
            return jsonify(re_code=RET.DBERR, msg="发送失败")

#拉取通知,从feed流里面拉取
class Pull_notice(MethodView):

    def get(self):
        return jsonify(re_code=RET.METHODNOTALLOWERR, msg='请求类型不正确，需要post方法')

    def post(self):

        user_id = request.json.get("user_id")

        user_message_infos = pull_message(user_id)
        if user_message_infos:
            return jsonify(re_code=RET.OK, msg="拉取动态成功", user_message_infos = json.dumps(user_message_infos))
        else:
            return jsonify(re_code=RET.DBERR, msg="拉取动态失败")


#拉取用户好友
class Pull_user_friendship(MethodView):

    def get(self):
        return jsonify(re_code=RET.METHODNOTALLOWERR, msg='请求类型不正确，需要post方法')

    def post(self):
        user_id = request.json.get("user_id")
        friends,count_friends = get_user_friendship(user_id)
        if friends:
            current_app.logger.info("Pull user friendship is success, user id is %s", user_id)
            return jsonify(re_code = RET.OK, msg = "获取好友成功", friends = json.dumps(friends), count_friends = count_friends)
        else:
            current_app.logger.error("Pull user friendship is failed, user id is %s", user_id)
            return jsonify(re_code=RET.DBERR, msg="获取好友失败")





