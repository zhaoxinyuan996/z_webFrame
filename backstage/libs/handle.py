from re import search, findall
from functools import partial

from backstage import urls
from backstage.libs.static import *


class CheckData():
    def __get__(self, instance, owner):
        return self.value
        # elif '':
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
    checkValue = Attribute()
    checkValue.check = request.get('httpUrl')

    funcRes = 'SyntaxError: url读取失败'.encode()
    # 未识别 返回未识别
    if not checkValue.check:
        funcRes = httpResponse_404()
        s.send(funcRes)

    if request.get('httpUrl'):

            # 走路由
        if checkValue.check == 'url':
            if urls.urlDict.get(request['httpUrl']):
                funcRes = urls.urlDict[request['httpUrl']](request)
        # 读静态文件
        elif checkValue.check == 'static':
            funcRes = get_static_file(request['httpUrl'])

    s.send(funcRes)
