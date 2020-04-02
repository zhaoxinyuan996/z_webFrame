import os
import json
import pytz
from datetime import datetime, timezone, timedelta

from backstage import settings
from backstage.settings import DateTime
from backstage.libs.static_file import GetStaticFile
from backstage.libs.static_data import responseStatusMessage, currentMessage, contentTypeDic, wkDayDic


g = None

if settings.preloadingStatic:
    g = GetStaticFile()

staticPath = settings.staticPath


class httpRequest():
    def __init__(self, data, **kwargs):
        self.data = data
        self.__dict__.update(kwargs.items())
        # print(data)
        try:
            self.parse_http_request()
        except:
            print('parse error')

    def __getattr__(self, item):
        return None

    def __getitem__(self, item):
        return self.__dict__[item]

    def get(self, key, default = None):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return default

    def parse_http_request(self):
        self.part1, self.part2 = self.data.decode().split('\r\n', 1)
        self.httpMethod, self.httpUrl, self.httpVersion = self.part1.split()
        for i in self.part2.split('\r\n'):
            try:
                self.__dict__.update(json.loads(i))
            except:
                if ':' in i:
                    self.__dict__[i.split(':')[0]] = i.split(':')[1]

        del self.data, self.part1, self.part2

class CustomHttpResponse():
    # type length
    currentMessage_part1 = \
        b'HTTP/1.1 200 OK\n'\
        b'Content-Type: %s; charset=UTF-8\n'\
        b'Content-Encoding: UTF-8\n'\
        b'Content-Length: %s\n'\
        b'Server: z_webFrame\n'
    currentMessage_part2 = \
        b'\n'\
        b'%s'

    @classmethod
    # 通过字典添加header信息, 2个占位符
    def add(cls, dic):
        tmp = cls.currentMessage_part1
        for i in dic:
            if i:
                tmp += i.__str__().encode() + b':' + dic[i].__str__().encode() + b'\n'
        return tmp + cls.currentMessage_part2

class agreementDateTime():
    def __init__(self, format):
        if format != 'GMT':
            raise KeyError('datatimeMode设置错误')
    @ staticmethod
    def get_date_time():
        'Sun, 06 Nov 1994 08:49:37 GMT'
        t = datetime.now()
        t.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(DateTime.zone))
        t += timedelta(hours=DateTime.adjustmentHour, minutes=DateTime.adjustmentMinute)
        t = t.strftime('%a, %d %b %Y %H:%M:%S GMT')
        return t

    @staticmethod
    def last_file_time(mtime):
        t = datetime.fromtimestamp(mtime)
        t = t.strftime('%a, %d %b %Y %H:%M:%S GMT')
        return t



def httpResponse_404():
    return 404, responseStatusMessage % (b'404', b'URL NOT FOUNT', b'404 not found')

def httpResponse_500():
    return 500, responseStatusMessage % (b'500', b'SERVER ERROR', b'500 server err')

# 页面
def httpRender(fileName):

    htmlPath = os.path.join(os.getcwd().split('z_webFrame')[0], 'z_webFrame', staticPath, fileName)
    if g:
        html, htmlSize, mtime = g.fileDict[htmlPath]
    else:
        with open(htmlPath, 'rb') as f:
            html = f.read()
            htmlSize = len(html)
    return 200, currentMessage % (b'text/html', htmlSize.__str__().encode(), html)

# 接口
def httpResponse(data):
    if not isinstance(data, bytes):
        data = data.encode()
    dataSize = len(data)
    return 200, currentMessage % (b'text/plain', dataSize.__str__().encode(), data)

# 静态文件
def get_static_file(fileName):

    htmlPath = os.path.join(os.getcwd().split('z_webFrame')[0], 'z_webFrame', staticPath) + os.path.normcase(fileName)
    if g:
        file, fileSize, mStrftime = g.fileDict[htmlPath]
    else:
        mStrftime = os.path.getmtime(htmlPath)
        with open(htmlPath, 'rb') as f:
            file = f.read()
            fileSize = len(file)
    suffix = fileName.rsplit('.', 1)[-1]

    if suffix in contentTypeDic:
        # return 200, currentMessage % (contentTypeDic[suffix], fileSize.__str__().encode(), file)
        return 200, CustomHttpResponse.add({'last-modified': mStrftime}) % (contentTypeDic[suffix], fileSize.__str__().encode(), file)
    return 200, currentMessage % (b'*/*', fileSize.__str__().encode(), file)


if __name__ == '__main__':
    pass

