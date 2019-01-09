import redis
from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from celery import Celery
from config import APP_ENV, config
from logs.logs import setupLogging

db = SQLAlchemy()
mail = Mail()
redis_conn = None
celery = Celery(__name__,
                broker = config["testing"].CELERY_BROKER_URL,
                backend = config["testing"].CELERY_RESULT_BACKEND,
                include=['app.mq.celery_tasks.tasks',
                         'app.user.celery_tasks.task_send_email',
                         ])


def creat_app():
    '''
    工厂函数，创建APP实例
    :return app实例
    '''
    setupLogging(config[APP_ENV].LOGGING_LEVEL)

    app = Flask(__name__)
    app.config.from_object(config[APP_ENV])
    #config[APP_ENV].init_app(app)


    CORS(app, resources=r'/*')

    #创建Redis数据库连接对象
    global redis_conn
    redis_conn = redis.StrictRedis(host=config[APP_ENV].REDIS_HOST, port=config[APP_ENV].REDIS_PORT)

    db.init_app(app)
    mail.init_app(app)
    celery.conf.update(config)


    # import blueprints
    from app.user.views import user_app
    from app.search.views import search_app
    from app.mq.views import mq_app

    # register blueprints
    app.register_blueprint(user_app)
    app.register_blueprint(search_app)
    app.register_blueprint(mq_app)

    app.debug = True
    return app


