from backstage.libs.static import *
from backstage.libs.db import Connection
import json
import math
import redis
import datetime
from time import strftime



def get_ip(x,y):#添加日志 记录ip地址
    # if 'HTTP_X_FORWARDED_FOR' in x.META:
    #     ip = x.META['HTTP_X_FORWARDED_FOR']
    # else:
    #     ip = x.META['REMOTE_ADDR']
    ip = x['addr']
    print('访问来自',ip)
    log=open('/home/admin/logs/%s.txt'%strftime('%Y-%m-%d'),'a')
    log.write(strftime('%H:%M:%S')+' '+ip+' '+y+'\n')
def redis_insert():
    tim=strftime('%Y-%m-%d')
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
    res = redis.Redis(connection_pool=pool)
    res.set(tim,1,ex=691200,nx=True)
    res.incr(tim)
    res.close()
###########################视图函数###############################
def home(request):
    # get_ip(request, 'home')
    return httpRender('index.html')
# def home(request):
#     get_ip(request,'home')
#     redis_insert()
#     return httpRender(request,'index.html')
def limit(request):#分页 默认第一页 截取前40
    get_ip(request,'limit')
    with Connection() as cursor:
        # cursor=connection.cursor()
        sql='select iid,date,name,firsturl from album limit 40'
        cursor.execute(sql)
        res=cursor.fetchall()
        dic={
            'img':res,
            'top':[],
        }
    return httpResponse(json.dumps(dic))
def page(request):#带page参数的分页，默认page=1
    get_ip(request,'page')
    if request.httpMethod=='POST':
        page=request['page']
        with Connection() as cursor:
            num=(int(page) - 1) * 20
            sql='select iid,date,name,firsturl from album where hide="False" order by date desc,iid limit 20'
            if int(page)>1:
                sql='select iid,date,name,firsturl from album  where hide="False"order by date desc,iid limit %s,20'%(num)
            cursor.execute(sql)
            res=list(cursor.fetchall())
            res_final=[]
            for i in res:
                i=list(i)
                i.append((str(i[0])+'x'))
                res_final.append(i)

            sqlnum = 'select count(name) from album where hide="False"'
            cursor.execute(sqlnum)
            resnum = cursor.fetchall()
            page_num=resnum
            dic={
                'url':res_final,
                'pagenum':page_num
            }
        return httpResponse(json.dumps(dic))
    else:
        return httpResponse('0')
def pagenum(request):#返回总页数
    get_ip(request,'pagenum')
    with Connection() as cursor:
        sql = 'select count(name) from album'
        cursor.execute(sql)
        res = cursor.fetchall()
        page_num=math.ceil(res[0][0]/20)
    return httpResponse(json.dumps({'pagenum':page_num}))
def signup(request):#注册功能 成功返回1 失败返回0
    get_ip(request,'signup')
    if request.httpMethod=='POST':
        try:
            username,password,tel=request['username'],request['password'],request['tel']
            with Connection() as cursor:
                sql='insert into users (username,password,tel) values("%s","%s","%s")'%(username,password,tel)
                cursor.execute(sql)
                sql1='select uid from users where username="%s"'%username
                cursor.execute(sql1)
                res=cursor.fetchall()[0][0]
            return httpResponse(json.dumps({'success':1,'uid':res}))
        except Exception as err:
            info=str(err).split("'")[-2]
            print(err)
            return httpResponse(json.dumps({'success':0,'repeat':info}))

    else:
        return httpResponse('0')
def signin(request):
    get_ip(request,'signin')
    if request.httpMethod=='POST':
            username,password=request['username'],request['password']
            with Connection() as cursor:
                sql='select uid from users where username="%s" and password="%s"'%(username,password)
                cursor.execute(sql)
                uid=cursor.fetchall()
            if uid:
                return httpResponse(json.dumps({'success':'1','uid':uid[0][0]}))
            else:
                return httpResponse(json.dumps({'success':'0'}))
    else:
        return httpResponse('0')

def select_userinfo(request):
    if request.httpMethod=='POST':
        try:
            uid=request['uid']
            with Connection() as cursor:
                sql='select tel,sex,birthday,province,city from users where uid="%s"'%uid
                cursor.execute(sql)
                res=cursor.fetchall()
            return httpResponse(json.dumps({'success': '1','userinfo':res}).encode())
        except Exception as err:
            return httpResponse(json.dumps({'success': '0', 'errorinfo':str(err)}).encode())
def update_userinfo(request):
    if request.httpMethod=='POST':
        try:
            with Connection() as cursor:
                uid=request['uid']
                # password=res['password']
                tel=request['tel']
                sex=request['sex']
                birthday=request['birthday']
                province=request['province']
                city=request['city']
                sql='update users set tel="%s",sex="%s",birthday="%s",province="%s",city="%s" where uid="%s"'%(tel,sex,birthday,province,city,uid)
                cursor.execute(sql)
            return httpResponse(json.dumps({'success':'1'}).encode())
        except Exception as err:
            return httpResponse(json.dumps({'success':'0','errorinfo':str(err)}).encode())
def look(request):#点赞功能，与排行相关，接收参数是iid
    get_ip(request,'look')
    if request.httpMethod=='POST':
        iid=request['iid']
        with Connection() as cursor:
            sql='update album set look=look+1 where iid=%d'%iid
            cursor.execute(sql)
        return httpResponse(json.dumps({'key':'1'}))
