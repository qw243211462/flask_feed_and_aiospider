import re
import os
import time
import random

from flask.views import MethodView
from flask import current_app, jsonify, request, g
from werkzeug.utils import secure_filename

from app.user.models import User
from app.user.utils.check_in_user_status import login_required
from application import redis_conn
from application import db

from app.response_code import RET
from app.user.celery_tasks.task_send_email import send_mail
from app.user.utils.common import User_status_info

#注册发送邮件接口
class Send_email_api(MethodView):

    def get(self):
        return jsonify(re_code = RET.METHODNOTALLOWERR, msg = '请求类型不正确，需要post方法')

    def post(self):
        '''发送邮箱验证码'''
        nickname = request.json.get('nickname')
        email = request.json.get('email')
        if not all([email, nickname]):
            return jsonify(re_code=RET.PARAMERR, msg='请填写完整的注册信息')
        if not re.match(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$', email):
            return jsonify(RET.PARAMERR, msg='请填写正确的邮箱')

        # 判断用户是否注册
        try:
            user_email = User.query.filter(User.email == email).first()
            user_nickname = User.query.filter(User.nickname == nickname).first()
        except Exception as e:
            current_app.logger.info(e)
            return jsonify(re_code=RET.DBERR, msg='查询数据库错误')
            # 用户存在,提示该账户已被注册
        if user_email or user_nickname:
            return jsonify(re_code=RET.DATAEXIST, msg='该用户已被注册')

        # 生成邮箱验证码
        email_code = '%06d' % random.randint(0, 99999)
        current_app.logger.info('邮箱验证码为: ' + email_code)
        try:
            redis_conn.set('EMAILCODE:' + email, email_code, 1800)  # half-hour = 1800有效期
        except Exception as e:
            current_app.logger.info(e)
            return jsonify(re_code=RET.DBERR, msg='存储邮箱验证码失败')

        # 异步发送邮件
        send_mail.delay(
            to = email,
            nickname = nickname,
            mailcode = email_code,
        )

        return jsonify(re_code=RET.OK, msg='验证码发送成功')


#注册接口
class Register_api(MethodView):

    def get(self):
        pass

    def post(self):
        '''用户注册接口
            :return 返回注册信息{'re_code': '0', 'msg': '注册成功'}
        '''
        nickname = request.json.get('nickname')
        email = request.json.get('email')
        password = request.json.get('password')
        mailcode_client = request.json.get('mailcode')

        if not all([email, nickname, password, mailcode_client]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')

        # 从Redis中获取此邮箱对应的验证码,与前端传来的数据校验
        try:
            mailcode_server = redis_conn.get('EMAILCODE:' + email).decode()
        except Exception as e:
            current_app.logger.info(e)
            return jsonify(re_code=RET.DBERR, msg='查询邮箱验证码失败')
        if mailcode_server != mailcode_client:
            current_app.logger.info(mailcode_server)
            return jsonify(re_code=RET.PARAMERR, msg='邮箱验证码错误')

        user = User()
        user.email = email
        user.nickname = nickname
        user.password = password  # 利用user model中的类属性方法加密用户的密码并存入数据库
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            current_app.logger.info(e)
            db.session.rollback()
            return jsonify(re_code=RET.DBERR, msg='注册失败')
        # 6.响应结果
        return jsonify(re_code=RET.OK, msg='注册成功')

#登陆接口
class Login_api(MethodView):

    def get(self):
        pass

    def post(self):
        '''登录
            TODO: 添加图片验证
            :return 返回响应,保持登录状态
        '''
        email = request.json.get('email')
        password = request.json.get('password')
        if not all([email, password]):
            return jsonify(re_code=RET.PARAMERR, msg='参数不完整')
        try:
            user = User.query.filter(User.email == email).first()
        except Exception as e:
            current_app.logger.info(e)
            return jsonify(re_code=RET.DBERR, msg='查询用户失败')
        if not user:
            return jsonify(re_code=RET.NODATA, msg='用户不存在', user=user)
        if not user.verify_password(password):
            return jsonify(re_code=RET.PARAMERR, msg='帐户名或密码错误')
        # 更新最后一次登录时间
        user.update_last_seen()
        token = user.generate_user_token()
        #将用户登陆信息存储到redis
        user_id = user.id
        user_status_info = User_status_info(user_id)
        user_status_info.save_user_info_to_redis()
        #用户登陆ip
        ip = request.remote_addr
        return jsonify(re_code=RET.OK, msg='登录成功', token=token, ip = ip)


#退出登陆接口
@login_required
class Login_out_api(MethodView):

    def get(self):
        pass

    def post(self):
        user_id = g.user_id
        user_status_info = User_status_info(user_id)
        if not user_id:
            return jsonify(msg = "该用户没有登陆")
        user_status_info.delete_user_info()
        return jsonify(msg = "用户退出登陆")


#上传头像
class Upload_user_head_portrait(MethodView):

    def get(self):
        pass

    def post(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        file_dir = os.path.join(basedir, current_app.config['UPLOAD_FOLDER'])
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        f = request.files['myfile'] # 从表单的file字段获取文件，myfile为该表单的name值
        if f and self.allowed_file(f.filename):  # 判断是否是允许上传的文件类型
            fname = secure_filename(f.filename)
            #print(fname)
            ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
            '''登录
                TODO: 根据用户id生成url
                :return 上传图片的url
            '''

            unix_time = int(time.time())
            new_filename = str(unix_time) + '.' + ext  # 修改了上传的文件名
            f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录

            return jsonify({"errno": 0, "errmsg": "上传成功", "token": 1})
        else:
            return jsonify({"errno": 1001, "errmsg": "上传失败"})

    @staticmethod
    # 用于判断文件后缀
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in current_app.config["ALLOWED_EXTENSIONS"]


#显示当前登陆的用户数量
class Count_user_login(MethodView):

    def get(self):
        pass

    def post(self):

        count = User_status_info.get_all_user_online()

        return jsonify(re_code = RET.OK, msg = "获取在线用户数量成功", count = count)


class Test_login_require_api(MethodView):

    def get(self):
        pass

    @login_required
    def post(self):
        # token = request.json.get('token')
        # user = User.verify_user_token(token)
        # print("___________",type(user))
        return str(g.user_id)

