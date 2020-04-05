from socket import socket, SOL_SOCKET, SO_REUSEADDR, gethostbyname, gethostname, AF_INET, SOCK_STREAM, SO_SNDBUF
from time import sleep
from functools import partial

from backstage.libs.handle import handle_url
from backstage.libs.static import httpRequest


class MySocket(socket):
    def __init__(self,fileno=None):
        super().__init__(family=AF_INET, type=SOCK_STREAM, proto=0, fileno=fileno)
        self.setblocking(False)

    def accept(self):
        try:
            fd, addr = self._accept()
            c = MySocket(fileno=fd)
            c.setsockopt(SOL_SOCKET, SO_SNDBUF, 4096)
            return c, addr
        except BlockingIOError:
            return None

    def my_send(self):
        try:
            self.send(b'')
            return True
        except (ConnectionAbortedError, BlockingIOError):
            return False

    def my_recv(self):
        try:
            self.recv(1)
            return True
        except (ConnectionAbortedError, BlockingIOError):
            return False

class CheckEvent():
    def __init__(self):
        self.dic = {1: {}, 2: {}}
        self.modifyTmp = {}
        self.unregisterTmp = set()
        self.flag = 1
        self.allowMode = ('accept', 'my_recv', 'my_send')

    def register(self, obj, event, func):
        if event not in self.allowMode:
            raise ValueError('mode is not permissible')
        obj.func = func
        if self.flag == 1:
            self.dic[2][obj] = event
        else:
            self.dic[1][obj] = event

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
                if self.flag == 1:
                    self.dic[2][k] = w
                else:
                    self.dic[1][k] = w

            # 复制
            for k ,w in self.dic[self.flag].items():
                if k not in self.modifyTmp and k not in self.unregisterTmp:
                    if self.flag == 1:
                        self.dic[2][k] = w
                    else:
                        self.dic[1][k] = w

            # 复制完毕，清空所有临时池和待复制字典
            self.modifyTmp.clear()
            self.unregisterTmp.clear()
            self.dic[self.flag].clear()

            # 换字典
            if self.flag == 1: self.flag = 2
            else: self.flag = 1

# 3种情况 注册 修改 注销
# 注册 注册到另一个dic
# 修改 修改到另一个dic 添加到修改池 复制字典先添加修改池，如果复制时重复则跳过
# 注销 添加到注销池，如果复制的键在注销池则跳过
# 复制完毕后全部清空
def func_accept(check, sock, addr):
    check.register(sock, 'my_recv', partial(func_read, check, sock, addr))

def func_read(check, sock, addr):
    # 解析
    # print(sock)
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
        sock.setblocking(True)
        sock.sendall(data)
        check.unregister(sock)


# 读为1 写为2
def engine(check, port):
    serverIp = gethostbyname(gethostname())
    print('当前地址为%s:%s' % (serverIp, port))

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
        sleep(0.1)

# 注册时就应该把函数加进去
# 下一步直接运行不带参的函数

MODE = 'mysocket'
check = CheckEvent()
if __name__ == '__main__':
    engine(check, 8000)



