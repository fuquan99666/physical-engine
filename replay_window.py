from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSlider
from PyQt6.QtCore import Qt, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from recorder import DataReplayer
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QSlider,
    QVBoxLayout, QHBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsLineItem, QToolBar, QGraphicsRectItem,QSplitter,QMenu,
    QDialog,QFormLayout,QLineEdit,QDialogButtonBox,QCheckBox,QColorDialog,QInputDialog, QTreeView
)
class ReplayWindow(QWidget):
    def __init__(self):
        super().__init__()
        # self.pathname=db_path
        # self.replayer = DataReplayer(f'{db_path}.db')
        self.init_ui()
        self.setup_timeline()

    def init_ui(self):
        self.setWindowTitle("模拟回放: ")
        self.setGeometry(100, 100, 800, 600)
        
        # 可视化区域
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        
        # 控制条
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.seek_time)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.slider)
        self.setLayout(layout)
        
        # 定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def setup_timeline(self):
        """初始化时间轴"""
        timeline = self.replayer.get_full_timeline()
        self.time_points = [t[0] for t in timeline]
        self.slider.setRange(0, len(self.time_points)-1)
        
    def start_replay(self, speed=1.0):
        """开始回放"""
        self.current_frame = 0
        self.timer.start(1000//speed)  # 按指定帧率更新
        
    def update_frame(self):
        """更新帧显示"""
        if self.current_frame >= len(self.time_points):
            self.timer.stop()
            return
            
        current_time = self.time_points[self.current_frame]
        frame_data = self.replayer.get_frame_data(current_time)
        
        self.ax.clear()
        for obj_id, data in frame_data.items():
            self.draw_object(obj_id, data)
        
        self.ax.set_xlim(0, 800)
        self.ax.set_ylim(0, 600)
        self.canvas.draw()
        self.current_frame += 1

    def draw_object(self, obj_id, data):
        props = data['properties']
        x, y = data['position']
        
        if props['shape_type'] == 'circle':
            circle = plt.Circle((x, y), props['radius'], fill=False, edgecolor='red')
            self.ax.add_patch(circle)
        elif props['shape_type'] == 'rectangle':
            rect = plt.Rectangle(
                (x - props['width']/2, y - props['height']/2),
                props['width'], props['height'], 
                fill=False, edgecolor='blue'
            )
            self.ax.add_patch(rect)
        elif props['shape_type'] == 'polygon' and props['vertices']:
            polygon = plt.Polygon(
                [(x + vx, y + vy) for vx, vy in props['vertices']],
                fill=False, edgecolor='green'
            )
            self.ax.add_patch(polygon)
        #关于不同物体属性的问题，to be continued……
    def seek_time(self, frame_index):
        """跳转到指定帧"""
        self.current_frame = frame_index
        self.update_frame()
if __name__=='__main__':
    app = QApplication(sys.argv)
    window = ReplayWindow()
    window.show()
    sys.exit(app.exec())