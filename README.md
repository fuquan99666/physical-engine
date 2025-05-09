# physical-engine

今天天气不错！适合去公园游玩。
hello world!

## uni-ver editted

# 4.6 updated:设置成功

# 4.11 updated:

实现了restore_data函数中的restore_data,loading_data和delete_file三个函数
在dataset文件夹中手动生成了示例json文件'自由落体.json',作为一个预设实验的初始值范例
注记：我个人建议返回的数据按照'自由落体.json'的格式，即：
data={
    'name':'filename',
    'gravity':g,
    'shape':'ibject_shape',
    'process':[
        {'time1':time,'position':(px,py),'v':(vx,vy)}
        {'time2':time,'position':(px,py),'v':(vx,vy)}
        …
        …
        …
    ]
}
若有其它的想法或需求，也可以告知进行修改
下一步计划：可能会是使用matplotlib完成图像绘制


# 5.5 updated:

大作业雏形初具
见mainwindow.py


# 5.9 未完成功能

A：1.场力系统，公式化添加非恒力（如空气阻力等）
   2.音效系统
   3.多边形物体的添加逻辑
   
B：1.录制系统
   2.回放系统
   3.数据分析（表格类）

C: 1.主界面菜单
   2.动画同步性问题
   3.数据统计界面


