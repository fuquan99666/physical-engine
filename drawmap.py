import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
from datetime import datetime

#查询物体的位置并绘制图像
def time_position_byindex(db_name,*object_idx):
    conn=sqlite3.connect("dataset\\"+db_name+".db")

    plt.figure(figsize=(12,6))
    plt.subplot(1,2,1)
    plt.xlabel("time")
    plt.ylabel("X_position")

    plt.subplot(1,2,2)
    plt.xlabel("time")
    plt.ylabel("Y_position")

    for i in object_idx:
        data=pd.read_sql_query('''
        SELECT idx,timestamp, x, y
        FROM body_data
        WHERE idx = ?
    ''', conn,params=(i,))
        plt.subplot(1,2,1)
        plt.plot(data["timestamp"],data["x"],label=f"object {i}")
    
        plt.subplot(1,2,2)
        plt.plot(data["timestamp"],data["y"],label=f"object {i}")
    
    conn.close()
    plt.subplot(1,2,1)
    plt.legend()
    plt.subplot(1,2,2)
    plt.legend()

    plt.tight_layout()
    plt.show()

#输入物体编号范围
def time_position_byrange(db_name,startrange,endrange):#结果包含前端点，但是不包含后端点
    conn=sqlite3.connect("dataset\\"+db_name+".db")

    plt.figure(figsize=(12,6))
    plt.subplot(1,2,1)
    plt.xlabel("time")
    plt.ylabel("X_position")

    plt.subplot(1,2,2)
    plt.xlabel("time")
    plt.ylabel("Y_position")

    for i in range(startrange,endrange):
        data=pd.read_sql_query('''
        SELECT idx,timestamp, x, y
        FROM body_data
        WHERE idx = ?
    ''', conn,params=(i,))
        plt.subplot(1,2,1)
        plt.plot(data["timestamp"],data["x"],label=f"object {i}")
    
        plt.subplot(1,2,2)
        plt.plot(data["timestamp"],data["y"],label=f"object {i}")
    
    conn.close()
    plt.subplot(1,2,1)
    plt.legend()
    plt.subplot(1,2,2)
    plt.legend()

    plt.tight_layout()
    plt.show()

def time_v_byindex(db_name,*object_idx):
    conn=sqlite3.connect("dataset\\"+db_name+".db")

    plt.figure(figsize=(12,6))
    plt.subplot(1,2,1)
    plt.xlabel("time")
    plt.ylabel("V_x")

    plt.subplot(1,2,2)
    plt.xlabel("time")
    plt.ylabel("V_y")

    for i in object_idx:
        data=pd.read_sql_query('''
        SELECT idx,timestamp, vx, vy
        FROM body_data
        WHERE idx = ?
    ''', conn,params=(i,))
        plt.subplot(1,2,1)
        plt.plot(data["timestamp"],data["vx"],label=f"object {i}")
    
        plt.subplot(1,2,2)
        plt.plot(data["timestamp"],data["vy"],label=f"object {i}")
    
    conn.close()
    plt.subplot(1,2,1)
    plt.legend()
    plt.subplot(1,2,2)
    plt.legend()

    plt.tight_layout()
    plt.show()

def time_v_byrange(db_name,startrange,endrange):
    conn=sqlite3.connect("dataset\\"+db_name+".db")

    plt.figure(figsize=(12,6))
    plt.subplot(1,2,1)
    plt.xlabel("time")
    plt.ylabel("V_x")

    plt.subplot(1,2,2)
    plt.xlabel("time")
    plt.ylabel("V_y")

    for i in range(startrange,endrange):
        data=pd.read_sql_query('''
        SELECT idx,timestamp, vx, vy
        FROM body_data
        WHERE idx = ?
    ''', conn,params=(i,))
        plt.subplot(1,2,1)
        plt.plot(data["timestamp"],data["vx"],label=f"object {i}")
    
        plt.subplot(1,2,2)
        plt.plot(data["timestamp"],data["vy"],label=f"object {i}")
    
    conn.close()
    plt.subplot(1,2,1)
    plt.legend()
    plt.subplot(1,2,2)
    plt.legend()

    plt.tight_layout()
    plt.show()
if __name__=="__main__":
    time_v_byindex('2',0,1)