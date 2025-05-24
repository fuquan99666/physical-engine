import pymunk
import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QSlider,
    QVBoxLayout, QHBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsLineItem, QToolBar, QGraphicsRectItem,QSplitter,QMenu,
    QDialog,QFormLayout,QLineEdit,QDialogButtonBox,QCheckBox,QColorDialog
)
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QColor, QAction, QPen, QPainter
import pyqtgraph as pg

from add_object_dialog import AddObjectDialog
from simulator import PhysicsSimulator as ph


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2D Physics Engine UI")
        self.resize(1200, 700)

        self.gravity = 10
        self.simulator = ph()
        self.simulator.space.gravity = (0, -self.gravity)
        self.simulator.space.collision_slop = 0.01
        self.spring_update_counter=0

        self.toolbar = QToolBar("Main ToolBar")
        self.addToolBar(self.toolbar)

        self._init_toolbar()
        self._init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scene)
        self.running = False
        self.time = 0

        self.spring_selection = None
        self.springs = []

    def _init_toolbar(self):
        actions = [
            ("Start/Pause", self.toggle_simulation),
            ("Reset", self.reset_simulation),
            ("Delete Selected", self.delete_selected_item),
            ("Quit Selected", self.quit_select),
            ("Add Spring", self.prepare_add_spring)
        ]
        for name, slot in actions:
            action = QAction(name, self)
            action.triggered.connect(slot)
            self.toolbar.addAction(action)

        add_object_menu=QMenu("Add Object",self)
        for obj_type in ["Circle","Box","Segment"]:
            action=QAction(obj_type,self)
            action.triggered.connect(lambda checked,t=obj_type:self.add_object_with_defaults(t))
            add_object_menu.addAction(action)
        
        add_object_button=QAction("Add Qbject",self)
        add_object_button.setMenu(add_object_menu)
        self.toolbar.addAction(add_object_button)

        edit_action=QAction("Edit Selected",self)
        edit_action.triggered.connect(self.edit_selected_object)
        self.toolbar.addAction(edit_action)

    
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

                #angle = width_vector.angle 
                width_input = QLineEdit(str(width))
                height_input = QLineEdit(str(height))
                layout.addRow("Width:", width_input)
                layout.addRow("Height:", height_input)
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

                    item.setRect(-new_radius,-new_radius,2*new_radius,2*new_radius)
                    

                elif isinstance(shape, pymunk.Poly):
                    new_width = float(width_input.text())
                    new_height = float(height_input.text())
                    if(not is_static):
                        body.moment=pymunk.moment_for_box(m,(new_width,new_height))

                    new_shape=pymunk.Poly.create_box(body,(new_width,new_height))
                    new_shape.elasticity=shape.elasticity
                    self.simulator.space.remove(shape)
                    self.simulator.space.add(new_shape)
                    self.selected_item_data["shape"]=new_shape

                    item.setRect(-new_width/2,-new_height/2,new_width,new_height)

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

                    shape=new_shape
                    body.angle=new_angle_rad

                    item.setLine(new_shape.a.x, new_shape.a.y, new_shape.b.x, new_shape.b.y)
                item.setFlag(item.GraphicsItemFlag.ItemIsMovable, not is_static)


                if not is_static:
                    item.mouseMoveEvent = lambda e, b=item, bd=body,s=shape: self.drag_item(b, bd,s, e)
                else:
                    item.mouseMoveEvent= lambda e,b=item,bd=body,s=shape: None
                self.update_graphics_position(item, body,shape, force=True)

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

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.gravity_label)
        control_layout.addWidget(self.gravity_slider)

        self.plot = pg.PlotWidget()
        self.plot.setYRange(0, 400)
        self.plot_data = []
        self.plot_curve = self.plot.plot(self.plot_data, pen='g')

        right_layout = QVBoxLayout()
        right_layout.addLayout(control_layout)
        right_layout.addWidget(self.plot)

        right_widget=QWidget()
        right_widget.setLayout(right_layout)

        splitter=QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.view)
        splitter.addWidget(right_widget)
        splitter.setSizes([800,400])

        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter)


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
        self.simulator.space.gravity = (0, -self.gravity)

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
        self.simulator.space.gravity = (0, -value)
        self.gravity_label.setText(f"Gravity: {value}")




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
            else:
                current_pos = item.last_pos
                smoothed = current_pos * 0.7 + target_pos * 0.3
                item.setPos(smoothed)
                item.last_pos = smoothed
                item.setRotation(-math.degrees(body.angle))  

    def select_item(self, item):
        for entry in self.all_item:
            if entry["item"] == item:
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
        for spring,line in self.springs:
            if spring.a is body or spring.b is body:
                self.scene.removeItem(line)
                self.simulator.space.remove(spring)
                self.springs.remove((spring,line))#从弹簧组中移除
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


    def update_scene(self):
        for _ in range(10):  # 多步模拟提升平滑度
            self.simulator.space.step(1 / 600.0)

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