def top(request):#排行功能
    get_ip(request,'top')
    with Connection() as cursor:
        # cursor=connection.cursor()
        sql='select iid,date,name from album order by look desc limit 7'
        cursor.execute(sql)
        res=cursor.fetchall()
    return httpResponse(json.dumps({'img':res}))
def imgList(request):
    get_ip(request,'imgList')
    if request.httpMethod=='POST':
        iid=request['iid']
        with Connection() as cursor:
            sql='select date,name,url from album,url where album.iid=%s and album.iid=url.iid'%iid
            cursor.execute(sql)
            res=cursor.fetchall()
            sql_last = 'select date,name,iid from album where iid<%s order by iid desc limit 1' % iid
            sql_next = 'select date,name,iid from album where iid>%s order by iid  limit 1' % iid
            cursor.execute(sql_last)
            img_last = cursor.fetchall()
            if img_last:
                img_last = img_last[0]
            else:
                img_last = '没有了'
            cursor.execute(sql_next)
            img_next = cursor.fetchall()
            if img_next:
                img_next = img_next[0]
            else:
                img_next = '没有了'
        return httpResponse(json.dumps({'img':res,'img_last':img_last,'img_next':img_next}))
def around(request):
    get_ip(request,'around')
    if request.httpMethod=='POST':
        iid=request['iid']
        with Connection() as cursor:
            sql_last = 'select date,name,iid from album where iid<%s order by iid desc limit 1' % iid
            sql_next = 'select date,name,iid from album where iid>%s order by iid  limit 1' % iid
            cursor.execute(sql_last)
            img_last=cursor.fetchall()
            if img_last:
                img_last=img_last[0]
            else:
                img_last='没有了'
            cursor.execute(sql_next)
            img_next=cursor.fetchall()
            if img_next:
                img_next=img_next[0]
            else:
                img_next='没有了'
        return httpResponse(json.dumps({'img_last':img_last,'img_next':img_next}))
def view(request):
    get_ip(request,'view')
    if request.httpMethod=='POST':
        iid=request['iid']
        with Connection() as cursor:
            sql_last='select date,name,url from album,url where album.iid=%s and album.iid=url.iid where album.iid<%s order by iid desc limit 1'%iid
            sql_next='select date,name,url from album,url where album.iid=%s and album.iid=url.iid where album.iid>%s order by iid limit 1' % iid
            cursor.execute(sql_last)
            img_last = cursor.fetchall()
            cursor.execute(sql_next)
            img_next=cursor.fetchall()
        return httpResponse(json.dumps({'img_last':img_last,'img_next':img_next}))
def province_city_count(request):
    with Connection() as cursor:
        if request.httpMethod=='GET':
            sql='select distinct province from province_city'
            cursor.execute(sql)
            res=cursor.fetchall()
            return httpResponse(json.dumps({'province':res}))
        elif request.httpMethod=='POST':
            if 'province' in str(request):
                province=request['province']
                sql = 'select distinct city from province_city where province="%s"' % province
                cursor.execute(sql)
                res = cursor.fetchall()
                return httpResponse(json.dumps({'city': res}))
            elif 'city' in str(request):
                city=request['city']
                sql = 'select county from province_city where city="%s"' % city
                cursor.execute(sql)
                res = cursor.fetchall()
                return httpResponse(json.dumps({'county': res}))
def count_visit(request):
    pool=redis.ConnectionPool(host='127.0.0.1', port=6379)
    conn=redis.Redis(connection_pool=pool)
    today=datetime.date.today()
    last_1=today-datetime.timedelta(days=1)
    last_2=today-datetime.timedelta(days=2)
    last_3=today-datetime.timedelta(days=3)
    last_4=today-datetime.timedelta(days=4)
    last_5=today-datetime.timedelta(days=5)
    last_6=today-datetime.timedelta(days=6)
    last_7=today-datetime.timedelta(days=7)
    last_1=conn.get(str(last_1))
    if last_1:
        last_1=last_1.decode()
    else:
        last_1=0
    last_2=conn.get(str(last_2))
    if last_2:
        last_2 = last_2.decode()
    else:
        last_2 = 0
    last_3=conn.get(str(last_3))
    if last_3:
        last_3 = last_3.decode()
    else:
        last_3 = 0
    last_4=conn.get(str(last_4))
    if last_4:
        last_4 = last_4.decode()
    else:
        last_4 = 0
    last_5=conn.get(str(last_5))
    if last_5:
        last_5 = last_5.decode()
    else:
        last_5 = 0
    last_6=conn.get(str(last_6))
    if last_6:
        last_6 = last_6.decode()
    else:
        last_6 = 0
    last_7=conn.get(str(last_7))
    if last_7:
        last_7 = last_7.decode()
    else:
        last_7 = 0
    today=conn.get(str(today))
    if today:
        today = today.decode()
    else:
        today = 0
    dic={'today':today,'last_1':last_1,'last_2':last_2,'last_3':last_3,'last_4':last_4,'last_5':last_5,'last_6':last_6,'last_7':last_7}
    conn.close()
    return httpResponse(json.dumps(dic))