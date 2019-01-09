#启动celery入口

from application import creat_app,celery

app = creat_app()
# 推送app的程序上下文环境
app.app_context().push()

#启动命令celery worker -A celery_worker.celery -l INFO
#指定队列启动celery worker -A celery_worker.celery -l INFO -Q for_email


