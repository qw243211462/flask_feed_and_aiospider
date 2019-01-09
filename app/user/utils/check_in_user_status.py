import datetime, time
import jwt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

import  config

from flask import request, make_response, jsonify, g, current_app
from flask_httpauth import HTTPBasicAuth
from app.user.models import User
from functools import wraps
from app.response_code import RET

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token, password):
    if request.path == '/login':
        user = User.query.filter_by(email=email_or_token).first()
        if not user or not user.verify_password(password):
            return False
    else:
        user = User.verify_user_token(email_or_token)
        if not user:
            return False

    g.user = user
    return True

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.email})



def login_required(view_func):
    """登录校验装饰器
    :param func:函数名
    :return: 闭包函数名
    """
    # 装饰器装饰一个函数时，会修改该函数的__name__属性
    # 如果希望装饰器装饰之后的函数，依然保留原始的名字和说明文档,就需要使用wraps装饰器，装饰内存函数
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        if not 'token' in request.headers:
            # 用户未登录
            return jsonify(re_code=RET.SESSIONERR,msg='用户未登录')
        token = request.headers['token'].encode('utf-8')
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_info = s.loads(token)
        except SignatureExpired:
            # valid token, but expired
            return jsonify(re_code = RET.TOKENEXPIRE, msg = 'token过期')
        except BadSignature:
            # invalid token
            return jsonify(re_code = RET.TOKENVALID, msg = 'token无效')
        else:
            user_id = user_info['id']
            # 用户已登录使用g变量保存住user_id，方便被装饰的函数中调用g变量获取user_id。
            g.user_id = user_id
            print("___________", user_id)
            return view_func(*args, **kwargs)
    return wrapper

# #登陆验证装饰器
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not 'token' in request.headers:
#             return jsonify(re_code=RET.SESSIONERR,msg='用户未登录')
#         t=request.headers['token'].encode('utf-8')
#         s=Serializer(current_app.config['SECRET_KEY'])
#         try:
#             data=s.loads(t)
#         except:
#             abort(401)
#         uid=data.get('confirm')
#         return f(uid,*args,**kwargs)
#     return decorated_function()


class Auth():
    '''
    Auth_JWT
    '''

    #encode_auth_token方法用来生成认证Token
    @staticmethod
    def encode_auth_token(user_id, login_time):
        '''生成认证Token
        :param user_id: int
        :param login_time: int(timestamp)
        :return: string
        '''
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=10),
                'iat': datetime.datetime.utcnow(),
                'iss': 'ken',
                'data': {
                    'id': user_id,
                    'login_time': login_time
                }
            }
            return jwt.encode(
                payload,
                config.SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    #decode_auth_token方法用于Token验证
    @staticmethod
    def decode_auth_token(auth_token):
        '''
        验证Token
        :param auth_token:
        :return: integer|string
        '''
        try:
            # payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'), leeway=datetime.timedelta(seconds=10))
            # 取消过期时间验证
            payload = jwt.decode(auth_token, config.SECRET_KEY, options={'verify_exp': False})
            if ('data' in payload and 'id' in payload['data']):
                return payload
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return 'Token过期'
        except jwt.InvalidTokenError:
            return '无效Token'

    #authenticate方法用于用户登录验证
    def authenticate(self, username, password):
        '''
        用户登录，登录成功返回token，写将登录时间写入数据库；登录失败返回失败原因
        :param password:
        :return: json
        '''
        userInfo = User.query.filter_by(username=username).first()
        if (userInfo is None):
            return jsonify(falseReturn('', '找不到用户'))
        else:
            if (User.check_password(User, userInfo.password, password)):
                login_time = int(time.time())
                userInfo.login_time = login_time
                User.update(User)
                token = self.encode_auth_token(userInfo.id, login_time)
                return jsonify(trueReturn(token.decode(), '登录成功'))
            else:
                return jsonify(falseReturn('', '密码不正确'))
                #abort(400, message='Password is incorrect.')

    # #identify方法用于用户鉴权
    # def identify(self, request):
    #     '''
    #     用户鉴权
    #     :return: list
    #     '''
    #     auth_header = request.headers.get('Authorization')
    #     if (auth_header):
    #         auth_tokenArr = auth_header.split(" ")
    #         if (not auth_tokenArr or auth_tokenArr[0] != 'JWT' or len(auth_tokenArr) != 2):
    #             result = falseReturn('', '请传递正确的验证头信息')
    #         else:
    #             auth_token = auth_tokenArr[1]
    #             payload = self.decode_auth_token(auth_token)
    #             if not isinstance(payload, str):
    #                 user = User.get(User, payload['data']['id'])
    #                 if (user is None):
    #                     result = falseReturn('', '找不到该用户信息')
    #                 else:
    #                     if (user.login_time == payload['data']['login_time']):
    #                         result = trueReturn(user.id, '请求成功')
    #                     else:
    #                         result = falseReturn('', 'Token已更改，请重新登录获取')
    #             else:
    #                 result = falseReturn('', payload)
    #     else:
    #         result = falseReturn('', '没有提供认证token')
    #     return result

def trueReturn(data, msg):
    return {
        "status": True,
        "data": data,
        "msg": msg
    }


def falseReturn(data, msg):
    return {
        "status": False,
        "id": data['id'],
        "email": data['email']
    }


