# z_webFrame

这是一个基于python socket编程的sync/async双引擎web框架，为了方便上手，文件目录与django大致相似，url分配路由，views写视图函数


核心流程为：


创建监听套接字

解析http请求

解析分配路由

处理视图函数



2020年3月24日
添加monitor进程监控web进程，防止假死
修复静态文件因为replace加载失败的bug
格式化访问信息打印，time-ip-status-url
添加了404,500前/后台 状态码

2020年3月23日
完成demo
