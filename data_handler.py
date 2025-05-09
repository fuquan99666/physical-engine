import pandas as pd
from datetime import datetime
from pymunk import Body
from simulator import PhysicsSimulator
import sqlite3
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton,QFileDialog
from PyQt6.QtCore import QObject, pyqtSignal
import csv
class DataHandler(QObject):
    def __init__(self):
        self.buffer=[]
        self.last_save_time=datetime.now().timestamp()
        self.current_sim_time=0.0#总时间
        self.current_file=None

    def update_sim_time(self,dt):
        self.current_sim_time+=dt

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
            self.databuffer.append(new_row)
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
            # 准备批量插入的数据
            data_to_insert = [
                (row["idx"], row["timestamp"], row["x"], row["y"], row["vx"], row["vy"])
                for row in self.databuffer
            ]
            
            # 执行批量插入
            cursor.executemany('''
                INSERT INTO body_data (idx, timestamp, x, y, vx, vy)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', data_to_insert)
            conn.commit()  # 提交事务
            conn.close()   # 关闭连接
        except Exception as e:
            error_msg = f"保存失败: {str(e)}"
            self._show_error_dialog(error_msg)

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
        self._save_to_sqlite(filepath)
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

