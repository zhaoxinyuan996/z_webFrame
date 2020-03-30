import time
import traceback

from backstage import urls
from backstage.libs.static import *


class CheckData():
    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        if not value:
            self.value = None
        if 'static' in value:
            self.value = 'static'
        else:
            self.value = 'url'
        pass

    def __delete__(self, instance):
        pass

class Attribute():
    check = CheckData()

# 分发路由
def handle_url(s, request):
    reponseStatus = None
    checkValue = Attribute()
    checkValue.check = request.get('httpUrl')

    funcRes = 'SyntaxError: url读取失败'.encode()
    # 未识别 返回未识别
    if not checkValue.check:
        return

    if request.get('httpUrl'):

            # 走路由
        if checkValue.check == 'url':
            if urls.urlDict.get(request['httpUrl']):
                try:
                    reponseStatus, funcRes = urls.urlDict[request['httpUrl']](request)
                except Exception as err:
                    print('HANDLE ERRPR %s' % traceback.print_exc())
                    reponseStatus, funcRes = httpResponse_500()
            else:
                reponseStatus, funcRes = httpResponse_404()
        # 读静态文件
        elif checkValue.check == 'static':
            reponseStatus, funcRes = get_static_file(request['httpUrl'])

    outputUserInfo(request, reponseStatus)
    s.send(funcRes)



def outputUserInfo(request, reponseStatus):
    print('%s - %s - %s - %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), request.addr, reponseStatus, request.httpUrl))