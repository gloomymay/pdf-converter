import os
import sys
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                             QLabel, QVBoxLayout, QHBoxLayout, QFileDialog, 
                             QMessageBox, QLineEdit, QProgressBar)
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from .pdf_converter import extract_and_convert, parse_pages_arg

class ConversionThread(QThread):
    conversion_progress = pyqtSignal(int)
    conversion_complete = pyqtSignal(bool, str)

    def __init__(self, pdf_file, output_dir, pages=None):
        super().__init__()
        self.pdf_file = pdf_file
        self.output_dir = output_dir
        self.pages = pages

    def run(self):
        try:
            extract_and_convert(self.pdf_file, self.output_dir, self.pages)
            self.conversion_complete.emit(True, "转换成功")
        except Exception as e:
            self.conversion_complete.emit(False, str(e))

class PDFConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.pdf_file = None
        self.output_dir = None

    def initUI(self):
        self.setWindowTitle('PDF转换工具')
        self.setGeometry(300, 300, 600, 400)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)

        # 主容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 标题
        title_label = QLabel('PDF 转换工具')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 20, QFont.Bold))
        main_layout.addWidget(title_label)

        # PDF文件选择
        pdf_layout = QHBoxLayout()
        self.pdf_label = QLabel('未选择PDF文件')
        pdf_select_btn = QPushButton('选择PDF文件')
        pdf_select_btn.clicked.connect(self.select_pdf_file)
        pdf_layout.addWidget(self.pdf_label)
        pdf_layout.addWidget(pdf_select_btn)
        main_layout.addLayout(pdf_layout)

        # 输出目录选择
        output_layout = QHBoxLayout()
        self.output_label = QLabel('未选择输出目录')
        output_select_btn = QPushButton('选择输出目录')
        output_select_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(output_select_btn)
        main_layout.addLayout(output_layout)

        # 页面选择
        pages_layout = QHBoxLayout()
        pages_label = QLabel('页面（可选，如：1,3-5）')
        self.pages_input = QLineEdit()
        pages_layout.addWidget(pages_label)
        pages_layout.addWidget(self.pages_input)
        main_layout.addLayout(pages_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)

        # 转换按钮
        convert_btn = QPushButton('开始转换')
        convert_btn.clicked.connect(self.convert_pdf)
        main_layout.addWidget(convert_btn)

        # 状态标签
        self.status_label = QLabel('准备就绪')
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

    def select_pdf_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择PDF文件', '', 'PDF文件 (*.pdf)')
        if file_path:
            self.pdf_file = file_path
            self.pdf_label.setText(os.path.basename(file_path))

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, '选择输出目录')
        if dir_path:
            self.output_dir = dir_path
            self.output_label.setText(os.path.basename(dir_path))

    def convert_pdf(self):
        if not self.pdf_file:
            QMessageBox.warning(self, '错误', '请先选择PDF文件')
            return
        
        if not self.output_dir:
            QMessageBox.warning(self, '错误', '请先选择输出目录')
            return

        # 准备转换线程
        pages = self.pages_input.text() if self.pages_input.text() else None
        parsed_pages = parse_pages_arg(pages) if pages else None

        self.conversion_thread = ConversionThread(
            self.pdf_file, 
            self.output_dir, 
            parsed_pages
        )
        
        self.conversion_thread.conversion_complete.connect(self.on_conversion_complete)
        self.conversion_thread.start()

        # 更新UI状态
        self.status_label.setText('正在转换...')
        self.progress_bar.setRange(0, 0)  # 不确定进度模式

    def on_conversion_complete(self, success, message):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)

        if success:
            QMessageBox.information(self, '成功', message)
            self.status_label.setText('转换成功')
        else:
            QMessageBox.critical(self, '错误', message)
            self.status_label.setText('转换失败')

def main():
    app = QApplication(sys.argv)
    ex = PDFConverterApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
