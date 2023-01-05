import os
import time
from typing import Optional

from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QMessageBox

from data.database import Database
from data.job import Job
from inactivity.inactivity_controller import InactivityController
from timer.timer import JobTimer
from ui.dialogs import CreateProjectDialog, EditProjectDialog
from ui.main_window import MainWindow, RunningState


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # noinspection PyBroadException
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # noinspection PyProtectedMember,PyUnresolvedReferences
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


main_window = MainWindow(resource_path("icon/icon_running.png"), resource_path("icon/icon_stopped.png"),
                         resource_path("icon/icon_idle.png"))

sound_inactivity = QSound(resource_path("sound/inactivity.wav"))
sound_activity_returns = QSound(resource_path("sound/activity_returns.wav"))

database = Database()
active_job: Optional[Job] = None

is_running = False

# We auto save time to DB in case of computer crash
last_auto_save_time = time.time()
AUTO_SAVE_DELAY = 60  # seconds


def start_timer():
    global last_auto_save_time
    last_auto_save_time = time.time()

    timer.start()
    inactivity_controller.start()
    main_window.set_running_state(RunningState.RUNNING)
    global is_running
    is_running = True


def stop_timer():
    timer.stop()
    inactivity_controller.stop()
    main_window.set_running_state(RunningState.STOPPED)

    save_job_elapsed_time(timer.get_elapsed_seconds())
    global is_running
    is_running = False


def inactivity_callback():
    save_job_elapsed_time(timer.get_elapsed_seconds())
    sound_inactivity.play()
    timer.stop()
    main_window.set_running_state(RunningState.IDLE)


def activity_returns_callback():
    global last_auto_save_time
    last_auto_save_time = time.time()

    sound_activity_returns.play()
    timer.start()
    main_window.set_running_state(RunningState.RUNNING)


def set_active_job(new_job: Job):
    stop_timer()
    global active_job
    active_job = new_job

    timer.reset(active_job.elapsed_seconds)
    main_window.set_hourly_rate(active_job.hourly_rate)


def save_job_elapsed_time(elapsed_seconds: float):
    if active_job:
        active_job.elapsed_seconds = elapsed_seconds
        database.update_job_elapsed_time(active_job)


def on_create_project_button_clicked():
    if is_running:
        stop_timer()

    dialog = CreateProjectDialog()
    ok = dialog.exec()
    if ok:
        new_job = database.add_job(dialog.get_project_name(), dialog.get_hourly_rate())
        main_window.add_project_to_list(new_job)
        set_active_job(new_job)


def on_edit_project_button_clicked():
    if not active_job:
        return

    stop_timer()
    dialog = EditProjectDialog()
    dialog.set_values(active_job.name, active_job.hourly_rate)
    dialog.set_seconds(active_job.elapsed_seconds)

    if dialog.exec():
        database.edit_job(active_job.id, dialog.get_project_name(), dialog.get_hourly_rate())

        active_job.name = dialog.get_project_name()
        active_job.hourly_rate = dialog.get_hourly_rate()

        timer.set_elapsed_seconds(dialog.get_seconds())
        main_window.set_hourly_rate(active_job.hourly_rate)
        main_window.update_project_name(active_job)

        save_job_elapsed_time(dialog.get_seconds())


def on_delete_projet_button_clicked():
    global active_job
    if active_job is None:
        return

    stop_timer()
    choice = QMessageBox.question(main_window.get_window(), "Supprimer le projet",
                                  f"Supprimer le projet '{active_job.name}' ?",
                                  QMessageBox.Yes | QMessageBox.No)
    if choice == QMessageBox.Yes:
        database.delete_job(active_job)
        new_job = main_window.remove_project_from_list(active_job)

        if new_job:
            set_active_job(new_job)
        else:
            active_job = None
            main_window.set_clock_text("")
            main_window.set_price(-1)
            main_window.set_hourly_rate(-1)


def on_job_selected():
    job: Job = main_window.project_list.currentData()
    set_active_job(job)


def on_start_stop_clicked():
    if not active_job:
        return

    if not is_running:
        start_timer()
    else:
        stop_timer()


def timer_update_callback(seconds: float, formatted_time: str):
    global last_auto_save_time

    if time.time() - last_auto_save_time >= AUTO_SAVE_DELAY:
        save_job_elapsed_time(seconds)
        last_auto_save_time = time.time()

    main_window.set_clock_text(formatted_time)
    update_price(seconds)


def update_price(seconds: float):
    if active_job:
        price = (seconds / 3600) * active_job.hourly_rate
        main_window.set_price(price)


def on_app_closing():
    stop_timer()


main_window.app.aboutToQuit.connect(on_app_closing)
main_window.project_list.activated.connect(on_job_selected)
main_window.create_project_button.clicked.connect(on_create_project_button_clicked)
main_window.edit_project_button.clicked.connect(on_edit_project_button_clicked)
main_window.delete_project_button.clicked.connect(on_delete_projet_button_clicked)
main_window.clock_button.clicked.connect(on_start_stop_clicked)

timer = JobTimer(timer_update_callback)

inactivity_controller = InactivityController(main_window.window, inactivity_callback, activity_returns_callback)

selected_job = main_window.set_jobs(database.get_jobs())

if selected_job:
    set_active_job(selected_job)

main_window.start_application()
