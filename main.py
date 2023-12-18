import asyncio
import json
import os
import random
from datetime import datetime
from urllib import parse

import httpx
from dotenv import find_dotenv, load_dotenv

USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; "
    "SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; "
    "SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; "
    "Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; "
    "Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; "
    ".NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; "
    "Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; "
    ".NET CLR 3.5.30729; .NET CLR 3.0.30729; "
    ".NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; "
    "Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; "
    "InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) "
    "AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) "
    "Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ "
    "(KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; "
    "rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) "
    "Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) "
    "Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) "
    "Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 "
    "(KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) "
    "AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) "
    "Presto/2.9.168 Version/11.52"
]
TIMEOUT = 5


class Action:
    def __init__(self):
        load_dotenv(find_dotenv(), override=True)
        # ServerChan secret key
        self.secret = os.environ.get('SECRET', '')
        # qywx config info
        self.corpid = os.environ.get('CORPID', '')
        self.agentid = os.environ.get('AGENTID', '')
        self.thumbmediaid = os.environ.get('THUMBMEDIAID', '')
        self.corpsecret = os.environ.get('CORPSECRET', '')

        self.contents = []
        self.res = False
        self.task_list = []

    async def qywx(self):
        """ 企业微信推送 """
        dt = datetime.now()
        date = dt.strftime('%Y-%m-%d')
        time = dt.strftime('%H:%M:%S')
        url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}'
        try:
            resp = await self.client.get(url)
            access_token = resp.json()['access_token']
            send_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
            try:
                data = {
                    'touser': f'@all',
                    'agentid': self.agentid,
                    'msgtype': 'mpnews',
                    'mpnews': {
                        'articles': [{
                            'title': f'热搜榜 - {date}',
                            'thumb_media_id': self.thumbmediaid,
                            'author': 'Tonyz',
                            'digest': f'{time} - 每日热搜推送',
                            'content': f'{"".join(self.contents)}'
                        }
                        ]
                    }
                }
                res = await self.client.post(send_url, data=json.dumps(data), timeout=TIMEOUT)
                print(res.json())

            except Exception as e:
                print(f'something error occurred, message: {e}')

        except Exception as e:
            print(f'something error occurred, message: {e}')

        


    async def servechan(self):
        """ Server酱推送 """
        dt = datetime.now()
        time = dt.strftime('%Y-%m-%d')
        url = f'https://sc.ftqq.com/{self.secret}.send'
        data = {
            'text': f'资讯热文推送-{time}',
            'desp': f'{"".join(self.contents)}'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        try:
            resp = await self.client.post(url, headers=headers,
                                          data=parse.urlencode(data), timeout=TIMEOUT)
            self.res = resp.json()['errno'] == 0
            print(resp.text)
        except Exception as e:
            print(f'something error occurred, message: {e}')

    async def get_v2ex_hot_topics(self):
        url = 'https://www.v2ex.com/api/topics/hot.json'
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        try:
            resp = await self.client.get(url, headers=headers, timeout=TIMEOUT)
            self.contents.append(f'<h2> v2ex热门主题 </h2>')
            for item in resp.json()[:10]:
                detail_url = item['url']
                title = item['title']
                content = f'<ul><li> <a href={detail_url}>{title}</a> </li></ul>'
                self.contents.append(content)
        except Exception as e:
            print(f'something error occurred, message: {e}')

    async def get_zhihu_hot_topics(self):
        url = "https://bicido.com/api/news/?type_id=4"
        headers = {
            'Referer': 'https://bicido.com/',
            'Host': 'bicido.com',
            'User-Agent': random.choice(USER_AGENTS)
        }
        try:
            resp = await self.client.get(url, headers=headers, timeout=TIMEOUT)
            self.contents.append(f'\n 知乎热搜 \n\n')
            for item in resp.json()[:10]:
                detail_url = item['source_url']
                title = item['title']
                # content = f'- [{title}]({detail_url})\n'
                content = f'<ul><li> <a href={detail_url}>{title}</a> </li></ul>'
                self.contents.append(content)
        except Exception as e:
            print(f'something error occurred, message: {e}')

    async def get_weibo_hot_search(self):
        url = "https://bicido.com/api/news/?type_id=1"
        headers = {
            'Referer': 'https://bicido.com/',
            'Host': 'bicido.com',
            'User-Agent': random.choice(USER_AGENTS)
        }
        try:
            resp = await self.client.get(url, headers=headers, timeout=TIMEOUT)
            self.contents.append(f'\n 微博热搜榜\n\n')
            for item in resp.json()[:10]:
                detail_url = item['source_url']
                title = item['title']
                content = f'<ul><li> <a href={detail_url}>{title}</a> </li></ul>'
                # content = f'- [{title}]({detail_url})\n'
                self.contents.append(content)
        except Exception as e:
            print(f'something error occurred, message: {e}')

    async def get_baidu_hot_topics(self):
        url = "https://news.bicido.com/api/news/?type_id=37"
        headers = {
            'Referer': 'https://bicido.com/',
            'Host': 'bicido.com',
            'User-Agent': random.choice(USER_AGENTS)
        }
        try:
            resp = await self.client.get(url, headers=headers, timeout=TIMEOUT)
            self.contents.append(f'\n 百度|今日热点\n\n')
            for item in resp.json()[:10]:
                detail_url = item['source_url']
                title = item['title']
                # content = f'- [{title}]({detail_url})\n'
                content = f'<ul><li> <a href={detail_url}>{title}</a> </li></ul>'
                self.contents.append(content)
        except Exception as e:
            print(f'something error occurred, message: {e}')

    async def get_freebuf_hot_topics(self):
        url = "https://news.bicido.com/api/news/?type_id=147"
        headers = {
            'Referer': 'https://bicido.com/',
            'Host': 'bicido.com',
            'User-Agent': random.choice(USER_AGENTS)
        }
        try:
            resp = await self.client.get(url, headers=headers, timeout=TIMEOUT)
            self.contents.append(f'\n FreeBuf\n\n')
            for item in resp.json()[:10]:
                detail_url = item['source_url']
                title = item['title']
                # content = f'- [{title}]({detail_url})\n'
                content = f'<ul><li> <a href={detail_url}>{title}</a> </li></ul>'
                self.contents.append(content)
        except Exception as e:
            print(f'something error occurred, message: {e}')

    async def get_xzAliyun_hot_topics(self):
        url = "https://news.bicido.com/api/news/?type_id=115"
        headers = {
            'Referer': 'https://bicido.com/',
            'Host': 'bicido.com',
            'User-Agent': random.choice(USER_AGENTS)
        }
        try:
            resp = await self.client.get(url, headers=headers, timeout=TIMEOUT)
            self.contents.append(f'\n 先知社区\n\n')
            for item in resp.json()[:10]:
                detail_url = item['source_url']
                title = item['title']
                # content = f'- [{title}]({detail_url})\n'
                content = f'<ul><li> <a href={detail_url}>{title}</a> </li></ul>'
                self.contents.append(content)
        except Exception as e:
            print(f'something error occurred, message: {e}')

    async def get_seebug_hot_topics(self):
        url = "https://news.bicido.com/api/news/?type_id=115"
        headers = {
            'Referer': 'https://bicido.com/',
            'Host': 'bicido.com',
            'User-Agent': random.choice(USER_AGENTS)
        }
        try:
            resp = await self.client.get(url, headers=headers, timeout=TIMEOUT)
            self.contents.append(f'\n 知道创宇|洞悉漏洞\n\n')
            for item in resp.json()[:10]:
                detail_url = item['source_url']
                title = item['title']
                # content = f'- [{title}]({detail_url})\n'
                content = f'<ul><li> <a href={detail_url}>{title}</a> </li></ul>'
                self.contents.append(content)
        except Exception as e:
            print(f'something error occurred, message: {e}')

    async def run(self):
        """主方法"""
        async with httpx.AsyncClient() as client:
            self.client = client
            self.task_list.append(asyncio.create_task(self.get_v2ex_hot_topics()))
            self.task_list.append(asyncio.create_task(self.get_zhihu_hot_topics()))
            self.task_list.append(asyncio.create_task(self.get_weibo_hot_search()))
            self.task_list.append(asyncio.create_task(self.get_baidu_hot_topics()))
            self.task_list.append(asyncio.create_task(self.get_freebuf_hot_topics()))
            self.task_list.append(asyncio.create_task(self.get_xzAliyun_hot_topics()))
            self.task_list.append(asyncio.create_task(self.get_seebug_hot_topics()))

            await asyncio.gather(*self.task_list)

            # 自行修改对应的发送方式
            # await self.servechan()
            await self.qywx()

            # print(f'{"".join(self.contents)}')


if __name__ == '__main__':
    action = Action()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(action.run())
