import sys, os, signal
from time import sleep
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

    elif engine == 'io':
        from backstage.multi_engine import engine

    else:
        raise EngineError('请选择正确的引擎')



# def monitor(pid):
#
#     signal.signal(signal.SIGINT, lambda n1, n2 :os.kill(pid, 1) and os._exit(1))
#     while True:
#         sleep(99999)
#
# if __name__ == '__main__':
#
#     pFrame = Process(target=main)
#     pFrame.start()
#
#     pMonitor = Process(target=monitor, args=(pFrame.pid, ))
#     pMonitor.start()

if __name__ == '__main__':
    main()
