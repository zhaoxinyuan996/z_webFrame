import os
import platform

from time import sleep
from functools import partial
from socket import socket, SOL_SOCKET, SO_REUSEADDR, gethostbyname, gethostname, AF_INET, SOCK_STREAM, SO_SNDBUF

from backstage.libs.handle import handle_url
from backstage.libs.static import httpRequest
from backstage.settings import AsyncSettings


class MySocket(socket):
    def __init__(self,fileno=None):
        super().__init__(family=AF_INET, type=SOCK_STREAM, proto=0, fileno=fileno)
        self.setblocking(False)

    def accept(self):
        try:
            fd, addr = self._accept()
            c = MySocket(fileno=fd)
            c.setsockopt(SOL_SOCKET, SO_SNDBUF, AsyncSettings.wmem_max)
            return c, addr
        except BlockingIOError:
            return None

    def my_send(self):
        try:
            self.send(b'')
            return True
        # except (BrokenPipeError, ConnectionAbortedError, BlockingIOError, ConnectionResetError):
        except Exception:
            return False

    def my_recv(self):
        try:
            self.recv(1)
            return True
        except Exception:
            return False

class CheckEvent():
    def __init__(self):
        self.dic = {0: {}, 1: {}}
        self.modifyTmp = {}
        self.unregisterTmp = set()
        self.flag = 0
        self.allowMode = ('accept', 'my_recv', 'my_send')

    def register(self, obj, event, func):
        if event not in self.allowMode:
            raise ValueError('mode is not permissible')
        obj.func = func
        self.dic[self.flag ^ 1][obj] = event

    def unregister(self, obj):
        if obj not in self.dic[self.flag]:
            raise KeyError('object is not register!')
        self.unregisterTmp.add(obj)

    def modify(self, obj, event, func):
        if event not in self.allowMode:
            raise ValueError('mode is not permissible')
        if obj not in self.dic[self.flag]:
            raise KeyError('object is not register!')
        obj.func = func
        self.modifyTmp[obj] = event

    def check(self):
        # 运行下，如果跑通就返回结果
        # 遍历时候字典不可修改，所以用2个字典交替遍历
        for c, event in self.dic[self.flag].items():
            if event == 'accept':
                res = type(c).__dict__[event](c)
                if res:
                    yield res, event
            else:
                if type(c).__dict__[event](c):
                    yield c, event
        else:
            # 修改
            for k, w in self.modifyTmp.items():
                self.dic[self.flag ^ 1][k] = w

            # 复制
            for k ,w in self.dic[self.flag].items():
                if k not in self.modifyTmp and k not in self.unregisterTmp:
                    self.dic[self.flag ^ 1][k] = w


            # 复制完毕，清空所有临时池和待复制字典
            self.modifyTmp.clear()
            self.unregisterTmp.clear()
            self.dic[self.flag].clear()

            # 换字典
            self.flag = self.flag ^ 1

# 3种情况 注册 修改 注销
# 注册 注册到另一个dic
# 修改 修改到另一个dic 添加到修改池 复制字典先添加修改池，如果复制时重复则跳过
# 注销 添加到注销池，如果复制的键在注销池则跳过
# 复制完毕后全部清空
def func_accept(check, sock, addr):
    check.register(sock, 'my_recv', partial(func_read, check, sock, addr))

def func_read(check, sock, addr):
    # 解析
    res = sock.recv(1024)
    if res.startswith(b'E'):
        res = b'G' + res
    elif res.startswith(b'O'):
        res = b'P' + res
    res = httpRequest(res, addr = addr[0])
    check.modify(sock, 'my_send', partial(func_write, check, sock, res))

def func_write(check, sock, request):
    data = handle_url(sock, request, 'mysocket')
    if data:
        sock.send(data)
        check.modify(sock, 'my_send', partial(wait_close, check, sock))
    else:
        sock.close()

def wait_close(check, sock):
    sock.close()
    check.unregister(sock)


def engine(check, port):
    if 'linux' in platform.system().lower():
        os.system('sysctl -w net.core.wmem_max=%s' % AsyncSettings.wmem_max)
    serverIp = gethostbyname(gethostname())
    sleepTime = AsyncSettings.sleepTime / 1000000

    print('当前地址为%s:%s' % (serverIp, port))
    print('当前TCP缓冲区最大值为%s' % AsyncSettings.wmem_max)
    print('当前事件循环强制等待时长为%ss' % sleepTime)

    sock = MySocket()
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)
    sock.bind(('0.0.0.0', port))
    sock.listen()
    check.register(sock, 'accept', sock.accept)
    while True:
        for s, event in check.check():
            if isinstance(s, tuple):
                func_accept(check, s[0], s[-1][0])
                continue
            s.func()
        sleep(sleepTime)


MODE = 'mysocket'
check = CheckEvent()
if __name__ == '__main__':
    engine(check, 8000)


