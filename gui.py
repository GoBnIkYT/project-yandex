from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit, QLineEdit, QPushButton, QLabel, QDateTimeEdit
from PyQt6.QtCore import QDateTime


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Заметки с напоминаниями")
        self.setGeometry(100, 100, 700, 550)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget, 1)

        right_layout = QVBoxLayout()
        layout.addLayout(right_layout, 2)

        title_label = QLabel("Заголовок")
        right_layout.addWidget(title_label)

        self.title_input = QLineEdit()
        right_layout.addWidget(self.title_input)

        text_label = QLabel("Текст заметки")
        right_layout.addWidget(text_label)

        self.text_input = QTextEdit()
        right_layout.addWidget(self.text_input)

        reminder_label = QLabel("Напоминание (дата и время)")
        right_layout.addWidget(reminder_label)

        self.reminder_input = QDateTimeEdit()
        self.reminder_input.setCalendarPopup(True)
        self.reminder_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.reminder_input.setDateTime(QDateTime.currentDateTime())
        right_layout.addWidget(self.reminder_input)

        buttons_layout = QHBoxLayout()
        right_layout.addLayout(buttons_layout)

        self.add_button = QPushButton("Новая")
        buttons_layout.addWidget(self.add_button)

        self.save_button = QPushButton("Сохранить")
        buttons_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("Удалить")
        buttons_layout.addWidget(self.delete_button)
