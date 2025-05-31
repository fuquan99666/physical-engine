import pymunk
import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QSlider,
    QVBoxLayout, QHBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsLineItem, QToolBar, QGraphicsRectItem, QSplitter, QMenu,
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QCheckBox, QColorDialog, QInputDialog, QTreeView, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QPointF, QDir
from PyQt6.QtGui import QColor, QAction, QPen, QPainter, QFileSystemModel
import pyqtgraph as pg
import os
from add_object_dialog import AddObjectDialog
from core.simulator import PhysicsSimulator as ph

from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl


class HomePage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("物理引擎模拟系统")
        self.resize(1200, 700)

        # 设置背景视频
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.5)
        self.media_player.setAudioOutput(self.audio_output)
        self.video_widget = QVideoWidget()

        # 创建主容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 添加视频背景
        layout.addWidget(self.video_widget)

        # 创建按钮容器
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_container.setStyleSheet("background-color: rgba(0, 0, 0, 150); border-radius: 15px;")
        button_container.setFixedSize(300, 200)

        # 创建按钮
        self.start_btn = QPushButton("开始")
        self.history_btn = QPushButton("历史记录")

        # 设置按钮样式
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        self.start_btn.setStyleSheet(button_style)
        self.history_btn.setStyleSheet(button_style)

        # 添加按钮到布局
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.history_btn)

        # 添加按钮容器到主布局
        layout.addWidget(button_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # 设置背景视频
        self.load_background_video()

        # 连接信号
        self.start_btn.clicked.connect(self.open_simulator)
        self.history_btn.clicked.connect(self.show_history)

    def load_background_video(self):
        # 这里应该替换为实际的视频路径
        # 如果没有视频文件，可以使用在线视频URL
        video_path = "background_video.mp4"  # 本地视频文件

        if os.path.exists(video_path):
            self.media_player.setSource(QUrl.fromLocalFile(video_path))
        else:
            # 如果没有视频文件，使用默认颜色背景
            self.video_widget.setStyleSheet(
                "background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a2a6c, stop:1 #b21f1f);")
            return

        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.play()
        self.media_player.setLoops(QMediaPlayer.Loops.Infinite)  # 循环播放

    def open_simulator(self):
        #不再播放视频
        self.media_player.stop()
        self.media_player.setSource(QUrl())


        self.simulator = PhysicsSimulatorWindow()
        self.simulator.show()
        self.hide()

    def show_history(self):
        # 这里可以添加历史记录功能
        QMessageBox.information(self, "历史记录", "历史记录功能将在后续版本中实现", QMessageBox.StandardButton.Ok)

class PhysicsSimulatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2D Physics Engine UI")
        self.resize(1200, 700)

        self.gravity = 10
        self.simulator = ph()
        self.simulator.space.gravity = (0, -self.gravity)
        self.simulator.space.collision_slop = 0.01
        self.spring_update_counter = 0
        self.init_menubar()
        self.toolbar = QToolBar("Main ToolBar")
        self.addToolBar(self.toolbar)
        # self.init_file_browser()
        self._init_toolbar()
        self._init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scene)
        self.running = False
        self.time = 0

        self.spring_selection = None
        self.springs = []

    # def init_file_browser(self):
    #     """初始化文件浏览器侧边栏"""
    #     # 创建文件系统模型
    #     self.model = QFileSystemModel()
    #     self.model.setRootPath(QDir.currentPath())  # 设置初始目录

    #     # 创建树形视图
    #     self.tree_view = QTreeView()
    #     self.tree_view.setModel(self.model)
    #     self.tree_view.setRootIndex(self.model.index(QDir.currentPath()))
    #     self.tree_view.doubleClicked.connect(self.open_file)

    #     # 设置列宽和显示选项
    #     self.tree_view.setColumnWidth(0, 300)  # 名称列宽度
    #     self.tree_view.setHeaderHidden(False)   # 显示表头
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

        save_action = QAction("保存(&S)...", self)
        save_action.triggered.connect(self.save)
        file_menu.addAction(save_action)

        save_as_action = QAction("另存为", self)
        save_as_action.triggered.connect(self.save_as)
        file_menu.addAction(save_as_action)
        # 添加分隔线
        file_menu.addSeparator()

        exit_action = QAction("退出(&X)", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        # 将添加物品的代码向上移动
        # 添加圆，矩形和线段
        create_menu = menu_bar.addMenu("添加(&A)")
        for obj_type in ["Circle", "Box", "Segment"]:
            action = QAction(obj_type, self)
            action.triggered.connect(lambda checked, t=obj_type: self.add_object_with_defaults(t))
            create_menu.addAction(action)
        # 添加弹簧
        create_spring = QAction("spring", self)
        create_spring.triggered.connect(self.prepare_add_spring)
        create_menu.addAction(create_spring)

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

        edit_action = QAction("Edit Selected", self)
        edit_action.triggered.connect(self.edit_selected_object)
        self.toolbar.addAction(edit_action)

    def new_file(self):
        self.simulator.data_handler.create_initial_file()

    def open_file(self, index):
        path = self.model.filePath(index)
        if os.path.isfile(path):
            try:
                # 这里可以添加实际的文件打开逻辑
                self.statusBar().showMessage(f"已打开文件: {path}", 3000)
                print(f"打开文件: {path}")

                # 示例：读取文本文件内容
                # with open(path, 'r') as f:
                #     print(f.read())

            except Exception as e:
                self.statusBar().showMessage(f"打开失败: {str(e)}", 5000)
        else:
            self.statusBar().showMessage(f"已展开目录: {path}", 2000)

    def add_object_with_defaults(self, obj_type):
        x, y = 300, 300
        mass = 30
        is_static = False

        if obj_type == "Circle":
            radius = 30
            body, shape = self.simulator.add_circle(x, y, mass, radius)
            item = QGraphicsEllipseItem(-radius, -radius, 2 * radius, 2 * radius)
        elif obj_type == "Box":
            width, height = 60, 60
            body, shape = self.simulator.add_box(x, y, width, height, mass)
            item = QGraphicsRectItem(-width / 2, -height / 2, width, height)
        elif obj_type == "Segment":
            start = pymunk.Vec2d(x, y)
            end = pymunk.Vec2d(x + 100, y)
            body, shape = self.simulator.add_segment(start, end, mass, radius=5, static=is_static)
            item = QGraphicsLineItem()
        else:
            return
        self._configure_item(item, body, shape, is_static)
        self.all_item.append({"item": item, "body": body, "shape": shape})
        self.scene.addItem(item)
        self.update_graphics_position(item, body, shape, force=True)

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

                # angle = width_vector.angle
                width_input = QLineEdit(str(width))
                height_input = QLineEdit(str(height))
                layout.addRow("Width:", width_input)
                layout.addRow("Height:", height_input)
        elif isinstance(shape, pymunk.Segment):
            # 获取当前长度和角度
            vec = shape.b - shape.a  # 没毛病
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
                    # body.mass = float("inf")
                else:
                    body.body_type = pymunk.Body.DYNAMIC
                    body.mass = m

                is_static = is_static_checkbox.isChecked()

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

                    item.setRect(-new_radius, -new_radius, 2 * new_radius, 2 * new_radius)


                elif isinstance(shape, pymunk.Poly):
                    new_width = float(width_input.text())
                    new_height = float(height_input.text())
                    if (not is_static):
                        body.moment = pymunk.moment_for_box(m, (new_width, new_height))

                    new_shape = pymunk.Poly.create_box(body, (new_width, new_height))
                    new_shape.elasticity = shape.elasticity
                    self.simulator.space.remove(shape)
                    self.simulator.space.add(new_shape)
                    self.selected_item_data["shape"] = new_shape

                    item.setRect(-new_width / 2, -new_height / 2, new_width, new_height)

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
                    shape = new_shape

                    item.setLine(new_shape.a.x, new_shape.a.y, new_shape.b.x, new_shape.b.y)
                item.setFlag(item.GraphicsItemFlag.ItemIsMovable, not is_static)

                if not is_static:
                    item.mouseMoveEvent = lambda e, b=item, bd=body, s=shape: self.drag_item(b, bd, s, e)
                else:
                    item.mouseMoveEvent = lambda e, b=item, bd=body, s=shape: None
                self.update_graphics_position(item, body, shape, force=True)

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

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.view)
        splitter.addWidget(right_widget)
        splitter.setSizes([800, 400])

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

    def _configure_item(self, item, body, shape, is_static):
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
            item.mouseMoveEvent = lambda e, b=item, bd=body, s=shape: self.drag_item(b, bd, s, e)

    def drag_item(self, item, body, shape, event):
        pos = event.scenePos()
        body.position = (pos.x(), 600 - pos.y())
        body.velocity = (0, 0)  # 停止速度防止跳动
        self.update_graphics_position(item, body, shape, force=True)
        for spring, line in self.springs:
            if spring.a is body or spring.b is body:
                self.update_spring_line_with_smoothing(spring, line, 1)

    def update_graphics_position(self, item, body, shape, force=False):
        if isinstance(item, QGraphicsLineItem):

            a = body.position + shape.a.rotated(body.angle)
            b = body.position + shape.b.rotated(body.angle)

            item.setLine(a.x, 600 - a.y, b.x, 600 - b.y)

        elif isinstance(item, QGraphicsEllipseItem):
            x, y = body.position.x, 600 - body.position.y
            target_pos = QPointF(x, y)
            if force or not hasattr(item, 'last_pos'):
                item.setPos(target_pos)
                item.last_pos = target_pos
            else:
                current_pos = item.last_pos
                smoothed = current_pos * 0.7 + target_pos * 0.3  # 这个是平缓插值
                item.setPos(smoothed)
                item.last_pos = smoothed
        elif isinstance(item, QGraphicsRectItem):
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
        self.update_spring_line_with_smoothing(spring, line, 1)
        print("Spring created. Click Start to see it in action.")

    def quit_select(self):
        self.selected_item_data = None

    def delete_selected_item(self):
        if not self.selected_item_data:
            return
        item = self.selected_item_data["item"]
        body = self.selected_item_data["body"]
        shape = self.selected_item_data["shape"]
        self.scene.removeItem(item)
        self.simulator.space.remove(body, shape)
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
        except Exception as e:
            print(e)

    def update_scene(self):
        for _ in range(10):  # 多步模拟提升平滑度
            self.simulator.step(1 / 600.0)

        for entry in self.all_item:
            item = entry["item"]
            body = entry["body"]
            shape = entry["shape"]
            self.update_graphics_position(item, body, shape)

            if self.selected_item_data and self.selected_item_data["item"] == item:
                self.plot_data.append(body.position.y)
                if len(self.plot_data) > 100:
                    self.plot_data = self.plot_data[-100:]
                self.plot_curve.setData(self.plot_data)
        self.spring_update_counter += 1
        if self.spring_update_counter % 2 == 0:
            for spring, line in self.springs:
                self.update_spring_line_with_smoothing(spring, line)


        #与开始界面联系
            self.home_action = QAction("返回主页", self)
            self.home_action.triggered.connect(self.return_to_home)
            self.toolbar.addAction(self.home_action)

        def return_to_home(self):
            self.home_page = HomePage()
            self.home_page.show()
            self.close()


def main():
    app = QApplication(sys.argv)
    home_page=HomePage()
    home_page.show()


    sys.exit(app.exec())


if __name__ == "__main__":
    main()
