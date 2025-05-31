from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox
)

class AddObjectDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Object")
        self.resize(300, 200)

        self.layout = QVBoxLayout()

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Circle", "Box", "Segment"])
        self.layout.addWidget(QLabel("Object Type:"))
        self.layout.addWidget(self.type_combo)

        self.params = {}
        for label in ["x", "y", "mass", "radius_or_width", "height_or_inner_radius"]:
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(label + ":"))
            line_edit = QLineEdit()
            hbox.addWidget(line_edit)
            self.params[label] = line_edit
            self.layout.addLayout(hbox)

        # 添加 static 复选框
        self.static_checkbox = QCheckBox("Static (Unmovable)")
        self.layout.addWidget(self.static_checkbox)

        self.ok_button = QPushButton("Add")
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)

        self.setLayout(self.layout)

    def get_values(self):
        return {
            "type": self.type_combo.currentText(),
            "x": float(self.params["x"].text()),
            "y": float(self.params["y"].text()),
            "mass": float(self.params["mass"].text()),
            "r_or_w": float(self.params["radius_or_width"].text()),
            "h_or_r2": float(self.params["height_or_inner_radius"].text()),
            "static": self.static_checkbox.isChecked()
        }
