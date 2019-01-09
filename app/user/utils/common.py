from flask import current_app

from application import redis_conn


# # 将用户登陆信息存储到redis,以便后续登出操作
# def save_user_info_to_redis(user_id, token):
#     user_login_key = "user_login_" + str(user_id)
#     pipline = redis_conn.pipeline(True)
#     pipline.set(user_login_key, token)
#     pipline.execute()


class User_status_info:

    def __init__(self, user_id):
        self.user_id = user_id
        self.user_login_key = "online_users"


    #使用位图方式存储用户登陆状态
    def save_user_info_to_redis(self):
        try:
            pipline = redis_conn.pipline(True)
            pipline.setbit(self.user_login_key, str(self.user_id), 1)
            pipline.execute()
        except Exception as e:
            current_app.logger.error("save_user_info_to_redis is failed,reason is %s" %e)


    #判断用户是否在线
    def get_user_is_login(self):
        try:
            pipline = redis_conn.pipline(True)
            pipline.getbit(self.user_login_key, str(self.user_id))
            status = pipline.execute()
            if int(status) == 1:
                return True
            else:
                return False
        except Exception as e:
            current_app.logger.error("get_user_is_login is failed,reason is %s" %e)


    #判断用户在线总数:
    @staticmethod
    def get_all_user_online(user_login_key = "online_users"):
        try:
            pipline = redis_conn.pipline(True)
            pipline.bitcount(user_login_key)
            all_count = pipline.execute()
            return all_count
        except Exception as e:
            current_app.logger.error("get_all_user_online is failed,reason is %s" %e)


    #用户登出时操作
    def delete_user_info(self):
        try:
            pipline = redis_conn.pipline(True)
            pipline.setbit(self.user_login_key, str(self.user_id), 0)
            pipline.execute()
        except Exception as e:
            current_app.logger.error("delete_user_info is failed,reason is %s" %e)

