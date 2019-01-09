import logging
from kombu import Queue, Exchange
from redis import StrictRedis

APP_ENV = "testing"

class BaseConfig:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    #是否开启跟踪
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = "hello"
    '''
    根据业务和场景添加其他相关配置
    '''

    #配置Redis数据库
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_DB = 1
    # 配置session数据存储到redis数据库
    SESSION_TYPE = 'redis'
    # 指定存储session数据的redis的位置
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT,db=REDIS_DB)
    # 开启session数据的签名，意思是让session数据不以明文形式存储
    SESSION_USE_SIGNER = True
    # 设置session的会话的超时时长 ：一天,全局指定
    PERMANENT_SESSION_LIFETIME = 3600 * 24



    # QQ邮箱配置
    MAIL_DEBUG = True  # 开启debug，便于调试看信息
    MAIL_SUPPRESS_SEND = False  # 发送邮件，为True则不发送
    MAIL_SERVER = 'smtp.qq.com'  # 邮箱服务器
    MAIL_PORT = 465  # 端口
    MAIL_USE_SSL = True  # 重要，qq邮箱需要使用SSL
    MAIL_USE_TLS = False  # 不需要使用TLS
    MAIL_USERNAME = '243211462@qq.com'  # 填邮箱
    MAIL_PASSWORD = 'eomejkcqhfyjbihj'  # 填授权码
    FLASK_MAIL_SENDER = '<243211462@qq.com>'  # 邮件发送方
    FLASK_MAIL_SUBJECT_PREFIX = '[带哥好]'  # 邮件标题
    # MAIL_DEFAULT_SENDER = 'xxx@qq.com'  # 填邮箱，默认发送者


    #上传头像地址
    UPLOAD_FOLDER = 'upload'
    #允许上传头像的类型
    ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'xls', 'JPG', 'PNG', 'xlsx', 'gif', 'GIF'])


    #Celery配置
    #设置本机rabbitmq为broken，生产环境注意更换
    CELERY_BROKER_URL = 'amqp://guest:guest@localhost//'

    # 注意，celery4版本后，CELERY_BROKER_URL改为BROKER_URL
    #BROKER_URL = 'amqp://username:passwd@host:port/虚拟主机名'
    # 指定结果的接受地址
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    # 指定任务序列化方式
    CELERY_TASK_SERIALIZER = 'json'
    # 指定结果序列化方式
    CELERY_RESULT_SERIALIZER = 'json'
    # 任务过期时间,celery任务执行结果的超时时间
    CELERY_TASK_RESULT_EXPIRES = 60 * 20
    # 指定任务接受的序列化类型.
    CELERY_ACCEPT_CONTENT = ["json"]
    # 任务发送完成是否需要确认，这一项对性能有一点影响
    CELERY_ACKS_LATE = True
    # 压缩方案选择，可以是zlib, bzip2，默认是发送没有压缩的数据
    CELERY_MESSAGE_COMPRESSION = 'zlib'
    # 规定完成任务的时间
    CELERYD_TASK_TIME_LIMIT = 5  # 在5s内完成任务，否则执行该任务的worker将被杀死，任务移交给父进程
    # celery worker的并发数，默认是服务器的内核数目,也是命令行-c参数指定的数目
    CELERYD_CONCURRENCY = 4
    # celery worker 每次去rabbitmq预取任务的数量
    CELERYD_PREFETCH_MULTIPLIER = 4
    # 每个worker执行了多少任务就会死掉，默认是无限的
    CELERYD_MAX_TASKS_PER_CHILD = 40
    # 设置默认的队列名称，如果一个消息不符合其他的队列就会放在默认队列里面，如果什么都不设置的话，数据都会发送到默认的队列中
    CELERY_DEFAULT_QUEUE = "default"
    #忽视异步队列执行后的结果
    CELERY_IGNORE_RESULT = True

    CELERY_IMPORTS = (
        'ZongHeSheJI.app.mq.celery_tasks.task_push_announce'
    )

    # 设置详细的队列
    CELERY_QUEUES = {
        Queue('default', exchange = Exchange('default'), routing_key='default'),
        Queue("for_email", exchange = Exchange("for_email"), routing_key="for_email"),
        Queue("for_user_push_message", exchange = Exchange("for_user_push_message"), routing_key="for_user_push_message"),
        Queue("for_system_message", exchange = Exchange("for_system_message"), routing_key = "for_system_message"),
        Queue("for_delete_user_message", exchange = Exchange("for_delete_user_message"), routing_key = "for_delete_user_message")
    }

    CELERY_ROUTES = {
        'app.user.celery_tasks.task_send_mail.send_email': {'queue': 'for_email', 'routing_key': 'for_email'},
        'app.mq.celery_tasks.tasks.push_message': {'queue': 'for_user_push_message', 'routing_key': 'for_user_push_message'},
        'app.mq.celery_tasks.tasks.save_system_message_to_redis':{'queue': 'for_system_message', 'routing_key': "for_system_message"},
        'app.mq.celery_tasks.tasks.delete_user_message': {'queue': 'for_delete_user_message', 'routing_key': 'for_delete_user_message'}
    }


class TestingConfig(BaseConfig):
    DEBUG = True
    LOGGING_LEVEL = logging.DEBUG
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:qw13198321328@127.0.0.1:3306/test"

class DevelopmentConfig(BaseConfig):
    DEBUG = False
    LOGGING_LEVEL = logging.WARNING
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:qw13198321328@127.0.0.1:3306/test"

config = {
    "testing": TestingConfig,
    "devolopment": DevelopmentConfig,
}
