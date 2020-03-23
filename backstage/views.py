from backstage.libs.static import *



def home(request):
    return httpRender('index.html')