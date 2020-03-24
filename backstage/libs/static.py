import os
from backstage import settings

staticPath = settings.staticPath

htmlMessage = b'''HTTP/1.1 200 OK
Date: Mon, 23 May 2005 22:38:34 GMT
Content-Type: text/html; charset=UTF-8
Content-Encoding: UTF-8

%s
'''

apiMessage = b'''HTTP/1.1 200 OK
Date: Mon, 23 May 2005 22:38:34 GMT
Content-Type: */*; charset=UTF-8
Content-Encoding: UTF-8

%s
'''

editMessage = b'''HTTP/1.1 %s %s
Date: Mon, 23 May 2005 22:38:34 GMT
Content-Type: */*; charset=UTF-8
Content-Encoding: UTF-8

%s
'''

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
            if ':' in i:
                self.__dict__[i.split(':')[0]] = i.split(':')[1]

        del self.data, self.part1, self.part2

def httpResponse_404():
    return 404, editMessage % (b'404', b'URL NOT FOUNT', b'404 not found')

def httpResponse_500():
    return 500, editMessage % (b'500', b'SERVER ERROR', b'500 server err')

# 页面
def httpRender(fileName):
    htmlPath = os.path.join(os.getcwd().split('z_webFrame')[0], 'z_webFrame', staticPath, fileName)
    with open(htmlPath, 'rb') as f:
        html = f.read()

    return 200, htmlMessage % html

# 接口
def httpResponse(data):

    return 200, apiMessage % data

# 静态文件
def get_static_file(fileName):

    htmlPath = os.path.join(os.getcwd().split('z_webFrame')[0], 'z_webFrame', staticPath) + os.path.normcase(fileName)
    with open(htmlPath, 'rb') as f:
        html = f.read()

    return 200, apiMessage % html


if __name__ == '__main__':
    print(os.getcwd())