import os
import sys
from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, \
    QSizePolicy, QMessageBox, QSystemTrayIcon

from data.database import Database
from data.job import Job
from timer.timer import JobTimer
from ui.dialogs import CreateProjectDialog

app = QApplication([])
app.setApplicationDisplayName("Job Timer")

window = QWidget()
v_layout = QVBoxLayout()
h_layout = QHBoxLayout()
project_list = QComboBox()

create_project_button = QPushButton("Nouveau")
edit_project_button = QPushButton("Éditer")
delete_project_button = QPushButton("Supprimer")

hourly_rate_label = QLabel()

price_label = QLabel()
price_label.setAlignment(Qt.AlignCenter)
price_label.setStyleSheet('font-size: 22px; color:grey; font-weight: bold')

clock = QLabel()
clock.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
clock.setAlignment(Qt.AlignCenter)
clock_base_style_sheet = "font-size: 34px; font-weight: bold;"
clock.setStyleSheet(clock_base_style_sheet + "color:grey;")

clock_button = QPushButton("Démarrer/arrêter")

h_layout.addWidget(project_list)
h_layout.addWidget(create_project_button)
h_layout.addWidget(edit_project_button)
h_layout.addWidget(delete_project_button)

v_layout.addLayout(h_layout)
v_layout.addWidget(hourly_rate_label)
v_layout.addWidget(clock)
v_layout.addWidget(price_label)
v_layout.addWidget(clock_button)

window.setLayout(v_layout)
window.resize(350, 130)


# TODO cleaner le code icon et css dans un autre fichier
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # noinspection PyBroadException
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # noinspection PyUnresolvedReferences
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


icon_start = QIcon(resource_path("icon/icon_start.png"))
icon_stop = QIcon(resource_path("icon/icon_stop.png"))
app.setWindowIcon(icon_stop)


def tray_icon_clicked():
    window.activateWindow()
    window.showNormal()


tray = QSystemTrayIcon()
tray.setIcon(icon_stop)
tray.setVisible(True)
# noinspection PyUnresolvedReferences
tray.activated.connect(tray_icon_clicked)

database = Database()
active_job: Union[Job, None] = None


def start_timer():
    timer.start()
    clock.setStyleSheet(clock_base_style_sheet + "color:green;")
    app.setWindowIcon(icon_start)
    tray.setIcon(icon_start)


def stop_timer():
    timer.stop()
    clock.setStyleSheet(clock_base_style_sheet + "color:grey;")
    app.setWindowIcon(icon_stop)
    tray.setIcon(icon_stop)

    if active_job is not None:
        save_job_elapsed_time(active_job)


def set_active_job(job: Job):
    stop_timer()
    global active_job
    active_job = job
    timer.set_job(active_job)
    hourly_rate_label.setText("{} € / h".format(job.hourly_rate))
    # price_label


def save_job_elapsed_time(job: Job):
    database.update_job_elapsed_time(job)


def on_create_projet_button_clicked():
    stop_timer()
    dialog = CreateProjectDialog()
    ok = dialog.exec()
    if ok:
        new_job = database.add_job(dialog.get_project_name(), int(dialog.get_hourly_rate()))
        project_list.addItem(new_job.name, new_job)
        project_list.setCurrentIndex(project_list.findData(new_job))
        set_active_job(new_job)


def on_edit_projet_button_clicked():
    global active_job
    if not active_job:
        return

    stop_timer()
    dialog = CreateProjectDialog()
    dialog.set_values(active_job.name, active_job.hourly_rate)

    if dialog.exec():
        database.edit_job(active_job.id, dialog.get_project_name(), int(dialog.get_hourly_rate()))
        active_job.name = dialog.get_project_name()
        active_job.hourly_rate = int(dialog.get_hourly_rate())
        project_list.setItemText(project_list.currentIndex(), active_job.name)
        set_active_job(active_job)


def on_delete_projet_button_clicked():
    global active_job
    if active_job is None:
        return

    stop_timer()
    choice = QMessageBox.question(delete_project_button, "Supprimer le projet",
                                  f"Supprimer le projet '{active_job.name}' ?",
                                  QMessageBox.Yes | QMessageBox.No)
    if choice == QMessageBox.Yes:
        database.delete_job(active_job)
        project_list.removeItem(project_list.currentIndex())
        if project_list.currentData() is not None:
            set_active_job(project_list.currentData())
        else:
            active_job = None
            clock.setText("")


def on_job_selected():
    selected_job: Job = project_list.currentData()
    set_active_job(selected_job)


def on_start_stop_clicked():
    if not timer.is_running:
        start_timer()
    else:
        stop_timer()


def timer_update_callback(seconds: float, time: str):
    clock.setText(time)
    update_price(seconds)


def update_price(seconds: float):
    if active_job:
        price = (seconds / 3600) * active_job.hourly_rate
        price_label.setText("{:.2f} €".format(price))


def on_app_closing():
    stop_timer()


app.aboutToQuit.connect(on_app_closing)
project_list.activated.connect(on_job_selected)
create_project_button.clicked.connect(on_create_projet_button_clicked)
edit_project_button.clicked.connect(on_edit_projet_button_clicked)
delete_project_button.clicked.connect(on_delete_projet_button_clicked)
clock_button.clicked.connect(on_start_stop_clicked)

timer = JobTimer(timer_update_callback)

jobs = database.get_jobs()
for job in jobs:
    project_list.addItem(job.name, job)

if len(jobs) > 0:
    set_active_job(jobs[0])

window.show()
app.exec_()
