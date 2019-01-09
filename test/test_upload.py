# from application import creat_app
# from flask import render_template
from app.mq.models import User_friend_follow
from config import config
from datetime import datetime

# app = creat_app()
#
# # 用于测试上传，稍后用到
# @app.route('/test/upload')
# def upload_test():
#     return render_template('upload.html')

#coding=utf-8
import urllib
a='佐助'
aa = "http://www.chuanxincao.net/search/?keyword=%u4F50%u52A9"
print(a.encode("unicode_escape").decode().replace('\\','%'))

