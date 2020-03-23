import sys, os
from multiprocessing import Process
class EngineError(Exception):pass
def main():
    sys.argv.remove(os.path.basename(globals()['__file__']))

    engine = 'async'
    port = 8000
    if len(sys.argv) == 1:
        if sys.argv[0] == 'async' or sys.argv[0] == 'sync':
            engine = sys.argv[0]
        else:
            port = sys.argv[0]

    elif len(sys.argv) == 2:
        engine, port =  sys.argv

    try:
        port = int(port)
    except:
        raise TypeError('端口号必须是数字')

    if engine == 'sync':
        from backstage.sync_engine import engine

        engine(port)

    elif engine == 'async':
        pass

    else:
        raise EngineError('请选择正确的引擎')


if __name__ == '__main__':
    p = Process(target=main)
    p.start()


# 还需要重定向，解决图片返回格式非image/jpeg，导致response加载失败