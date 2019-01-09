from flask import Blueprint


from app.search.api import Search_api, Search_history_api

search_app = Blueprint('search_api', __name__)

#搜索接口
search_view = Search_api.as_view('search_api')
search_app.add_url_rule('/search', view_func = search_view, methods = ['POST',])

#查询搜索历史接口
search_history_view = Search_history_api.as_view("search_history_api")
search_app.add_url_rule('/search/history', view_func = search_history_view, methods = ['POST',])