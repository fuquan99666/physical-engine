# physical-engine



# 本小组的录频文件位置：https://disk.pku.edu.cn/link/AAB690FCFFB745409ABD185A3E1328E69F
# 文件名：27-演示.mp4
# 有效期限：2025-07-30 15:50
# 提取码：zebZ

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


# 5.27 updated:

成功找到datahandler.buffer中没有数据的原因了
因为***mainwindow中并没有调用simulator.step(在该分支的mainwindow下搜素step只能在多部模拟提升平滑度处看见self.simulator.space.step()的调用)
# 5.28updated:
昨天晚上太高兴了没有更新完readme，今天进行补充：
将self.simulator.space.step()改成self.simulator.step()，buffer成功开始传入数据。
经过调试，根据2.db中的数据，已经能够成功画出matplotlib图像（v_t和x_t）
下一步计划：
1.实现主界面的文件资源管理，即在左侧新增一个资源管理的边框，显示dataset中所有已保存的文件
2.将资源管理文件按钮连接drawmap.py中的相关绘图函数，通过点击查看绘制的图像
3.（在5月31日前很可能无法完成）完善数据保存格式，实现录屏回放。

# 5.28晚updated：
资源管理的边框已经完成，暂时还没有绑定事件。
准备先把drawmap的函数绑定上去，回放功能再说
还有一些细节问题，比如说选定文件显示颜色变化，关闭或切换前提醒未保存文件等等。
save_as的逻辑可能需要更新，选择保存到新文件时应该将旧文件的几个properties表复制过去
edit_object可能需要添加将更改后的物体属性存储进表中的代码（在没有开始写回放前都不着急）

# 5.28 20：03updated:
一个非常有趣的问题：mainwindow和matplotlib的进程是冲突的，即在打开绘图后，无法在不关闭该窗口的前提下继续正常地添加物体
正在解决该问题中……
突然想起来，仅仅实现了添加是不够的。即使由于回放功能可能不需要删除已有的物体数据，至少需要在进行改动时保存物体数据的改变，例如颜色，半径等等。
同样，我暂时还没能找到解决方案，原因是选中物体是让self.selected_item_data为选中的物体，然而在sqlite3中寻找物体基本只能依靠物体idx索引

这个问题我完成了大半（大嘘），主要是找到了mainwindow中的all_item，
segment部分尚未完成，大概只能明天继续了
=======

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

# 5.24 弹簧可以删除，修改了segment的转动惯量系数使得转动效果更加的明显




