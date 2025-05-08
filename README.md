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
# 5.8 updated:
对原先的数据存储方式进行了大更新，原先readme里的存储结构已经不再适用。
现在可以直接通过调用data_handler.py中的 save_to_sqlite函数进行存储数据（需要在函数调用时输入储存的文件名）
更新了drawmap文件，通过调用新的存储文件绘制时间——位置和时间——速度图像（均提供了两种调用方式）
（这次的存储方式从.json改到sqLite3，希望不要再调整数据格式了）
仍然暂时保留restore_data.py(尽管现在看来它已经没什么作用了)
由于我还没有拿到数据，所以不能够保证代码的正确性。如果在调试时出现问题，我会及时（？）进行修改