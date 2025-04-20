# physical-engine
今天天气不错！适合去公园游玩。
hello world!
## uni-ver editted
# 4.6 updated:设置成功
# 4.11 updated:
实现了restore_data函数中的restore_data,loading_data和delete_file三个函数
在dataset文件夹中手动生成了示例json文件'自由落体.json',作为一个预设实验的初始值范例
最新通过讨论得到的存储数据的结构如下：
data={
    'name':'filename',
    ('gravity':g,)
    ('G_data':[
            'fixed':true/false,
            (if true:[{'code':code1,'m':mass,},{'code':code1,'m':mass,}……])
            (if false:{'time1':[time,{'code':code1,'m':mass,},{'code':code1,'m':mass,}……]})
        ],
    )
    (magnet_data:[
            {'time:time','direction':垂直纸面向内或向外，具体怎么表示自行决定,'strength':磁场强度的值}，
            {'time:time','direction':垂直纸面向内或向外，具体怎么表示自行决定,'strength':磁场强度的值}，……
        ]
    )
    'object_data':[
        {
            'code':code1,
            'm':mass,
            'shape':'object_shape',
            ('miu':摩擦系数)，
            'process':[
                {'time1':time,'position':(px,py),'v':(vx,vy),'f':(fx,fy)},
                {'time2':time,'position':(px,py),'v':(vx,vy),'f':(fx,fy)},
                …
                …
                …
            ],
        },
        {
            'code':code2,
            'm':mass,
            'shape':'object_shape',
            ('miu':摩擦系数)，
            'process':[
                {'time1':time,'position':(px,py),'v':(vx,vy),'f':(fx,fy)},
                {'time2':time,'position':(px,py),'v':(vx,vy),'f':(fx,fy)},
                …
                …
                …
            ],
        }
    ]
}
对一些其它的功能，可以讨论添加
下一步计划：可能会是使用matplotlib完成图像绘制
