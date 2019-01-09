from flask import Blueprint

from app.user.api import Send_email_api, \
                        Register_api, Login_api, \
                        Test_login_require_api,\
                        Upload_user_head_portrait,\
                        Count_user_login

user_app = Blueprint('user_api', __name__)

#发送邮件接口
email_view = Send_email_api.as_view('email_api')
user_app.add_url_rule('/emailcode', view_func = email_view, methods = ['POST',])

#注册接口
register_view = Register_api.as_view('register_api')
user_app.add_url_rule('/register', view_func = register_view, methods = ['POST',])

#登陆接口
login_view = Login_api.as_view('login_api')
user_app.add_url_rule('/login', view_func = login_view, methods = ['POST',])

#头像上传接口
upload_user_head_portrait = Upload_user_head_portrait.as_view("upload_api")
user_app.add_url_rule('/upload', view_func = upload_user_head_portrait, methods = ['POST',])

count_user_login = Count_user_login.as_view('count_online_user')
user_app.add_url_rule('/count_online_user', view_func = count_user_login, methods = ['POST',])

#测试login_require接口
login_require_view = Test_login_require_api.as_view('test_login_require_api')
user_app.add_url_rule('/test_login_require', view_func = login_require_view, methods = ['POST'])


