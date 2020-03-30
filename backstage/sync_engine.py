import traceback
from socket import socket, SOL_SOCKET, SO_REUSEADDR, gethostbyname, gethostname

from backstage.libs.static import *
from backstage.settings import socketBlock
from backstage.libs.handle import handle_url, outputUserInfo


def engine(port = 8000):

    s=socket()

    s.setblocking(socketBlock)

    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    serverIp = gethostbyname(gethostname())
    print('当前地址为%s:%s' % (serverIp, port))
    s.bind(('0.0.0.0', port))
    s.listen()
    while True:
        while True:
            try:
                c, addr = s.accept()
                break
            except BlockingIOError:
                pass
        while True:
            try:
                request = httpRequest(c.recv(1024), addr=addr[0])
                break
            except BlockingIOError:
                pass
        # 分发路由

        try:
            handle_url(c, request)
        except Exception as err:
            print('SYNE ERRPR %s' % traceback.print_exc())
            reponseStatus, funcRes = httpResponse_500()
            outputUserInfo(request, reponseStatus)
            try:
                c.send(funcRes)
            except Exception as err:
                print(err)

        c.close()


if __name__ == '__main__':
    engine(8000)