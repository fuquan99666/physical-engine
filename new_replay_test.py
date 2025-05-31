import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class MediaPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Media Player")
        self.setGeometry(100, 100, 800, 600)

        # 播放状态
        self.is_playing = False
        self.current_speed = 1.0
        self.duration = 1000  # 模拟总时长（秒）
        self.position = 0

        # 创建UI
        self.init_ui()
        self.init_timer()

    def init_ui(self):
        # 创建工具栏
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # 播放/暂停按钮
        self.play_action = QAction(QIcon("play.png"), "Play", self)
        self.play_action.triggered.connect(self.toggle_play)
        toolbar.addAction(self.play_action)

        # 进度条
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, self.duration)
        self.progress_slider.sliderMoved.connect(self.set_position)
        toolbar.addWidget(self.progress_slider)

        # 时间显示
        self.time_label = QLabel("00:00 / 20:00")
        toolbar.addWidget(self.time_label)

        # 倍速菜单
        speed_menu = QComboBox()
        speed_menu.addItems(["0.5x", "1.0x", "1.5x", "2.0x"])
        speed_menu.setCurrentIndex(1)
        speed_menu.currentIndexChanged.connect(self.change_speed)
        toolbar.addWidget(QLabel("Speed:"))
        toolbar.addWidget(speed_menu)

        # 状态栏
        self.statusBar().showMessage("Ready")

    def init_timer(self):
        # 更新进度定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)

    def toggle_play(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_action.setIcon(QIcon("pause.png"))
            self.play_action.setText("Pause")
            self.timer.start(int(1000 / self.current_speed))
        else:
            self.play_action.setIcon(QIcon("play.png"))
            self.play_action.setText("Play")
            self.timer.stop()
            
        self.update_time_display()

    def update_progress(self):
        if self.position < self.duration:
            self.position += 1
            self.progress_slider.setValue(self.position)
            self.update_time_display()
        else:
            self.toggle_play()

    def set_position(self, position):
        self.position = position
        self.progress_slider.setValue(position)
        self.update_time_display()

    def change_speed(self, index):
        speeds = [0.5, 1.0, 1.5, 2.0]
        self.current_speed = speeds[index]
        if self.is_playing:
            self.timer.setInterval(1000 / self.current_speed)

    def update_time_display(self):
        current_time = self.format_time(self.position)
        total_time = self.format_time(self.duration)
        self.time_label.setText(f"{current_time} / {total_time}")

    def format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MediaPlayer()
    player.show()
    sys.exit(app.exec())