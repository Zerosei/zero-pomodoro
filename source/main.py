import sys

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QDialog, QPushButton, QLabel, QApplication, QMenu, \
    QSystemTrayIcon, QAction
from PyQt5.QtCore import *
from ui import Ui_MainWindow
import os
import sys


def closeEvent(self, event):
    """Interceptar el evento de cierre para minimizar a la bandeja"""
    event.ignore()
    self.hide()
    self.tray_icon.showMessage("Temporizador pomodoro en segundo plano", QSystemTrayIcon.Information, 3000)


def get_hh_mm_ss(minutes_interval):
    minutes_interval = int(minutes_interval)
    seconds = 0
    hours = 0
    if minutes_interval >= 60:
        hours = minutes_interval // 60
        minutes_interval %= 60

    return hours, minutes_interval, seconds


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Inicializamos la interfaz (esto es lo generado por pyuic5)
        self.disable = False
        self.disable_2 = False
        self.disable_3 = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Configura la interfaz en la ventana principal

        self.ui.main_timer_label.hide()
        self.ui.pushButton.clicked.connect(self.start_pomodoro)
        self.ui.main_timer.textChanged.connect(lambda: self.input_validator(1))
        self.ui.main_timer_2.textChanged.connect(lambda: self.input_validator(2))
        self.ui.main_timer_3.textChanged.connect(lambda: self.input_validator(3))
        self.ui.error_label.hide()
        self.ui.pushButton.setDisabled(True)
        self.ui.pushButton_2.setDisabled(True)
        self.ui.pushButton_3.setDisabled(True)
        self.timer = None
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.timer_tracker = 0
        self.focus = 0
        self.rest = 0
        self.long_rest = 0
        self.step = 0
        self.stage = "Pomodoro"
        self.tray_icon = QSystemTrayIcon(QIcon(self.resource_path("tomate.png")), self)
        self.setWindowIcon(QIcon(self.resource_path("tomate.png")))
        if not self.tray_icon.isSystemTrayAvailable():
            self.tray_icon.setIcon(self.style().standardIcon(QSystemTrayIcon.SP_Computer))
        self.tray_icon.setToolTip("Pomodoro!")

        menu = QMenu()
        restore_action = QAction("Restaurar", self)
        restore_action.triggered.connect(self.open_window)
        menu.addAction(restore_action)

        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.exit)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.abrir_desde_bandeja)
        self.tray_icon.show()

    def get_timers(self):
        focus_minutes = int(self.ui.main_timer.toPlainText())
        if self.ui.main_timer_2.toPlainText() != '':
            rest_minutes = int(self.ui.main_timer_2.toPlainText())
        else:
            rest_minutes = 0
        if self.ui.main_timer_3.toPlainText() != '':
            long_rest_minutes = int(self.ui.main_timer_3.toPlainText())
        else:
            long_rest_minutes = 0
        return focus_minutes, rest_minutes, long_rest_minutes


    def start_pomodoro(self):
        self.step += 1
        self.ui.pushButton.setText("Pausar")
        self.ui.pushButton.clicked.disconnect()
        self.ui.pushButton.clicked.connect(self.stop_timer)
        self.ui.pushButton_3.setEnabled(True)
        self.ui.pushButton_3.clicked.connect(self.short_rest)
        self.ui.inputs.hide()
        self.ui.main_timer_label.show()
        self.focus, self.rest, self.long_rest = self.get_timers()
        self.hours, self.minutes, self.seconds = get_hh_mm_ss(self.focus)
        self.ui.pushButton_2.setEnabled(True)
        self.ui.pushButton_2.clicked.connect(self.end_pomodoro)

        self.ui.main_timer_label.setText(f"{self.hours}:{self.minutes:02d}:{self.seconds:02d}")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)


    def update_timer(self):
        self.timer_tracker += 1
        if self.seconds > 0:
            self.seconds -= 1
        elif self.seconds == 0 and self.minutes != 0:
            self.minutes -=1
            self.seconds = 59
        elif self.minutes == 0 and self.seconds == 0 and self.hours != 0:
            self.hours -= 1
            self.minutes = 59
        elif self.seconds == 0 and self.minutes == 0 and self.hours == 0:
            self.open_window()
            if self.step == 4:
                self.start_long_rest()
            elif self.stage == "Pomodoro":
                self.short_rest()
            else:
                self.pomodoro()

        self.ui.main_timer_label.setText(f"{self.hours}:{self.minutes:02d}:{self.seconds:02d}")


    def stop_timer(self):
        self.timer.stop()
        self.ui.pushButton.clicked.disconnect()
        self.ui.pushButton.setText("Reanudar")
        self.ui.pushButton.clicked.connect(self.resume_timer)


    def resume_timer(self):
        self.timer.start(1000)
        self.ui.pushButton.setText("Pausar")
        self.ui.pushButton.clicked.disconnect()
        self.ui.pushButton.clicked.connect(self.stop_timer)


    def input_validator(self, timer:int):
        try:
            if timer == 1:
                if len(self.ui.main_timer.toPlainText()) < 8 and self.ui.main_timer.toPlainText().find("-") == -1 \
                        and self.disable_2 == False and self.disable_3 == False:
                    int(self.ui.main_timer.toPlainText())
                    self.ui.error_label.hide()
                    self.ui.pushButton.setEnabled(True)
                    self.disable = False
                else:
                    self.ui.error_label.show()
                    self.ui.pushButton.setEnabled(True)
                    self.ui.pushButton.setDisabled(True)
                    if self.disable_3 == False and self.disable_2 == False:
                        self.disable = True
            elif timer == 2:
                if len(self.ui.main_timer_2.toPlainText()) < 8 and self.ui.main_timer_2.toPlainText().find("-") == -1 \
                        and self.disable == False and self.disable_3 == False:
                    int(self.ui.main_timer_2.toPlainText())
                    self.ui.error_label.hide()
                    self.ui.pushButton.setEnabled(True)
                    self.disable_2 = False
                else:
                    self.ui.error_label.show()
                    self.ui.pushButton.setEnabled(True)
                    self.ui.pushButton.setDisabled(True)
                    if self.disable == False and self.disable_3 == False:
                        self.disable_2 = True
            else:
                if len(self.ui.main_timer_3.toPlainText()) < 8 and self.ui.main_timer_3.toPlainText().find("-") == -1\
                        and self.disable == False and self.disable_2 == False:
                    int(self.ui.main_timer_3.toPlainText())
                    self.ui.error_label.hide()
                    self.ui.pushButton.setEnabled(True)
                    self.disable_3 = False
                else:
                    self.ui.error_label.show()
                    self.ui.pushButton.setEnabled(True)
                    self.ui.pushButton.setDisabled(True)
                    if self.disable == False and self.disable_2 == False:
                        self.disable_3 = True
        except ValueError:
            self.ui.pushButton.setEnabled(True)
            self.ui.pushButton.setDisabled(True)
            self.ui.error_label.show()


    def pomodoro(self):
        if self.stage != "Pomodoro":
            self.stage = "Pomodoro"
        self.ui.pushButton_3.clicked.disconnect()
        self.step += 1
        self.ui.label.setText("Pomodoro!")
        self.ui.pushButton.setText("Pausar")
        self.ui.pushButton.clicked.disconnect()
        self.ui.pushButton.clicked.connect(self.stop_timer)
        self.hours, self.minutes, self.seconds = get_hh_mm_ss(self.focus)
        self.ui.main_timer_label.setText(f"{self.hours}:{self.minutes:02d}:{self.seconds:02d}")
        if self.step == 4:
            self.ui.pushButton_3.clicked.connect(self.start_long_rest)
        else:
            self.ui.pushButton_3.clicked.connect(self.short_rest)


    def short_rest(self):
        self.stage = "Descanso corto"
        self.ui.label.setText("Descanso!")
        self.hours, self.minutes, self.seconds = get_hh_mm_ss(self.rest)
        self.ui.main_timer_label.setText(f"{self.hours}:{self.minutes:02d}:{self.seconds:02d}")
        self.ui.pushButton_3.clicked.disconnect()
        self.ui.pushButton_3.clicked.connect(self.pomodoro)


    def start_long_rest(self):
        self.stage = "Descanso reparador"
        self.step = 0
        self.ui.label.setText("Descanso reparador")
        self.hours, self.minutes, self.seconds = get_hh_mm_ss(self.long_rest)
        self.ui.main_timer_label.setText(f"{self.hours}:{self.minutes:02d}:{self.seconds:02d}")
        self.ui.pushButton_3.clicked.disconnect()
        self.ui.pushButton_3.clicked.connect(self.pomodoro)


    def end_pomodoro(self):
        self.ui.pushButton.clicked.disconnect()
        self.timer.stop()
        self.ui.inputs.show()
        self.ui.pushButton.setText("Iniciar")
        self.ui.main_timer_label.hide()
        self.ui.main_timer.clear()
        self.ui.main_timer_2.clear()
        self.ui.main_timer_3.clear()
        self.ui.pushButton.clicked.connect(self.start_pomodoro)
        self.ui.error_label.hide()
        self.ui.pushButton.setDisabled(True)
        self.ui.pushButton_2.setDisabled(True)
        self.ui.pushButton_3.setDisabled(True)
        self.timer = None
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.timer_tracker = 0
        self.focus = 0
        self.rest = 0
        self.long_rest = 0
        self.step = 0
        self.ui.pushButton_2.clicked.disconnect()


    def open_window(self):
        """Restaurar y traer la ventana al frente"""
        self.showNormal()
        self.activateWindow()  # Asegura que la ventana está activa
        self.raise_()  # La pone sobre otras ventanas


    def exit(self):
        """Salir completamente"""
        self.tray_icon.hide()
        QApplication.quit()


    def abrir_desde_bandeja(self, reason):
        """Restaurar la ventana al hacer clic en el icono de la bandeja"""
        if reason == QSystemTrayIcon.Trigger:  # Click izquierdo
            self.open_window()

    def resource_path(self, relative_path):
        """ Obtiene la ruta del recurso, compatible con PyInstaller """
        if getattr(sys, 'frozen', False):  # Si está empaquetado con PyInstaller
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.abspath(relative_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

