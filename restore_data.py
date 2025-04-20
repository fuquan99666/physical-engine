import json
import os
def restore_data(data):#传入的数据可以是一串字符串，也可以是一个json格式的对象（形式类似于字典）。请保证数据中存在name对象
    try:
        file_name=data["name"]
    except Exception as e:
        print('警告:data中不含有名为name的值')
        return False
    try:
        with open(f'dataset//{file_name}.json','w',encoding='gbk') as f:
            json.dump(data,f)
            f.close()
    except Exception as e:
        print("restore error,warning tips:"+e)
        return False
    #print(f'成功传入数据，名称为{name}.json')
    return True
def loading_data(data_name,return_str=False):#传入需要加载的文件名和返回值格式(格式默认为.json,输出str需要传入True)
    data=None
    name=data_name.split('.')
    if name[-1]=='json':
        name.pop(-1)
    name=''.join(name)
    #统一data_name结尾是否带有.json,即支持直接传入文件名或文件名.json,但是请不要把dataset//也传进来
    try:
        with open(f'dataset//{name}.json','r',encoding='gbk') as f:
            data=json.load(f)
            if return_str:
                data=str(data)
            f.close()
    except Exception as e:
        print('文件打开失败')
    return data
def delete_file(data_name):#传入需要删除的文件名（是否含有.json均可）
    data_path=data_name.split('.')
    if data_path[-1]=='json':
        data_path.pop(-1)
    data_path=''.join(data_path)
    if os.path.exists(f'dataset//{data_path}.json'):
        os.remove(f'dataset//{data_path}.json')
        print('成功删除文件')
        return True
    else:
        print('未能找到文件，请重试')
        return False
if __name__=='__main__':
    test_dataset={
        'name':'自由落体',
        'gravity':9.81,
        'shape':'circle',
        'process':[
            {'time':0,'position':(0,0),'v':(0,0)},
        ]
    }
    restore_data(test_dataset)
    print(loading_data('自由落体'))
    #delete_file('自由落体')


