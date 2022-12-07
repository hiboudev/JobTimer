from enum import Enum
from typing import Optional, List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, \
    QSizePolicy, QSystemTrayIcon

from data.job import Job


class RunningState(Enum):
    RUNNING = 1
    # When running but inactivity detected
    IDLE = 2
    STOPPED = 3


# TODO dans les app QT ils héritent de Window, ça se trouve ça a une influence sur la gestion des threads ?
# Investiguer pour voir si ça change quelque chose.
# Dans le doute faire comme dans les exemples de la doc PyQT
class MainWindow:
    __COLOR_STOPPED = "#808080"
    __COLOR_IDLE = "#2374c0"
    __COLOR_RUNNING = "#dd0044"

    def __init__(self, icon_start_path: str, icon_stop_path: str, icon_idle_path: str):
        self.app = QApplication([])
        self.app.setApplicationDisplayName("Job Timer")

        self.icon_start = QIcon(icon_start_path)
        self.icon_stop = QIcon(icon_stop_path)
        self.icon_idle = QIcon(icon_idle_path)

        self.window = QWidget()
        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        self.project_list = QComboBox()

        self.create_project_button = QPushButton("Nouveau")
        self.edit_project_button = QPushButton("Éditer")
        self.delete_project_button = QPushButton("Supprimer")
        self.clock_button = QPushButton("Démarrer/arrêter")

        self.hourly_rate_label = QLabel()

        self.price_label = QLabel()
        self.price_label.setAlignment(Qt.AlignCenter)
        self.price_label.setStyleSheet('font-size: 22px; color:{}; font-weight: bold'.format(self.__COLOR_STOPPED))

        self.clock = QLabel()
        self.clock.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.clock.setAlignment(Qt.AlignCenter)
        self.clock_base_style_sheet = "font-size: 34px; font-weight: bold;"
        self.clock.setStyleSheet(self.clock_base_style_sheet + "color: {};".format(self.__COLOR_STOPPED))

        h_layout.addWidget(self.create_project_button)
        h_layout.addWidget(self.edit_project_button)
        h_layout.addWidget(self.delete_project_button)

        v_layout.addWidget(self.project_list)
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.hourly_rate_label)
        v_layout.addWidget(self.clock)
        v_layout.addWidget(self.price_label)
        v_layout.addWidget(self.clock_button)

        self.window.setLayout(v_layout)
        self.window.resize(350, 130)

        self.app.setWindowIcon(self.icon_stop)

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon_stop)
        self.tray.setVisible(True)
        self.tray.activated.connect(self.tray_icon_clicked)

    def start_application(self):
        self.window.show()
        self.app.exec_()

    def set_running_state(self, state: RunningState):
        if state == RunningState.RUNNING:
            self.clock.setStyleSheet(self.clock_base_style_sheet + "color: {};".format(self.__COLOR_RUNNING))
            self.app.setWindowIcon(self.icon_start)
            self.tray.setIcon(self.icon_start)
        elif state == RunningState.STOPPED:
            self.clock.setStyleSheet(self.clock_base_style_sheet + "color: {};".format(self.__COLOR_STOPPED))
            self.app.setWindowIcon(self.icon_stop)
            self.tray.setIcon(self.icon_stop)
        elif state == RunningState.IDLE:
            self.clock.setStyleSheet(self.clock_base_style_sheet + "color: {};".format(self.__COLOR_IDLE))
            self.app.setWindowIcon(self.icon_idle)
            self.tray.setIcon(self.icon_idle)

    def set_hourly_rate(self, hourly_rate: int):
        """Give value -1 to clear display."""
        if hourly_rate == -1:
            self.hourly_rate_label.setText("")
        else:
            self.hourly_rate_label.setText("{} € / h".format(hourly_rate))

    def set_clock_text(self, value: str):
        self.clock.setText(value)

    def set_price(self, price: float):
        """Give value -1 to clear display."""
        if price == -1:
            self.price_label.setText("")
        else:
            self.price_label.setText("{:.2f} €".format(price))

    def add_project_to_list(self, job: Job):
        self.project_list.addItem(job.name, job)
        self.project_list.setCurrentIndex(self.project_list.findData(job))

    def remove_project_from_list(self, job: Job) -> Optional[Job]:
        self.project_list.removeItem(self.__get_job_index(job))
        return self.project_list.currentData()

    def update_project_name(self, job: Job):
        self.project_list.setItemText(self.__get_job_index(job), job.name)

    def __get_job_index(self, job: Job) -> int:
        item_index = self.project_list.findData(job)

        if item_index == -1:
            raise Exception("Item not found!")

        return item_index

    def tray_icon_clicked(self):
        self.window.activateWindow()
        self.window.showNormal()

    def get_window(self):
        return self.window

    def set_jobs(self, jobs: List[Job]) -> Job:
        for job in jobs:
            self.project_list.addItem(job.name, job)

        return self.project_list.currentData()
