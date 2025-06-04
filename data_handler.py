import pandas as pd
from datetime import datetime
from pymunk import Body
# from simulator import PhysicsSimulator
import sqlite3
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QInputDialog
from PyQt6.QtCore import QObject, pyqtSignal
import json


class DataHandler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.buffer = []
        self.restored_bodies = []
        self.last_save_time = datetime.now().timestamp()
        self.current_sim_time = 0.0  # 总时间
        self.current_file = None

    def create_initial_file(self):
        text, ok = QInputDialog.getText(
            self,  # 父窗口
            "新建文件",  # 对话框标题
            "请输入文件名:",  # 提示文字
        )
        # 处理用户输入
        if ok and text:  # 用户点击了OK且输入不为空
            dataset_dir = os.path.abspath('./dataset')  # 获取绝对路径
            if not os.path.exists(dataset_dir):
                os.makedirs(dataset_dir)  # 创建目录

            # 构建完整路径
            self.current_file = os.path.join(dataset_dir, f'{text}.db')
            print(f"正在创建文件: {self.current_file}")


            try:
                conn = sqlite3.connect(self.current_file)
                cursor = conn.cursor()
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
                cursor.execute('''CREATE TABLE IF NOT EXISTS circle_properties(
                                obj_id INTEGER PRIMARY KEY,  -- 与轨迹表的obj_id关联
                                shape_type TEXT,
                                mass REAL,
                                color TEXT,
                                radius REAL
                                )
                                ''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS polygon_properties(
                                obj_id INTEGER PRIMARY KEY,  -- 与轨迹表的obj_id关联
                                shape_type TEXT,
                                mass REAL,
                                color TEXT,
                                width REAL,                  
                                height REAL
                                )
                                ''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS segment_properties(
                            obj_id INTEGER PRIMARY KEY,  -- 与轨迹表的obj_id关联
                            shape_type TEXT,
                            mass REAL,
                            color TEXT,
                            radius REAL,
                            start_x REAL,                  -- 线段的起点
                            start_y REAL,     
                            destination_x REAL,            -- 线段的终点
                            destination_y REAL,
                            elasticity REAL)

                        ''')
                conn.commit()
                conn.close()
                print("成功创建文件")
            except Exception as e:
                print(f"创建文件失败: {str(e)}")
                self.statusBar().showMessage(f"创建失败: {str(e)}", 3000)

        else:  # 用户点击了Cancel
            print("取消创建文件")
            self.statusBar().showMessage("取消创建文件", 3000)

    def update_sim_time(self, dt):
        self.current_sim_time += dt

    def register_object(self, obj_id, shape_type, **properties):
        """注册物体属性到数据库"""
        try:
            conn = sqlite3.connect(self.current_file)  # 连接到数据库
            cursor = conn.cursor()  # 创建游标对象
            type = shape_type
            if type == 'circle':
                prop_data = {
                    'obj_id': obj_id,
                    'shape_type': shape_type,
                    'mass': properties.get("mass"),
                    'color': properties.get("color"),
                    'radius': properties.get('radius'),
                }
                cursor.execute('''
                    INSERT INTO circle_properties 
                    VALUES(:obj_id, :shape_type, :mass,:color, :radius)
                ''', prop_data)
            elif type == 'polygon':
                prop_data = {
                    'obj_id': obj_id,
                    'shape_type': shape_type,
                    'mass': properties.get("mass"),
                    'color': properties.get("color"),
                    'width': properties.get('width'),
                    'height': properties.get('height'),
                }
                cursor.execute('''
                    INSERT INTO polygon_properties 
                    VALUES(:obj_id, :shape_type, :mass,:color, :width, :height)
                ''', prop_data)
            elif type == 'segment':
                prop_data = {
                    'obj_id': obj_id,
                    'shape_type': shape_type,
                    'mass': properties.get("mass"),
                    'color': properties.get("color"),
                    'radius': properties.get('radius'),
                    'start_x': properties.get('start').x,
                    'start_y': properties.get('start').y,
                    'destination_x': properties.get('destination').x,
                    'destination_y': properties.get("destination").y,
                    'elasticity': properties.get("elasticity"),
                }
                cursor.execute('''
                    INSERT INTO segment_properties 
                    VALUES(:obj_id, :shape_type, :mass,:color, :radius,:start_x,:start_y,:destination_x,:destination_y,:elasticity)
                ''', prop_data)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"属性注册失败: {str(e)}")

    def collect_data(self, bodies, current_time):
        """收集数据，在确认数据类型后再确定形式"""
        for index, body in enumerate(bodies):
            new_row = {
                "idx": index,
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
        self.current_sim_time = 0.0

    def save_to_sqlite(self, filepath):
        try:
            conn = sqlite3.connect(filepath)  # 连接到数据库
            cursor = conn.cursor()  # 创建游标对象
            data_to_insert = [
                (row["idx"], row["timestamp"], row["x"], row["y"], row["vx"], row["vy"])
                for row in self.buffer
            ]
            # 目前为止一个很重要的问题：data_to_insert在调试时为空列表
            # 执行批量插入
            cursor.executemany('''
                INSERT INTO body_data (idx, timestamp, x, y, vx, vy)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', data_to_insert)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.commit()  # 提交事务
            conn.close()  # 关闭连接
        except Exception as e:
            error_msg = f"保存失败: {str(e)}"
            print(error_msg)
            # self._show_error_dialog(error_msg)

    """另存为（选择新路径保存）"""

    def save_as(self):
        # 使用 PyQt 文件对话框
        filepath, _ = QFileDialog.getSaveFileName(
            None,  # 父窗口（可选）
            "另存为",  # 对话框标题
            "./dataset",  # 初始目录
            "SQLite Database (*.db);;All Files (*)"  # 文件过滤器
        )
        # 用户取消操作时，filepath会返回""
        if not filepath:
            return
        self.current_file = f'./dataset/{filepath}.db'
        self.save_to_sqlite(self.current_file)

    def save(self):
        if self.current_file:
            self.save_to_sqlite(self.current_file)
        else:
            self.save_as()


class DataCalculator:
    @staticmethod
    def kinetic_energy(body: Body):
        return 0.5 * body.mass * (body.velocity.x ** 2 + body.velocity.y ** 2)

    @staticmethod
    def potential_energy(body: Body, ground_y=400, y_axis_direction: str = "down"):
        height = (ground_y - body.position.y) if y_axis_direction == "down" else (body.position.y - ground_y)
        '''重力设定似乎很不完全，需要调整'''
        return body.mass * 9.81 * height
