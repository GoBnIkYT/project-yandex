import sys
import os
import winsound
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, QDateTime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gui

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes.db")


def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, text TEXT, reminder TEXT, notified INTEGER DEFAULT 0)")
    conn.commit()

    cursor.execute("PRAGMA table_info(notes)")
    cols = [c[1] for c in cursor.fetchall()]
    if "reminder" not in cols:
        cursor.execute("ALTER TABLE notes ADD COLUMN reminder TEXT")
    if "notified" not in cols:
        cursor.execute("ALTER TABLE notes ADD COLUMN notified INTEGER DEFAULT 0")
    conn.commit()
    conn.close()


def get_notes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM notes ORDER BY id DESC")
    result = cursor.fetchall()
    conn.close()
    return result


def add_note(title, text, reminder):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (title, text, reminder) VALUES (?, ?, ?)", (title, text, reminder))
    conn.commit()
    conn.close()


def update_note(note_id, title, text, reminder):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE notes SET title = ?, text = ?, reminder = ?, notified = 0 WHERE id = ?", (title, text, reminder, note_id))
    conn.commit()
    conn.close()


def get_note_by_title(title):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, text, reminder FROM notes WHERE title = ?", (title,))
    result = cursor.fetchone()
    conn.close()
    return result


def delete_note(note_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()


def get_due_reminders(now):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, text FROM notes WHERE notified = 0 AND reminder <= ?", (now,))
    result = cursor.fetchall()
    conn.close()
    return result


def mark_notified(note_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE notes SET notified = 1 WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()


class NotesWindow(gui.MainWindow):
    def __init__(self):
        super().__init__()

        create_table()
        self.current_id = None

        self.list_widget.itemClicked.connect(self.load_note)
        self.add_button.clicked.connect(self.new_note)
        self.save_button.clicked.connect(self.save_note)
        self.delete_button.clicked.connect(self.delete_note)

        self.refresh_list()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_reminders)
        self.timer.start(1000)

    def refresh_list(self):
        self.list_widget.clear()
        rows = get_notes()
        for row in rows:
            self.list_widget.addItem(row[1])

    def new_note(self):
        self.current_id = None
        self.title_input.clear()
        self.text_input.clear()
        self.reminder_input.setDateTime(QDateTime.currentDateTime())

    def save_note(self):
        title = self.title_input.text().strip()
        text = self.text_input.toPlainText()
        reminder = self.reminder_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        if not title:
            QMessageBox.warning(self, "Ошибка", "Напиши заголовок")
            return

        if self.current_id is None:
            add_note(title, text, reminder)
        else:
            update_note(self.current_id, title, text, reminder)

        self.refresh_list()
        QMessageBox.information(self, "Готово", "Заметка сохранена")

    def load_note(self, item):
        title = item.text()
        row = get_note_by_title(title)
        if row:
            self.current_id = row[0]
            self.title_input.setText(row[1])
            self.text_input.setText(row[2])
            if row[3]:
                self.reminder_input.setDateTime(QDateTime.fromString(row[3], "yyyy-MM-dd HH:mm:ss"))
            else:
                self.reminder_input.setDateTime(QDateTime.currentDateTime())

    def delete_note(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Ошибка", "Выбери заметку для удаления")
            return

        answer = QMessageBox.question(self, "Удаление", "Точно удалить эту заметку?")
        if answer == QMessageBox.StandardButton.Yes:
            delete_note(self.current_id)
            self.new_note()
            self.refresh_list()

    def check_reminders(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows = get_due_reminders(now)
        for row in rows:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            QMessageBox.information(self, "Напоминание!", row[1] + "\n\n" + row[2])
            mark_notified(row[0])


app = QApplication(sys.argv)
window = NotesWindow()
window.show()
sys.exit(app.exec())
