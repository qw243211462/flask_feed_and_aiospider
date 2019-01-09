

#aiohttp中文文档
#https://hubertroy.gitbooks.io/aiohttp-chinese-documentation/content/aiohttp%E6%96%87%E6%A1%A3/ClientUsage.html#%E4%BD%BF%E7%94%A8WebSockets

import re
import asyncio
import aiohttp
import time
import urllib
import async_timeout
from lxml import html
from flask import current_app

now = lambda :time.time()
result_url = []
result_content = {}
# asyncio.Semaphore(),限制同时运行协程数量
sem = asyncio.Semaphore(20)


#定义一个下载网页定位异步任务
async def download_html(url, callback = None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    with (await sem):
        async with aiohttp.ClientSession() as session:
            # 设置超时时间
            with async_timeout.timeout(10):
                # 爬虫开始获取网站
                try:
                    async with session.get(url, headers=headers) as resp:
                        assert resp.status == 200
                        body = await resp.text()
                        if callback == get_img_url:
                            callback(body)
                        if callback == get_text_content:
                            callback(body)
                        else:
                            return await resp.text()
                        # 关闭请求
                        #session.close()
                except Exception as err:
                    #打印日志
                    print('Error for url {}: {}'.format(url, err))

#定义规则去获取网站中所需要的内容
def get_img_url(content):
    etree = html.etree
    htmlDiv = etree.HTML(content)
    img_url = htmlDiv.xpath("//div[@class='img']/a/img/@src")
    result_url.extend(list(img_url))

    #正则匹配方式，速度稍慢
    # pattern = '<img class="dt" src="(.*?)"'
    # urls = re.findall(pattern, content)

#http://www.chuanxincao.net/
def get_text_content(content):
    etree = html.etree
    htmlDiv = etree.HTML(content)
    result_content["image"] = htmlDiv.xpath("//*[@id='bg_theme']/div[1]/div/div[2]/div/div[1]/div[1]/a/img/@src")[
        0].strip()
    result_content["name"] = htmlDiv.xpath("//div[@class='c_subject']/a/text()")[0].strip()
    result_content["sex"] = htmlDiv.xpath("//span[@class='color444']/text()")[0].strip()
    result_content["based_cartoon"] = htmlDiv.xpath("//div[@class='mt10']//span[@class='color444']/a/text()")[0].strip()
    result_content["content"] = \
    htmlDiv.xpath("//*[@id='bg_theme']/div[1]/div/div[2]/div/div[1]/div[2]/div[2]/div[4]/span[2]/text()")[0].strip()


#主函数，获取所需要的url结果/
def get_result_url(target_name, type):#type=image.图片 type=text,文字
    if type == "image":
        start = now()
        #需要爬取的页数
        page_num = 2
        # 起始页面
        page_url_base = 'http://www.ecyss.com/search?word=' + str(urllib.parse.quote(str(target_name))) + str("&p=")
        #page_url_base = 'http://www.ecyss.com/search?word=%E6%9F%AF%E5%8D%97&p='
        # 列表页面的列表
        page_urls = [page_url_base + str(i + 1) for i in range(page_num)]
        loop = asyncio.get_event_loop() #创建事件循环

        # 协程任务，获得对应图片的url
        # asyncio.ensure_future(coroutine)创建task
        tasks = [download_html(url, callback = get_img_url) for url in page_urls]
        # 将协程程序注册到任务循环中，然后在事件循环中执行协程程序
        loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()
        current_app.info('使用aiohttp,总共耗时：%s, url is %s,',(now() - start),page_urls)
        return result_url
    elif type == "text":
        start = now()
        page_url_base = 'http://www.chuanxincao.net/search/?keyword=' + str(target_name.encode("unicode_escape").decode().replace('\\','%'))
        loop = asyncio.get_event_loop() #创建事件循环
        tasks = [download_html(page_url_base, callback = get_text_content)]
        loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()
        print('使用aiohttp,总共耗时：%s' % (now() - start))
        return result_content


# get_result_url()
# import json
# print(result_url)
# count = [i for i in range(len(result_url) - 1)]
# json_result = json.dumps(dict(zip(count,result_url)))
# print(json_result)

