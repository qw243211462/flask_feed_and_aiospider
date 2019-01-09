import json
from flask.views import MethodView
from app.search.utils import crawl
from flask import jsonify, request, g, current_app
from app.response_code import RET
from app.user.utils.check_in_user_status import login_required
from app.search.utils.db_handle import save_search_history_to_redis, get_search_history_from_redis, limit_user_visit
import logging

logger = logging.getLogger(__name__)


#搜索接口
class Search_api(MethodView):

    def get(self):
        return jsonify(re_code = RET.METHODNOTALLOWERR, msg = '请求类型不正确，需要post方法')

    @login_required
    def post(self):
        target_name = request.json.get("target_name")
        target_type = request.json.get("target_type")
        '''
            TODO 用户输入为空，重定向
        '''
        # if not all[target_name]:
        #     return jsonify(re_code=RET.NODATA, msg="用户没有输入")
        user_id = g.user_id
        #限制用户在一分钟内使用三次搜索功能
        visit_limit = limit_user_visit(user_id)
        if visit_limit == True:
            if target_type == "image":
                save_search_history_to_redis(user_id, target_name)
                result = crawl.get_result_url(target_name, target_type)
                count = [i for i in range(len(result))]
                json_result = json.dumps(dict(zip(count, result)))
                if result:
                    current_app.info("user %s get search info s success, result is %s", user_id, target_name)
                    return jsonify(re_code = RET.OK, result_url = json_result)
                else:
                    current_app.error("user %s get search info is failed, target_name is %s", user_id, target_name)
                    return jsonify(re_code = RET.NODATA, msg = "爬虫没有获取结果")
            elif target_type == "text":
                save_search_history_to_redis(user_id, target_name)
                result = crawl.get_result_url(target_name, target_type)
                json_result = json.dumps(result)
                if json_result:
                    current_app.info("user %s get search info s success, result is %s", user_id, target_name)
                    return jsonify(re_code = RET.OK, text_result = json_result)
                else:
                    current_app.error("user %s get search info is failed, target_name is %s", user_id, target_name)
                    return jsonify(re_code = RET.NODATA, msg = "爬虫没有获取结果")
        else:
            return jsonify(msg = "一分钟内最多访问三次")

#搜索历史接口
class Search_history_api(MethodView):

    def get(self):
        return jsonify(re_code = RET.METHODNOTALLOWERR, msg = '请求类型不正确，需要post方法')

    @login_required
    def post(self):
        prefix = request.json.get("prefix")
        user_id = g.user_id
        search_history = get_search_history_from_redis(user_id, prefix)
        logger.info("****************")
        if search_history:
            return jsonify(history = search_history)



