# z_webFrame

这是一个基于python socket编程的sync/async双引擎web框架
为了方便上手，文件目录与django大致相似，url分配路由，views为视图函数


核心处理流程为：


创建监听套接字

解析http请求

解析分配路由

处理视图函数

异步io导图
! [导图] (https://github.com/zhaoxinyuan996/z_webFrame/blob/master/MindMapping/socket%2B%E4%BA%8B%E4%BB%B6%E5%BE%AA%E7%8E%AF%2B%E5%9B%9E%E8%B0%83%20%E6%A8%A1%E5%BC%8F%E5%A4%84%E7%90%86%E6%B5%81%E7%A8%8B.jpg);

2020年4月5日
添加 socket+事件循环+回调模式引擎
发现epoll的bug是源于超出TCP最大缓存区引起的

2020年4月2日
因为浏览器通过静态资源的最后修改时间来缓存到内存，
所以除html文件外的静态文件都添加了最后修改时长的字段
添加时区设置
添加 加减当前时间的方法和设置

2020年4月1日
修复contentlength和contenttype缺失引起的致命性bug，
全部接口已添加length和type

2020年3月30日
send方法改为多线程异步io
一个小小的图标改名

2020年3月24日
添加monitor进程监控web进程，防止假死
修复静态文件因为replace加载失败的bug
格式化访问信息打印，time-ip-status-url
添加了404,500前/后台 状态码

2020年3月23日
完成demo
