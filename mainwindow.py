import pymunk
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QSlider,
    QVBoxLayout, QHBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsLineItem, QToolBar, QGraphicsRectItem
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QAction, QPen
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
        self.simulator.space.collision_slop = 0.01  # 可选：更贴合

        self.toolbar = QToolBar("Main ToolBar")
        self.addToolBar(self.toolbar)

        self._init_toolbar()
        self._init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scene)
        self.running = False
        self.time = 0

        self.spring_selection=[]
        self.springs=[]

    def _init_toolbar(self):
        actions = [
            ("Start/Pause", self.toggle_simulation),
            ("Reset", self.reset_simulation),
            ("Delete Selected", self.delete_selected_item),
            ("Quit Selected", self.quit_select),
            ("Add Object", self.show_add_object_dialog),
            ("Add Spring",self.prepare_add_spring)
        ]
        for name, slot in actions:
            action = QAction(name, self)
            action.triggered.connect(slot)
            self.toolbar.addAction(action)

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 600, 600)
        self.view = QGraphicsView(self.scene)
        self.view.setMinimumSize(400, 400)
        self.view.setStyleSheet("background: #f0f0f0")

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

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.view)
        main_layout.addLayout(right_layout)

        central_widget.setLayout(main_layout)

    def toggle_simulation(self):
        self.running = not self.running
        self.start_btn.setText("Pause" if self.running else "Start")
        if self.running:
            self.timer.start(16)  # 60 FPS
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

    def show_add_object_dialog(self):
        dialog = AddObjectDialog()
        if not dialog.exec():
            return

        values = dialog.get_values()
        obj_type = values["type"]
        x, y = values["x"], values["y"]
        mass = values["mass"]
        a = values["r_or_w"]
        b = values["h_or_r2"]
        is_static = values.get("static", False)

        if obj_type == "Circle":
            body = self.simulator.add_circle(x, y, mass, a)
            item = QGraphicsEllipseItem(0, 0, 2*a, 2*a)
        elif obj_type == "Box":
            body = self.simulator.add_box(x, y, b, a, mass)
            item = QGraphicsRectItem(0, 0, a, b)
        elif obj_type == "Segment":
            start = pymunk.Vec2d(x, y)
            end = pymunk.Vec2d(x + a, y + b)
            body = self.simulator.add_segment(start, end, mass, radius=5, static=is_static)
            item = QGraphicsLineItem()
        else:
            return

        self._configure_item(item, body, is_static)
        self.all_item.append({"item": item, "body": body})
        self.scene.addItem(item)
        self.update_graphics_position(item, body)

    def _configure_item(self, item, body, is_static):
        if hasattr(item, 'setBrush'):
            item.setBrush(QColor("green"))
        if isinstance(item, QGraphicsLineItem):
            shape = next(iter(body.shapes))
            pen = QPen(QColor("green"))
            pen.setWidthF(shape.radius * 2)  # 匹配物理厚度
            item.setPen(pen)

        item.setFlag(item.GraphicsItemFlag.ItemIsMovable, not is_static)
        item.setFlag(item.GraphicsItemFlag.ItemIsSelectable, True)
        item.setAcceptHoverEvents(True)
        item.mousePressEvent = lambda e, b=item: self.select_item(b)
        if not is_static:
            item.mouseMoveEvent = lambda e, b=item, bd=body: self.drag_item(b, bd, e)

    def drag_item(self, item, body, event):
        pos = event.scenePos()
        body.position = (pos.x(), 600 - pos.y())
        self.update_graphics_position(item, body)

    def update_graphics_position(self, item, body):
        if isinstance(item, QGraphicsLineItem):
            shape = next(iter(body.shapes))
            a = body.position + shape.a.rotated(body.angle)
            b = body.position + shape.b.rotated(body.angle)
            item.setLine(a.x, 600 - a.y, b.x, 600 - b.y)
        else:
            item.setPos(body.position.x, 600 - body.position.y)

    def select_item(self, item):
        for entry in self.all_item:
            if entry["item"] == item:
                self.selected_item_data = entry
                if self.spring_selection is not None:
                    self.spring_selection.append(entry)
                    if len(self.spring_selection)==2:
                      
                        self.add_spring_between_bodies()
                        self.spring_selection=None
                        self.statusBar().clearMessage()
                break


    def add_spring_between_bodies(self):
        e1,e2=self.spring_selection
        b1,b2=e1["body"],e2["body"]
        if b1 is b2:
            print("Cannot connect a spring to the same object!")
        
            return 
        spring=self.simulator.add_spring(
            b1,b2,
            stiffness=200,damping=10,
            anchor1=(0,0),anchor2=(0,0),
            rest_length=(b1.position-b2.position).length
        )
        line=QGraphicsLineItem()
        pen=QPen(QColor("red"))
        pen.setWidth(5)
        line.setPen(pen)
        self.scene.addItem(line)
        self.springs.append((spring,line))
        print("the spring has been created.You just need to click the start button so that you can see it.")

    def quit_select(self):
        self.selected_item_data = None

    def delete_selected_item(self):
        if not self.selected_item_data:
            return
        item = self.selected_item_data["item"]
        body = self.selected_item_data["body"]
        self.scene.removeItem(item)
        self.simulator.space.remove(body, *body.shapes)
        self.all_item.remove(self.selected_item_data)
        self.selected_item_data = None
        self.plot_data.clear()
        self.plot_curve.setData([])

    def prepare_add_spring(self):
        self.spring_selection=[]
        self.statusBar().showMessage("Select two objects to add a spring.")


    def update_scene(self):
        self.simulator.space.step(1 / 60.0)
        for entry in self.all_item:
            item = entry["item"]
            body = entry["body"]
            self.update_graphics_position(item, body)

            if self.selected_item_data and self.selected_item_data["item"] == item:
                self.plot_data.append(body.position.y)
                if len(self.plot_data) > 100:
                    self.plot_data = self.plot_data[-100:]
                self.plot_curve.setData(self.plot_data)

        for spring,line in self.springs:
            a=spring.a.position+spring.anchor_a.rotated(spring.a.angle)
            b=spring.b.position+spring.anchor_b.rotated(spring.b.angle)
            line.setLine(a.x,600-a.y,b.x,600-b.y)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()