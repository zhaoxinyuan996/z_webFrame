from .views import *


urlDict = {
    '/': home,
    '/limit': limit,  # 分页，好像没用
    '/signin': signin,  # 登录 参数分别是 username,password 成功返回1，失败返回0
    '/page': page,  # 分页，每页40条
    '/pagenum': pagenum,  # 返回总页数
    '/register': signup,  # 注册 参数分别是 username,password,tel
    '/select_userinfo': select_userinfo,  # 查看用户资料
    '/update_userinfo': update_userinfo,  # 更新用户资料
    '/look': look,  # 点赞 接收iid，后台加1
    '/top': top,  # 排行 返回点赞数最多的前7个
    '/list': imgList,  # 套图内页的图片列表
    '/around': around,  # 上一套，下一套
    '/view': view,  # 二级页面跳转接口
    '/PCC': province_city_count,  # 省市县3级联动
    '/count_visit': count_visit
# 访问/home会增加当天访问量 返回当天和前七天的访问量字典
}