#本代码使用的是pyqt6，实现的是一个qt界面

""" QMainWindow 是 PyQt/PySide 中用于创建主窗口的类。它通常包含以下区域：
        菜单栏(Menu Bar)
        工具栏(Toolbar)
        状态栏(Status Bar)
        中央区域(Central Widget) """
import pymunk
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QSlider,
    QVBoxLayout, QHBoxLayout, QLabel, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,QToolBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor,QAction
import pyqtgraph as pg



class MainWindow(QMainWindow):                                #继承一个主窗口的类
    def __init__(self):           #构造函数          
        super().__init__()          #基类初始化
        self.setWindowTitle("2D Physics Engine UI")   #设置窗口标题
        self.resize(1200, 700)          #设置窗口大小，1000*600像素


        #设置工具栏
        self.toolbar=QToolBar("Main ToolBar")
        self.addToolBar(self.toolbar)

        start_action=QAction("Start/Pause",self)
        start_action.triggered.connect(self.toggle_simulation)
        self.toolbar.addAction(start_action)

        reset_action=QAction("Reset",self)
        reset_action.triggered.connect(self.reset_simulation)
        self.toolbar.addAction(reset_action)


        add_ball_action=QAction("Add a ball",self)
        add_ball_action.triggered.connect(self.add_ball)
        self.toolbar.addAction(add_ball_action)

        delete_ball_action=QAction("Delete Selected",self)
        delete_ball_action.triggered.connect(self.delete_selected_ball)
        self.toolbar.addAction(delete_ball_action)

        quit_select_action=QAction("quit selected",self)
        quit_select_action.triggered.connect(self.quit_select)
        self.toolbar.addAction(quit_select_action)


        # 主界面结构
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 1. 场景 + 刚体图形
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 600, 600)

        self.view = QGraphicsView(self.scene)
        self.view.setMinimumSize(400, 400)
        self.view.setStyleSheet("background: #f0f0f0")

        #物体类定义

        self.selected_ball_data=None 
        self.all_ball=[]

        """         ball = QGraphicsEllipseItem(0, 0, 30, 30)
        ball.setBrush(QColor("red"))  # 修改为 QColor 处理颜色
        ball.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable,True)
        ball.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable,True)
        self.scene.addItem(ball)
        ball.setPos(300, 0)

        self.all_ball=[{"item":ball,"velocity":0,"x":300,"y":0}]
        self.all_ball.append({"item":ball,"velocity":0,"x":300,"y":0}) """

        #物理量设置

        self.gravity = 10  # 初始重力

        # 2. 控制面板
        self.start_btn = QPushButton("Start")
        self.gravity_slider = QSlider(Qt.Orientation.Horizontal)  # 正确指定横向滑动条
        self.gravity_slider.setMinimum(0)
        self.gravity_slider.setMaximum(30)
        self.gravity_slider.setValue(self.gravity)
        self.gravity_label = QLabel(f"Gravity: {self.gravity}")


        #信号与槽
        self.start_btn.clicked.connect(self.toggle_simulation)
        self.gravity_slider.valueChanged.connect(self.update_gravity)


        #这里创建了一个垂直布局，里面包含start，重力标签，以及重力条
        control_layout = QVBoxLayout()
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.gravity_label)
        control_layout.addWidget(self.gravity_slider)

        # 3. 实时图像
        self.plot = pg.PlotWidget()
        self.plot.setYRange(0, 400)
        self.plot_data = []
        self.plot_curve = self.plot.plot(self.plot_data, pen='g')

        # 布局整合，将上面的和图像结合了
        right_layout = QVBoxLayout()  #这是右侧的
        right_layout.addLayout(control_layout)
        right_layout.addWidget(self.plot)


        #最大布局，水平的
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.view)
        main_layout.addLayout(right_layout)

        central_widget.setLayout(main_layout)

        self.space=pymunk.Space()
        self.space.gravity=(0,-self.gravity)


        # 动画定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scene)
        self.running = False
        self.time = 0

    def toggle_simulation(self):
        self.running = not self.running
        if self.running:
            self.start_btn.setText("Pause")
            self.timer.start(50)
        else:
            self.start_btn.setText("Start")
            self.timer.stop()

    def reset_simulation(self):

        # 重新创建 space
        self.space = pymunk.Space()
        self.space.gravity = (0, -self.gravity)

        # 清除视图中的球
        for ball_data in self.all_ball:
            self.scene.removeItem(ball_data["item"])
        self.all_ball.clear()

        # 清空图表
        self.selected_ball_data = None
        self.plot_data.clear()
        self.plot_curve.setData([])

        self.running=False
        self.timer.stop()
        self.time=0


    def add_ball(self):
        radius = 15
        mass = 1
        moment = pymunk.moment_for_circle(mass, 0, radius)

        body = pymunk.Body(mass, moment)
        body.position = (100, 100)
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 0.7
        shape.friction = 0.5

        self.space.add(body, shape)

        ball = QGraphicsEllipseItem(0, 0, 30, 30)
        ball.setBrush(QColor("blue"))
        ball.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, True)
        ball.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.scene.addItem(ball)
        ball.mousePressEvent = lambda event, b=ball: self.select_ball(b)
        ball.setPos(body.position[0], 600 - body.position[1])

        # 在鼠标拖动时，持续更新物理引擎中的位置

        ball.setAcceptHoverEvents(True)

        def drag_ball(event):
            mouse_pos = event.scenePos()
            body.position = mouse_pos.x(), 600 - mouse_pos.y()  # 更新物理位置
            ball.setPos(mouse_pos.x(), mouse_pos.y())  # 更新图形位置

        ball.mouseMoveEvent = drag_ball

        self.all_ball.append({"item": ball, "body": body, "shape": shape})


    def update_gravity(self, value):
        self.gravity = value
        self.space.gravity=(0,-value)
        self.gravity_label.setText(f"Gravity: {value}")


    def select_ball(self,ball_item):
        for ball_data in self.all_ball:
            if ball_data["item"]==ball_item:
                self.selected_ball_data=ball_data
                body=ball_data["body"]
                item=ball_data["item"]
                body.position=item.pos().x(),600-item.pos().y()
                
                break

    def quit_select(self):
        self.selected_ball_data=None
    
    def delete_selected_ball(self):
        if self.selected_ball_data:
            ball=self.selected_ball_data["item"]
            body=self.selected_ball_data["body"]
            shape=self.selected_ball_data["shape"]
            self.scene.removeItem(ball)#从scene中移除图形
            self.all_ball.remove(self.selected_ball_data)#从数据结构中移除这个球
            self.selected_ball_data=None
            self.plot_data.clear()
            self.plot_curve.setData([])


            self.space.remove(body,shape)


            print("Deleted selected ball.")
        else:
            print("No ball selected to delete.")

    def update_scene(self):
        #推进物理模拟
        self.space.step(0.05)


        for ball_data in self.all_ball:
            item=ball_data["item"]
            body=ball_data["body"]
            pos =body.position
            item.setPos(pos[0],600-pos[1])


            if self.selected_ball_data and self.selected_ball_data["item"]==item:

                self.plot_data.append(pos[1])
                if len(self.plot_data) > 100:
                    self.plot_data = self.plot_data[-100:]
                self.plot_curve.setData(self.plot_data)  

def main():
    app = QApplication(sys.argv)  # 创建应用程序
    window = MainWindow()  # 创建窗口
    window.show()  # 显示窗口
    sys.exit(app.exec())  # 启动应用程序的事件循环

if __name__ == "__main__":
    main()
