import selectors
from functools import partial
from socket import socket, SOL_SOCKET, SO_REUSEADDR, gethostbyname, gethostname

# 接入
from backstage.libs.handle import handle_url
from backstage.libs.static import httpRequest


def accept(sel, s, seat):
    c, addr = s.accept()
    c.setblocking(False)

    sel.register(c, selectors.EVENT_READ, partial(read_func, sel, addr))

# 读
def read_func(sel, addr, c, seat):
    if not addr:
        sel.unregister(c)
        return
    try:
        request = httpRequest(c.recv(1024), addr=addr[0])
        sel.modify(c, selectors.EVENT_WRITE, partial(write_func, sel, request))
    except (ConnectionResetError, ConnectionAbortedError):
        sel.unregister(c)

# 写
# lis = []
def write_func(sel, request, c, seat):
    handle_url(c, request)
    sel.modify(c, selectors.EVENT_READ, partial(read_func, sel, None))
    # 非阻塞引起的bug
    # if c not in lis:
    #     print(c, '不在')
    #     handle_url(c, request)
    #     lis.append(c)
    # else:
    #     print(c, '在')
    #     sel.unregister(c)
    #     lis.remove(c)


# 读为1 写为2
def engine(sel, port):
    serverIp = gethostbyname(gethostname())
    print('当前地址为%s:%s' % (serverIp, port))

    sock = socket()
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.setblocking(False)
    sock.bind(('0.0.0.0', port))
    sock.listen()
    sel.register(sock, selectors.EVENT_READ, partial(accept, sel))
    while True:
        for s, event in sel.select():
            callback = s.data
            callback(s.fileobj, 'seat')


if __name__ == '__main__':
    sel = selectors.DefaultSelector()
    engine(sel, 8000)



