import traceback
from threading import Thread
from socket import socket, SOL_SOCKET, SO_REUSEADDR, gethostbyname, gethostname

from backstage.libs.static import *
from backstage.libs.handle import handle_url, outputUserInfo

# from gevent import monkey
# monkey.patch_socket()
# import gevent

def send_thread(s, data):
    s.send(data)
    s.close()

def engine(port = 8000):

    s=socket()

    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    serverIp = gethostbyname(gethostname())
    print('当前地址为%s:%s' % (serverIp, port))
    s.bind(('0.0.0.0', port))
    s.listen()
    while True:
        c, addr = s.accept()
        request = httpRequest(c.recv(1024), addr = addr[0])

        # 分发路由
        try:
            # handle_url(c, request) # 纯同步
            Thread(target=handle_url, args=(c, request)).start() # 线程异步
            # gevent.spawn(handle_url, c, request).start()
        except Exception as err:
            print('SYNE ERRPR %s' % traceback.print_exc())
            reponseStatus, funcRes = httpResponse_500()
            outputUserInfo(request, reponseStatus)
            try:
                s.send(funcRes)
                s.close()
            except Exception as err:
                print(err)


if __name__ == '__main__':
    engine(8000)