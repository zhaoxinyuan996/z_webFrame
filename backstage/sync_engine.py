from socket import socket, SOL_SOCKET, SO_REUSEADDR, gethostbyname, gethostname

from backstage.libs.handle import handle_url
from backstage.libs.static import *



def engine(port = 8000):

    s=socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    serverIp = gethostbyname(gethostname())
    print('当前地址为%s:%s' % (serverIp, port))
    s.bind(('0.0.0.0', port))
    s.listen()
    while True:
        c, addr = s.accept()
        request = httpRequest(c.recv(1024))
        # 分发路由
        handle_url(c, request)
        c.close()


if __name__ == '__main__':
    engine(8000)