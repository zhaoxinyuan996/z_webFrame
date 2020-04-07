

class DB_CONFIG():
    username = 'root'
    password = '123456'

class DateTime():
    # 时间格式
    mode = 'GMT'
    zone = 'Asia/Shanghai'

    # 时间调整
    adjustmentHour = 0
    adjustmentMinute = 0

# 异步io的设置
class AsyncSettings():
    # 最大缓冲区设置，防止多个非阻塞的套接字把缓冲区写满 SB浏览器还不取，导致接收不完全的致命bug
    wmem_max = 4196304

    # 防止事件循环跑满cpu设置的等待时间
    # socket + 事件循环 + 回调 模式需要，其他模式不需要
    # 单位为μs(微秒) ，(1000μs == 1ms ; 1000ms = 1s)，不想要这个就改源码
    sleepTime = 1

# 静态文件根目录
staticPath = 'dist'

# 日志级别
debuggerLevel = 'DEBUG'

# 静态文件预加载
preloadingStatic = True

# 禁止访问的url e.g. *.*.*.* 127.*.0.1
deniedRequestIp = []

# 前台是否显示报错原因
debug = True