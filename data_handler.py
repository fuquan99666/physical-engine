import pandas as pd
from datetime import datetime
from pymunk import Body
#from simulator import PhysicsSimulator
import sqlite3
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton,QFileDialog,QInputDialog
from PyQt6.QtCore import QObject, pyqtSignal
import json
class DataHandler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.buffer=[]
        self.restored_bodies=[]
        self.last_save_time=datetime.now().timestamp()
        self.current_sim_time=0.0#总时间
        self.current_file=None
        self.create_initial_file()
    def create_initial_file(self):
        text, ok = QInputDialog.getText(
            self,                    # 父窗口
            "新建文件",              # 对话框标题
            "请输入文件名:",         # 提示文字
        )
        # 处理用户输入
        if ok and text:  # 用户点击了OK且输入不为空
            print(f"正在创建文件: {text}")
            self.current_file=text
            print("成功创建文件")
            conn=sqlite3.connect(f'./dataset/{self.current_file}.db')
            cursor=conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS body_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    idx INTEGER,
                    timestamp REAL,
                    x REAL,
                    y REAL,
                    vx REAL,
                    vy REAL
                )
            ''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS object_properties
                    (obj_id INTEGER PRIMARY KEY,  -- 与轨迹表的obj_id关联
                    shape_type TEXT CHECK(shape_type IN ('circle', 'rectangle', 'polygon','segment','spring')),
                    radius REAL,                 -- 圆形专用
                    width REAL,                  -- 矩形/多边形专用
                    height REAL,
                    start REAL,
                    destination REAL,
                    vertices TEXT,               -- 多边形顶点坐标 JSON存储
                    metadata TEXT)               -- 其他扩展属性 JSON
                ''')
            conn.commit()
            conn.close()
        else:  # 用户点击了Cancel
            print("取消创建文件")
            self.statusBar().showMessage("取消创建文件", 3000)
    def update_sim_time(self,dt):
        self.current_sim_time+=dt
    def register_object(self, obj_id, shape_type, **properties):
        """注册物体属性到数据库"""
        try:
            conn = sqlite3.connect(f'./dataset/{self.current_file}.db')       # 连接到数据库
            cursor = conn.cursor() # 创建游标对象
            
            # 将属性转换为字典，处理JSON字段
            prop_data = {
                'obj_id': obj_id,
                'shape_type': shape_type,
                'mass':properties['mass'],
                'radius': properties.get('radius'),
                'width': properties.get('width'),
                'height': properties.get('height'),
                'start':properties.get('start'),
                'destination':properties.get("destination"),
                'vertices': json.dumps(properties.get('vertices', [])),
                'metadata': json.dumps(properties.get('metadata', {}))
            }

            # 插入或更新属性表
            cursor.execute('''
                INSERT INTO object_properties 
                VALUES (:obj_id, :shape_type, :radius, :width, 
                            :height,:start,:destination, :vertices, :metadata)
            ''', prop_data)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"属性注册失败: {str(e)}")
    def collect_data(self,bodies,current_time):
        """收集数据，在确认数据类型后再确定形式"""
        for index,body in enumerate(bodies):
            new_row={
                "idx":index,
                "timestamp": current_time,
                "x": body.position.x,
                "y": body.position.y,
                "vx": body.velocity.x,
                "vy": body.velocity.y,
            }
            self.buffer.append(new_row)
    def reset(self):
        '''清空数据重新开始'''
        self.buffer.clear()
        self.current_sim_time=0.0
    
    
    def save_to_sqlite(self, filepath):
        try:
            #检测文件是否存在，如果在就删除旧文件
            if os.path.exists(filepath):
                os.remove(filepath)
            conn = sqlite3.connect(filepath)       # 连接到数据库
            cursor = conn.cursor()                 # 创建游标对象
            # 创建表（如果不存在）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS body_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    idx INTEGER,
                    timestamp REAL,
                    x REAL,
                    y REAL,
                    vx REAL,
                    vy REAL
                )
            ''')
            #创建另一张存储物体属性的表
            cursor.execute('''CREATE TABLE IF NOT EXISTS object_properties
                      (obj_id INTEGER PRIMARY KEY,  -- 与轨迹表的obj_id关联
                       shape_type TEXT CHECK(shape_type IN ('circle', 'rectangle', 'polygon','segment','spring')),
                       radius REAL,                 -- 圆形专用
                       width REAL,                  -- 矩形/多边形专用
                       height REAL,
                       vertices TEXT,               -- 多边形顶点坐标 JSON存储
                       metadata TEXT)               -- 其他扩展属性 JSON
                   ''')
            # 准备批量插入的数据
            data_to_insert = [
                (row["idx"], row["timestamp"], row["x"], row["y"], row["vx"], row["vy"])
                for row in self.buffer
            ]
            
            # 执行批量插入
            cursor.executemany('''
                INSERT INTO body_data (idx, timestamp, x, y, vx, vy)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', data_to_insert)
            self.conn.execute("PRAGMA foreign_keys = ON")
            conn.commit()  # 提交事务
            conn.close()   # 关闭连接
        except Exception as e:
            error_msg = f"保存失败: {str(e)}"
            #self._show_error_dialog(error_msg)

    """另存为（选择新路径保存）"""
    def save_as(self):
        # 使用 PyQt 文件对话框
        filepath, _ = QFileDialog.getSaveFileName(
            None,  # 父窗口（可选）
            "另存为",  # 对话框标题
            "./dataset",  # 初始目录
            "SQLite Database (*.db);;All Files (*)"  # 文件过滤器
        )
        #用户取消操作时，filepath会返回""
        if not filepath:
            return
        self.save_to_sqlite(filepath)
        self.current_file = filepath
    def save(self):
        if self.current_file:
            self.save_to_sqlite(self.current_file)
        else:
            self.save_as()
class DataCalculator:
    @staticmethod
    def kinetic_energy(body:Body):
        return 0.5*body.mass*(body.velocity.x**2+body.velocity.y**2)

    @staticmethod
    def potential_energy(body:Body,ground_y=400,y_axis_direction:str="down"):
        height = (ground_y - body.position.y) if y_axis_direction == "down" else (body.position.y - ground_y)
        '''重力设定似乎很不完全，需要调整'''
        return body.mass*9.81*height
