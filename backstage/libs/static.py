import os
import json
import pytz

from copy import deepcopy
from datetime import datetime, timedelta

from backstage import settings
from backstage.settings import DateTime, debug
from backstage.libs.static_file import GetStaticFile
from backstage.libs.static_data import responseStatusMessage, currentMessage, contentTypeDic

g = GetStaticFile()

staticPath = settings.staticPath


class httpRequest():
    def __init__(self, data, **kwargs):
        for k in kwargs:
            if k in self.__dict__:
                raise KeyError('key %s has been existed' % k)

        self.data = data
        self.__dict__.update(kwargs.items())
        try:
            self.parse_http_request()
        except Exception as e:
            print('parse error, %s' % e)

    def __getattr__(self, item):
        return None

    def __getitem__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            raise KeyError('httpRequest object has no Attribute “%s”' % item)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __iter__(self):
        for k in self.__dict__.keys():
            if not k.startswith('__'):
                yield k

    def get(self, key, default = None):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return default

    def parse_http_request(self):
        self.data = self.data.decode()

        if '\r\n' in self.data:
            self.data = self.data.replace('\r\n', '\n')

        self.part1, self.part2 = self.data.split('\n', 1)
        self.httpMethod, self.httpUrl, self.httpVersion = self.part1.split()
        for i in self.part2.split('\n'):
            if i:
                try:
                    self.__dict__.update(json.loads(i))
                except:
                    if ':' in i:
                        self.__dict__[i.split(':')[0]] = i.split(':')[1]


class BaseResponse():
    start = b'HTTP/1.1 200 OK\n'
    end = b'\n%s'
    dic = {
        'Content-Type': '',
        'Content-Encoding': 'UTF-8',
        'Content-Length': '',
        'Server': 'z_webFrame'
           }

    @ classmethod
    def add(cls, contentType, contentLength, kwargs, contentEncoding='UTF-8'):
        dic = deepcopy(cls.dic)
        dic['Content-Type'] = contentType
        dic['Content-Length'] = contentLength
        dic['Content-Encoding'] = contentEncoding
        dic.update(kwargs)

        parsed = b''
        for i in dic:
            parsed += i.__str__().encode() + b':' + dic[i].__str__().encode() + b'\n'
        return cls.start + parsed + cls.end

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


def httpResponse_403():
    return 403, responseStatusMessage % (b'403', b'URL FORBIDDEN', b'403 access denied')

def httpResponse_404():
    return 404, responseStatusMessage % (b'404', b'URL NOT FOUNT', b'404 not found')

def httpResponse_500(traceback=None):
    if traceback and debug:
        return 500, responseStatusMessage % (b'500', b'SERVER ERROR', str(traceback).encode())
    return 500, responseStatusMessage % (b'500', b'SERVER ERROR', b'500 server err')

# 页面
def httpRender(fileName, request):

    htmlPath = os.path.join(os.getcwd().split('z_webFrame')[0], 'z_webFrame', staticPath, fileName)
    html, htmlSize, mtime, gzipFile = g.fileDict[htmlPath]

    if 'gzip' in request['Accept-Encoding']:
        return 200, BaseResponse.add('text/html', len(gzipFile).__str__(), {}, contentEncoding='gzip') % gzipFile
    return 200, BaseResponse.add('text/html', htmlSize.__str__(), {}) % html

# 接口
def httpResponse(data):
    if not isinstance(data, bytes):
        data = data.encode()
    dataSize = len(data)
    return 200, currentMessage % (b'text/plain', dataSize.__str__().encode(), data)

# 静态文件
def get_static_file(fileName, request):
    htmlPath = os.path.join(os.getcwd().split('z_webFrame')[0], 'z_webFrame', staticPath) + os.path.normcase(fileName)
    file, fileSize, mStrftime, gzipFile = g.fileDict[htmlPath]
    # 后缀
    suffix = fileName.rsplit('.', 1)[-1]
    mStrftime = agreementDateTime.last_file_time(mStrftime)
    if suffix in contentTypeDic:

        if 'gzip' in request['Accept-Encoding']:
            return 200, BaseResponse.add(contentTypeDic[suffix], len(gzipFile).__str__(), {'last-modified': mStrftime}, contentEncoding='gzip') % gzipFile

        return 200, BaseResponse.add(contentTypeDic[suffix], fileSize.__str__(), {'last-modified': mStrftime}) % file

    return 200, currentMessage % (b'*/*', fileSize.__str__().encode(), file)


if __name__ == '__main__':
    pass

