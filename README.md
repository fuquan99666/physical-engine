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
