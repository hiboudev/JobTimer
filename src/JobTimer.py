import os
import sys
from typing import Union

from data.job import Job
from data.database import Database
from timer.timer import JobTimer
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QInputDialog, \
    QLabel, QSizePolicy, QMessageBox, QSystemTrayIcon

# Note : time is not saved if application crashes or is closed by end of Windows session

app = QApplication([])
app.setApplicationDisplayName("Job Timer")
window = QWidget()
vLayout = QVBoxLayout()
hLayout = QHBoxLayout()
projectList = QComboBox()
createProjectButton = QPushButton("Nouveau")
deleteProjectButton = QPushButton("Supprimer")
clock = QLabel()
clock.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
clock.setAlignment(Qt.AlignCenter)
clock.setStyleSheet('font-size: 18px; color:grey; font-weight: bold')
clock_button = QPushButton("Démarrer/arrêter")
hLayout.addWidget(projectList)
hLayout.addWidget(createProjectButton)
hLayout.addWidget(deleteProjectButton)
vLayout.addLayout(hLayout)
vLayout.addWidget(clock)
vLayout.addWidget(clock_button)
window.setLayout(vLayout)
window.resize(350, 130)


# TODO cleaner le code icon et css dans un autre fichier
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # noinspection PyBroadException
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
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
    clock.setStyleSheet('font-size: 18px; color: green; font-weight: bold')
    app.setWindowIcon(icon_start)
    tray.setIcon(icon_start)


def stop_timer():
    timer.stop()
    clock.setStyleSheet('font-size: 18px; color:grey; font-weight: bold')
    app.setWindowIcon(icon_stop)
    tray.setIcon(icon_stop)

    if active_job is not None:
        save_job_elapsed_time(active_job)


def set_active_job(job: Job):
    stop_timer()
    global active_job
    active_job = job
    timer.set_job(active_job)


def save_job_elapsed_time(job: Job):
    database.update_job_elapsed_time(job)


def on_create_projet_button_clicked():
    stop_timer()
    text, ok = QInputDialog.getText(createProjectButton, "Nouveau projet", "Nom du projet :")
    if ok:
        new_job = database.add_job(text)
        projectList.addItem(new_job.name, new_job)
        projectList.setCurrentIndex(projectList.findData(new_job))
        set_active_job(new_job)


def on_delete_projet_button_clicked():
    global active_job
    if active_job is None:  # Just to avoid python warning
        return

    stop_timer()
    choice = QMessageBox.question(deleteProjectButton, "Supprimer le projet",
                                  f"Supprimer le projet '{active_job.name}' ?",
                                  QMessageBox.Yes | QMessageBox.No)
    if choice == QMessageBox.Yes:
        database.delete_job(active_job)
        projectList.removeItem(projectList.currentIndex())
        if projectList.currentData() is not None:
            set_active_job(projectList.currentData())
        else:
            active_job = None
            clock.setText("")


def on_job_selected():
    selected_job: Job = projectList.currentData()
    set_active_job(selected_job)


def on_start_stop_clicked():
    if not timer.is_running:
        start_timer()
    else:
        stop_timer()


def timer_update_callback(time: str):
    clock.setText(time)


def on_app_closing():
    stop_timer()


# noinspection PyUnresolvedReferences
app.aboutToQuit.connect(on_app_closing)
# noinspection PyUnresolvedReferences
projectList.activated.connect(on_job_selected)
# noinspection PyUnresolvedReferences
createProjectButton.clicked.connect(on_create_projet_button_clicked)
# noinspection PyUnresolvedReferences
deleteProjectButton.clicked.connect(on_delete_projet_button_clicked)
# noinspection PyUnresolvedReferences
clock_button.clicked.connect(on_start_stop_clicked)

timer = JobTimer(timer_update_callback)

jobs = database.get_jobs()
for job in jobs:
    projectList.addItem(job.name, job)

if len(jobs) > 0:
    set_active_job(jobs[0])

window.show()
app.exec_()
