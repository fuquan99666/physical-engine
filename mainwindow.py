import pymunk
import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QSlider,
    QVBoxLayout, QHBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsLineItem, QToolBar, QGraphicsRectItem,QSplitter,QMenu,
    QDialog,QFormLayout,QLineEdit,QDialogButtonBox,QCheckBox,QColorDialog,QInputDialog, QTreeView,QScrollArea, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer, QPointF,QDir
from PyQt6.QtGui import QColor, QAction, QPen, QPainter, QFileSystemModel
import pyqtgraph as pg
import os
from add_object_dialog import AddObjectDialog
from simulator import PhysicsSimulator as ph
import drawmap
import sqlite3
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2D Physics Engine UI")
        self.resize(1200, 700)

        self.gravity = 10
        self.F=10
        self.simulator = ph()
        self.simulator.space.gravity = (self.F, -self.gravity)
        
        self.simulator.space.collision_slop = 0.01
        self.spring_update_counter=0
        self.init_menubar()
        self.toolbar = QToolBar("Main ToolBar")
        self.addToolBar(self.toolbar)
       
        self._init_toolbar()
        self._init_ui()
        self.monitor_path='./dataset/'

        self.init_file_browser()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scene)
        self.running = False
        self.time = 0

        self.spring_selection = None
        self.springs = []

    def init_file_browser(self):
        """初始化文件浏览器侧边栏"""
        # 创建文件浏览器容器
        self.file_browser = QWidget()
        self.file_browser.setMinimumWidth(170)
        browser_layout = QVBoxLayout(self.file_browser)
        
        # 添加标题和刷新按钮
        title_bar = QHBoxLayout()
        self.path_label = QLabel("历史数据")
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.update_file_buttons)
        title_bar.addWidget(self.path_label)
        title_bar.addWidget(refresh_btn)
        browser_layout.addLayout(title_bar)

        # 创建可滚动区域
        scroll = QScrollArea()
        self.button_container = QWidget()
        self.button_layout = QVBoxLayout(self.button_container)
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.button_container)
        scroll.setWidgetResizable(True)
        browser_layout.addWidget(scroll)

        # 初始化按钮组和定时器
        self.button_group = QButtonGroup()
        self.button_group.buttonClicked.connect(self.on_file_button_clicked)
        self.update_file_buttons()

        # # 设置定时刷新（每2秒）
        self.file_timer = QTimer()
        self.file_timer.timeout.connect(self.update_file_buttons)
        self.file_timer.start(2000)

        # 将文件浏览器添加到主界面
        self.splitter.insertWidget(0, self.file_browser)  # 根据QSplitter结构调整

    def update_file_buttons(self):
        """更新文件按钮列表
        只需要在创建和另存为的时候调用
        """
        # 清空现有按钮
        while self.button_layout.count():
            child = self.button_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 生成新按钮
        dir = QDir(self.monitor_path)
        for file_info in dir.entryInfoList(QDir.Filter.NoDotAndDotDot | QDir.Filter.AllEntries):
            btn = QPushButton(file_info.fileName())
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: middle; 
                    padding: 5px;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                }
                QPushButton:hover { background-color: #b0b0b0; }
                QPushButton:checked { background-color: #a0a0a0; }
            """)
            btn.setToolTip(file_info.absoluteFilePath())
            self.button_group.addButton(btn)
            self.button_layout.addWidget(btn)

    def on_file_button_clicked(self, button):
        """文件按钮点击处理"""
        file_path = button.toolTip().split('/')[-1]
        print(f"选中文件：{file_path}")
        drawmap.pic_for_all(file_path)
        # 后续可添加双击打开等逻辑
    def loading_new_files(self):
        #清空所有的画面并加载新画面。
        #且让我想想怎么写
        pass
    def init_menubar(self):
         # 创建菜单栏
        menu_bar = self.menuBar()
        
        # 创建文件菜单
        file_menu = menu_bar.addMenu("文件(&F)")
        # 添加菜单项
        new_action = QAction("新建(&N)", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        save_action=QAction("保存(&S)...",self)
        save_action.triggered.connect(self.save)
        file_menu.addAction(save_action)

        save_as_action=QAction("另存为",self)
        save_as_action.triggered.connect(self.save_as)
        file_menu.addAction(save_as_action)
        # 添加分隔线
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        #将添加物品的代码向上移动
        #添加圆，矩形和线段
        create_menu=menu_bar.addMenu("添加(&A)")
        for obj_type in ["Circle","Box","Segment"]:
            action=QAction(obj_type,self)
            action.triggered.connect(lambda checked,t=obj_type:self.add_object_with_defaults(t))
            create_menu.addAction(action)
        #添加弹簧
        create_spring=QAction("spring",self)
        create_spring.triggered.connect(self.prepare_add_spring)
        create_menu.addAction(create_spring)

        #帮助菜单（暂时还没有什么用）
        file_menu=menu_bar.addMenu("帮助(&H)")

    def _init_toolbar(self):
        actions = [
            ("Start/Pause", self.toggle_simulation),
            ("Reset", self.reset_simulation),
            ("Delete Selected", self.delete_selected_item),
            ("Quit Selected", self.quit_select),
            
        ]
        for name, slot in actions:
            action = QAction(name, self)
            action.triggered.connect(slot)
            self.toolbar.addAction(action)
        
        edit_action=QAction("Edit Selected",self)
        edit_action.triggered.connect(self.edit_selected_object)
        self.toolbar.addAction(edit_action)

    def new_file(self):
        self.simulator.data_handler.create_initial_file()
        self.update_file_buttons()#在创建新文件后再更新
    def open_file(self,index):
        path = self.model.filePath(index)
        if os.path.isfile(path):
            try:
                # 这里可以添加实际的文件打开逻辑
                self.statusBar().showMessage(f"已打开文件: {path}", 3000)
                print(f"打开文件: {path}")
                
              
            except Exception as e:
                self.statusBar().showMessage(f"打开失败: {str(e)}", 5000)
        else:
            self.statusBar().showMessage(f"已展开目录: {path}", 2000)
    def add_object_with_defaults(self,obj_type):
        x,y=300,300
        mass=30
        is_static=False

        if obj_type=="Circle":
            radius=30
            body,shape=self.simulator.add_circle(x,y,mass,radius)
            item=QGraphicsEllipseItem(-radius,-radius,2*radius,2*radius)
        elif obj_type=="Box":
            width,height=60,60
            body,shape=self.simulator.add_box(x,y,width,height,mass)
            item=QGraphicsRectItem(-width/2,-height/2,width,height)
        elif obj_type=="Segment":
            start=pymunk.Vec2d(x,y)
            end=pymunk.Vec2d(x+100,y)
            body,shape=self.simulator.add_segment(start,end,mass,radius=5,static=is_static)
            item=QGraphicsLineItem()
        else:
            return 
        self._configure_item(item,body,shape,is_static)
        self.all_item.append({"item":item,"body":body,"shape":shape})
        self.scene.addItem(item)
        self.update_graphics_position(item,body,shape,force=True)

    def edit_selected_object(self):
        if not self.selected_item_data:
            return 

        body = self.selected_item_data["body"]
        shape = self.selected_item_data["shape"]
        item = self.selected_item_data["item"]
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Object")
        layout = QFormLayout(dialog)

        # ---- 基础属性 ----
        pos_x = QLineEdit(str(body.position.x))
        pos_y = QLineEdit(str(body.position.y))
        vel_x = QLineEdit(str(body.velocity.x))
        vel_y = QLineEdit(str(body.velocity.y))
        mass = QLineEdit(str(body.mass) if body.mass != float("inf") else "0")

        is_static_checkbox = QCheckBox()
        is_static_checkbox.setChecked(body.body_type == pymunk.Body.STATIC)

        current_color = self.selected_item_data.get("color", "#00ff00")
        color = QColor(current_color)
        color_button = QPushButton()
        color_button.setStyleSheet(f"background-color: {color.name()}")

        def choose_color():
            nonlocal color
            new_color = QColorDialog.getColor(color, self)
            if new_color.isValid():
                color = new_color
                color_button.setStyleSheet(f"background-color: {color.name()}")

        color_button.clicked.connect(choose_color)

        # ---- 添加控件 ----
        layout.addRow("Position X:", pos_x)
        layout.addRow("Position Y:", pos_y)
        layout.addRow("Velocity X:", vel_x)
        layout.addRow("Velocity Y:", vel_y)
        layout.addRow("Mass:", mass)
        layout.addRow("Is Static:", is_static_checkbox)
        layout.addRow("Color:", color_button)

        # ---- 形状参数 ----
        shape_type = type(shape)
        radius_input = None
        width_input = None
        height_input = None

        if isinstance(shape, pymunk.Circle):
            radius_input = QLineEdit(str(shape.radius))
            layout.addRow("Radius:", radius_input)
        elif isinstance(shape, pymunk.Poly):
            # 只支持矩形（4点）识别宽高
            vertices = shape.get_vertices()
            if len(vertices) == 4:
                global_vertices = [body.local_to_world(v) for v in shape.get_vertices()]

                # 按顺序取出前两个顶点，计算宽高方向向量
                v0, v1, v2, v3 = global_vertices

                width_vector = v1 - v0
                height_vector = v2 - v1


                width = width_vector.length
                height = height_vector.length

              
                width_input = QLineEdit(str(width))
                height_input = QLineEdit(str(height))
                layout.addRow("Width:", width_input)
                layout.addRow("Height:", height_input)
                angle=math.degrees(body.angle)
                angle_input=QLineEdit(str(angle))
                layout.addRow("Angle:",angle_input)
        elif isinstance(shape,pymunk.Segment):
            # 获取当前长度和角度
            vec = shape.b - shape.a#没毛病
            current_length = vec.length
            current_angle_deg = math.degrees(body.angle)

            length_input = QLineEdit(str(current_length))
            angle_input = QLineEdit(str(current_angle_deg))
            layout.addRow("Length:", length_input)
            layout.addRow("Angle (°):", angle_input)

        # ---- 确认/取消按钮 ----
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        # ---- 用户确认 ----
        if dialog.exec():
            try:
                x = float(pos_x.text())
                y = float(pos_y.text())
                vx = float(vel_x.text())
                vy = float(vel_y.text())
                m = float(mass.text())

                body.position = x, y
                body.velocity = vx, vy

                #连接到相关数据库，准备更新属性
                conn=sqlite3.connect(self.simulator.data_handler.current_file)
                cursor=conn.cursor()
                item_idx=self.all_item.index(self.selected_item_data)

                if is_static_checkbox.isChecked():
                    body.body_type = pymunk.Body.STATIC
                    #body.mass = float("inf")
                else:
                    body.body_type = pymunk.Body.DYNAMIC
                    body.mass = m

                is_static=is_static_checkbox.isChecked()

                # 更新颜色
                if isinstance(item, QGraphicsLineItem):
                    pen = item.pen()
                    pen.setColor(color)
                    item.setPen(pen)
                else:
                    item.setBrush(color)
                self.selected_item_data["color"] = color.name()

                # 更新形状（仅支持简单调整）
                if isinstance(shape, pymunk.Circle) and radius_input:
                    new_radius = float(radius_input.text())
                    shape.unsafe_set_radius(new_radius)
                    if(not is_static):
                        body.moment = pymunk.moment_for_circle(mass, 0, new_radius)
                    item.setRect(-new_radius,-new_radius,2*new_radius,2*new_radius)
                    sql = "UPDATE circle_properties SET radius = ? WHERE obj_id = ?"
                    cursor.execute(sql,(new_radius,item_idx))
                    

                elif isinstance(shape, pymunk.Poly):
                    new_width = float(width_input.text())
                    new_height = float(height_input.text())
                    new_angle=float(angle_input.text())
                    new_angle_rad = math.radians(new_angle)
                    if(not is_static):
                        body.moment=pymunk.moment_for_box(m,(new_width,new_height))

                    new_shape=pymunk.Poly.create_box(body,(new_width,new_height))
                    new_shape.elasticity=shape.elasticity
                    self.simulator.space.remove(shape)
                    self.simulator.space.add(new_shape)
                    self.selected_item_data["shape"]=new_shape
                    body.angle=new_angle_rad
                    item.setRect(-new_width/2,-new_height/2,new_width,new_height)
                    sql = "UPDATE polygon_properties SET height=?,width=? WHERE obj_id = ?"
                    cursor.execute(sql,(new_height,new_width,item_idx))

                elif isinstance(shape, pymunk.Segment) and length_input and angle_input:
                    new_length = float(length_input.text())
                    new_angle_deg = float(angle_input.text())
                    new_angle_rad = math.radians(new_angle_deg)

                    direction = pymunk.Vec2d(1, 0)
                    half_vec = direction * (new_length / 2)
                    new_a = -half_vec
                    new_b = half_vec

                    new_shape = pymunk.Segment(body, new_a, new_b, shape.radius)
                    new_shape.elasticity = shape.elasticity

                    self.simulator.space.remove(shape)
                    self.simulator.space.add(new_shape)
                    self.selected_item_data["shape"] = new_shape

                    # 更新 body 角度
                    body.angle = new_angle_rad
                    shape=new_shape
                    #此处的数据更改尚未完成，因为有点复杂，可能需要修改segment的存储代码结构
                    item.setLine(new_shape.a.x, new_shape.a.y, new_shape.b.x, new_shape.b.y)
                item.setFlag(item.GraphicsItemFlag.ItemIsMovable, not is_static)


                if not is_static:
                    item.mouseMoveEvent = lambda e, b=item, bd=body,s=shape: self.drag_item(b, bd,s, e)
                else:
                    item.mouseMoveEvent= lambda e,b=item,bd=body,s=shape: None
                self.update_graphics_position(item, body,shape, force=True)
                conn.commit()
                conn.close()
            except ValueError:
                print("Invalid input.")


    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 600, 600)
        self.view = QGraphicsView(self.scene)
        self.view.setMinimumSize(400, 400)
        self.view.setStyleSheet("background: #f0f0f0")
        self.view.setRenderHints(QPainter.RenderHint.Antialiasing)

        self.selected_item_data = None
        self.all_item = []

        self.start_btn = QPushButton("Start")
        self.gravity_slider = QSlider(Qt.Orientation.Horizontal)
        self.gravity_slider.setRange(-100, 100)
        self.gravity_slider.setValue(self.gravity)
        self.gravity_label = QLabel(f"Gravity: {self.gravity}")

        self.start_btn.clicked.connect(self.toggle_simulation)
        self.gravity_slider.valueChanged.connect(self.update_gravity)

        self.H_slider=QSlider(Qt.Orientation.Horizontal)
        self.H_slider.setRange(-100,100)
        self.H_slider.setValue(self.F)
        self.H_label = QLabel(f"水平力: {self.F}")

        self.H_slider.valueChanged.connect(self.update_F)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.gravity_label)
        control_layout.addWidget(self.gravity_slider)

        control_layout.addWidget(self.H_label)
        control_layout.addWidget(self.H_slider)

        self.plot = pg.PlotWidget()
        self.plot.setYRange(0, 400)
        self.plot_data = []
        self.plot_curve = self.plot.plot(self.plot_data, pen='g')

        right_layout = QVBoxLayout()
        right_layout.addLayout(control_layout)
        right_layout.addWidget(self.plot)

        right_widget=QWidget()
        right_widget.setLayout(right_layout)

        self.splitter=QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.view)
        self.splitter.addWidget(right_widget)
        self.splitter.setSizes([800,400])

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.splitter)


        central_widget.setLayout(main_layout)

    def toggle_simulation(self):
        self.running = not self.running
        self.start_btn.setText("Pause" if self.running else "Start")
        if self.running:
            self.timer.start(16)
        else:
            self.timer.stop()

    def reset_simulation(self):
        self.simulator = ph()
        self.update_F(10)
        self.update_gravity(10)

        for obj in self.all_item:
            self.scene.removeItem(obj["item"])
        self.all_item.clear()

        self.selected_item_data = None
        self.plot_data.clear()
        self.plot_curve.setData([])

        self.running = False
        self.timer.stop()
        self.time = 0
        

    def update_gravity(self, value):
        self.gravity = value
        self.simulator.space.gravity = (self.F, -self.gravity)
        self.gravity_label.setText(f"Gravity: {value}")
        self.gravity_slider.setValue(self.gravity)
    
    def update_F(self,value):
        self.F=value
        self.simulator.space.gravity=(self.F,-self.gravity)
        self.H_label.setText(f"水平力: {value}")
        self.H_slider.setValue(self.F)




    def _configure_item(self, item, body,shape, is_static):
        if hasattr(item, 'setBrush'):
            item.setBrush(QColor("green"))
        if isinstance(item, QGraphicsLineItem):

            pen = QPen(QColor("green"))
            pen.setWidthF(shape.radius * 2)
            item.setPen(pen)

        item.setFlag(item.GraphicsItemFlag.ItemIsMovable, not is_static)
        item.setFlag(item.GraphicsItemFlag.ItemIsSelectable, True)
        item.setAcceptHoverEvents(True)


        def on_mouse_press(e, b=item):
            if e.button() == Qt.MouseButton.RightButton:
                self.select_item(b)
                self.edit_selected_object()  # 弹出属性编辑窗口
            elif e.button() == Qt.MouseButton.LeftButton:
                self.select_item(b)

        item.mousePressEvent = on_mouse_press

        if not is_static:
            item.mouseMoveEvent = lambda e, b=item, bd=body,s=shape: self.drag_item(b, bd,s, e)

    def drag_item(self, item, body,shape, event):
        pos = event.scenePos()
        body.position = (pos.x(), 600 - pos.y())
        body.velocity = (0, 0)  # 停止速度防止跳动
        self.update_graphics_position(item, body,shape, force=True)
        for spring,line in self.springs:
            if spring.a is body or spring.b is body:
                self.update_spring_line_with_smoothing(spring,line,1)
    def update_graphics_position(self, item, body,shape, force=False):
        if isinstance(item, QGraphicsLineItem):
          

            a = body.position + shape.a.rotated(body.angle)
            b = body.position + shape.b.rotated(body.angle)


            item.setLine(a.x, 600 - a.y, b.x, 600 - b.y)

        elif isinstance(item,QGraphicsEllipseItem):
            x, y = body.position.x, 600 - body.position.y
            target_pos = QPointF(x, y)
            if force or not hasattr(item, 'last_pos'):
                item.setPos(target_pos)
                item.last_pos = target_pos
            else:
                current_pos = item.last_pos
                smoothed = current_pos * 0.7 + target_pos * 0.3  #这个是平缓插值
                item.setPos(smoothed)
                item.last_pos = smoothed
        elif isinstance(item,QGraphicsRectItem):
            x, y = body.position.x, 600 - body.position.y
            target_pos = QPointF(x, y)

            if force or not hasattr(item, 'last_pos'):
                item.setPos(target_pos)
                item.last_pos = target_pos
                item.setRotation(-math.degrees(body.angle))
            else:
                current_pos = item.last_pos
                smoothed = current_pos * 0.7 + target_pos * 0.3
                item.setPos(smoothed)
                item.last_pos = smoothed
                item.setRotation(-math.degrees(body.angle))  

    def select_item(self, item):
        for entry in self.all_item:
            if entry["item"] == item:#此处找到all_item列表中的item元素
                self.selected_item_data = entry
                if self.spring_selection is not None:
                    self.spring_selection.append(entry)
                    if len(self.spring_selection) == 2:
                        self.add_spring_between_bodies()
                        self.spring_selection = None
                        self.statusBar().clearMessage()
                break
    def add_spring_between_bodies(self):
        e1, e2 = self.spring_selection
        b1, b2 = e1["body"], e2["body"]
        if b1 is b2:
            print("Cannot connect a spring to the same object!")
            return
        spring = self.simulator.add_spring(
            b1, b2,
            stiffness=100, damping=6,
            anchor1=(0, 0), anchor2=(0, 0),
            rest_length=(b1.position - b2.position).length
        )
        line = QGraphicsLineItem()
        pen = QPen(QColor("red"))
        pen.setWidth(5)
        line.setPen(pen)
        self.scene.addItem(line)
        self.springs.append((spring, line))
        self.update_spring_line_with_smoothing(spring,line,1)
        print("Spring created. Click Start to see it in action.")

    def quit_select(self):
        self.selected_item_data = None

    def delete_selected_item(self):
        if not self.selected_item_data:
            return
        item = self.selected_item_data["item"]
        body = self.selected_item_data["body"]
        shape=self.selected_item_data["shape"]
        self.scene.removeItem(item)
        self.simulator.space.remove(body,shape)
        self.all_item.remove(self.selected_item_data)
        self.selected_item_data = None
        self.plot_data.clear()
        self.plot_curve.setData([])

    def prepare_add_spring(self):
        self.spring_selection = []
        self.statusBar().showMessage("Select two objects to add a spring.")


    def update_spring_line_with_smoothing(self, spring, line, base_alpha=0.3, max_alpha=1.0, speed_scale=500.0):
        # 获取物理位置
        a = spring.a.position + spring.anchor_a.rotated(spring.a.angle)
        b = spring.b.position + spring.anchor_b.rotated(spring.b.angle)

        # 当前绘制的位置（scene 坐标）
        current_a = line.line().p1()
        current_b = line.line().p2()

        current_a = pymunk.Vec2d(current_a.x(), 600 - current_a.y())  # 注意转换坐标系
        current_b = pymunk.Vec2d(current_b.x(), 600 - current_b.y())

        # 根据两个端点的速度调整 alpha（用相对速度估计动态程度）
        relative_velocity = (spring.a.velocity - spring.b.velocity).length
        dynamic_alpha = min(base_alpha + (relative_velocity / speed_scale), max_alpha)

        # 插值
        smoothed_a = current_a * (1 - dynamic_alpha) + a * dynamic_alpha
        smoothed_b = current_b * (1 - dynamic_alpha) + b * dynamic_alpha

        # 设置线段
        line.setLine(smoothed_a.x, 600 - smoothed_a.y, smoothed_b.x, 600 - smoothed_b.y)
    def save(self):
        try:
            self.simulator.data_handler.save()
        except Exception as e:
            print(e)
    def save_as(self):
        try:
            self.simulator.data_handler.save_as()
            self.update_file_buttons()
        except Exception as e:
            print(e)

    def update_scene(self):
        for _ in range(10):  # 多步模拟提升平滑度
            self.simulator.step(1 / 600.0)

        for entry in self.all_item:
            item = entry["item"]
            body = entry["body"]
            shape=entry["shape"]
            self.update_graphics_position(item, body,shape)

            if self.selected_item_data and self.selected_item_data["item"] == item:
                self.plot_data.append(body.position.y)
                if len(self.plot_data) > 100:
                    self.plot_data = self.plot_data[-100:]
                self.plot_curve.setData(self.plot_data)
        self.spring_update_counter+=1
        if self.spring_update_counter%2==0:
            for spring, line in self.springs:
                self.update_spring_line_with_smoothing(spring,line)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
