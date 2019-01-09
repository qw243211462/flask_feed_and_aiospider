from flask import Blueprint

from app.mq.api import Push_system_message, User_follow, Push_user_message, User_not_follow, Pull_notice, Pull_user_friendship

mq_app = Blueprint('mq_api', __name__)


#系统发送通知接口
pull_announce_view = Push_system_message.as_view('pull_announce_api')
mq_app.add_url_rule('/push_system_message', view_func = pull_announce_view, methods = ['POST',])

#添加好友接口
add_user_friendship_view = User_follow.as_view('add_user_friendship_api')
mq_app.add_url_rule('/add_friendship', view_func = add_user_friendship_view, methods = ['POST',])

#取消关注接口
delete_user_friendship = User_not_follow.as_view('delete_user_friednship_api')
mq_app.add_url_rule('/delete_friendship', view_func = delete_user_friendship, methods = ['POST',])

#用户发送动态接口
user_push_message = Push_user_message.as_view('push_message_api')
mq_app.add_url_rule('/push_user_message', view_func = user_push_message, methods = ['POST',])

#拉取通知接口
user_pull_message = Pull_notice.as_view('pull_message_api')
mq_app.add_url_rule('/pull_message', view_func = user_pull_message, methods = ['POST',])

#拉取用户好友接口
user_pull_friends = Pull_user_friendship.as_view('pull_friends_api')
mq_app.add_url_rule('/pull_friends', view_func = user_pull_friends, methods = ['POST',])