import base64
import subprocess
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QMenu, QAction, QPlainTextEdit,QGraphicsDropShadowEffect,QVBoxLayout,QSystemTrayIcon, QLabel
from PyQt5.QtGui import QColor, QIcon,QPixmap
from PyQt5.QtCore import Qt
from logo import img

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set window size.
        self.setFixedSize(322, 172)

        # Remove window title bar.
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        # Set window's title.
        self.setAttribute(Qt.WA_TranslucentBackground)  # Set main window to transparent
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setWindowTitle("TinyCopyBoard")

        self.widget = QWidget(self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.widget)

        # Added a text box instead of a button
        self.text_edit = QPlainTextEdit(self.widget)
        self.text_edit.setFixedSize(300, 150)
        self.text_edit.setStyleSheet(
            """
            QPlainTextEdit {
                color: #f5f5f5; 
                font-size: 14px;
                font-family:'Microsoft YaHei';
                background-color:rgba(18, 20, 20, 0.9);
                padding: 17px 10px 10px 10px;
                border: 1px solid #1e2228;
                border-radius: 5px;
            }
            QMenu {
                color: #f5f5f5;
                font-size: 13px;
                font-family:'Microsoft YaHei';
                background-color:#121414;
                padding: 5px 5px 5px 5px;
                border: 1px solid #1e2228;
                line-height: 150%;
            }
            QMenu::item {  
                padding: 5px 10px 5px 10px;
            }
            QMenu::item:selected {
                background-color: #191c21;
            }QScrollBar:vertical {
                background-color: #1e2228;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #707070;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            """
            )
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlaceholderText("剪贴板中的文本将显示在这里")
        self.text_edit.viewport().setCursor(Qt.IBeamCursor)
        self.text_edit.setFocusPolicy(Qt.NoFocus)

        self.label = QLabel(self.widget)
        self.label.setMaximumHeight(150)
        self.layout.addWidget(self.label)
        self.label.hide()  # 初始时隐藏 QLabel
        self.label.setStyleSheet(
            """
            QLabel {
                color: #f5f5f5; 
                background-color:rgba(18, 20, 20, 0.9);
                padding: 17px 10px 10px 10px;
                border: 1px solid #1e2228;
                border-radius: 5px;
            }
""")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(3, 3)
        self.widget.setGraphicsEffect(shadow)
        self.label.setGraphicsEffect(shadow)

        # Initialize variables for dragging the window
        self.drag_start_position = None

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(QIcon("tmp.ico"), self)
        self.tray_icon.setToolTip("TinyCopyBoard")
        self.tray_icon.activated.connect(self.handle_tray_icon_activated)
        self.tray_icon.show()

        # Create tray menu
        self.tray_menu = QMenu()
        self.tray_menu.setStyleSheet("""
        QMenu {
            color: #f5f5f5;
            font-size: 13px;
            font-family:'Microsoft YaHei';
            background-color:#121414;
            padding: 5px 5px 5px 5px;
            border: 1px solid #1e2228;
        line-height: 150%;
        }
        QMenu::item {  
            padding: 5px 10px 5px 10px;
        }
        QMenu::item:selected {
            background-color: #191c21;
        }
        """)
        self.restore_action = QAction("还原", self)
        self.restore_action.triggered.connect(self.restore_window)
        self.tray_menu.addAction(self.restore_action)
        self.minimize_action = QAction("最小化", self)
        self.minimize_action.triggered.connect(self.minimize_to_tray)
        self.tray_menu.addAction(self.minimize_action)
        self.exit_action = QAction("退出", self)
        self.exit_action.triggered.connect(self.handle_exit_action_triggered)
        self.tray_menu.addAction(self.exit_action)
        self.tray_icon.setContextMenu(self.tray_menu)

        # Connect clipboard dataChanged signal to slot
        clipboard = QApplication.clipboard()
        clipboard.dataChanged.connect(self.check_clipboard)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_start_position is not None and event.buttons() & QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_start_position = None
            event.accept()

    def mouseDoubleClickEvent(self, event):
        self.minimize_to_tray()

    def minimize_to_tray(self):
        if self.isMinimized():
            self.showNormal()
            self.activateWindow()
        else:
            self.hide()

    def restore_window(self):
        self.showNormal()
        self.activateWindow()

    def handle_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.restore_window()

    def handle_exit_action_triggered(self):
        self.tray_icon.hide()
        QApplication.quit()

    def check_clipboard(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if mime_data.hasText():  # 剪贴板内容是文本
            text = mime_data.text()
            self.text_edit.setPlainText(text)
            self.text_edit.show()
            self.label.hide()
        elif mime_data.hasImage():  # 剪贴板内容是图片
            image = clipboard.image()
            scaled_image = image.scaledToHeight(150, Qt.TransformationMode.SmoothTransformation)
            self.label.setPixmap(QPixmap.fromImage(scaled_image))
            self.label.show()
            self.text_edit.hide()
        else:  # 剪贴板内容既不是文本也不是图片
            text = mime_data.text()
            self.text_edit.setPlainText(text)
            self.text_edit.show()
            self.label.hide()

if __name__ == "__main__":
    tmp = open("tmp.ico","wb+")
    tmp.write(base64.b64decode(img))
    tmp.close()
    app = QApplication(sys.argv)
    
    app.setWindowIcon(QIcon("tmp.ico"))

    main_window = MainWindow()
    main_window.show()
    subprocess.run(["cmd", "/c", "del", "tmp.ico"], shell=True, check=True)
    sys.exit(app.exec_())