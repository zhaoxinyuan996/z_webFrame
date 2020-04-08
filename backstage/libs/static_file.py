import os
import gzip

from io import BytesIO

from backstage.settings import staticPath

rootPath = os.path.join(os.getcwd().split('z_webFrame')[0], 'z_webFrame',staticPath)

class GetStaticFile():
    def __init__(self):
        self.rootPath = os.path.join(os.getcwd().split('z_webFrame')[0], 'z_webFrame',staticPath)
        self.fileDict = {}
        self.deal_file(rootPath)
    def deal_file(self, file):
        for i in os.walk(file):
            if i[-1]:
                for j in i[-1]:
                    p = os.path.join(i[0], j)
                    self.write_cache(p, os.path.getmtime(p))


    def write_cache(self, absfile, modifytime):
        with open(absfile, 'rb') as f:
            res = f.read()
        f_gzip = BytesIO()
        gzip.open(f_gzip, 'wb').write(res)
        self.fileDict[absfile] = (res, len(res), modifytime, f_gzip.getvalue())


if __name__ == '__main__':
    g = GetStaticFile()

