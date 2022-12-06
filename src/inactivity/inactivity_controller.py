from typing import Callable

import keyboard
from PyQt5 import QtGui
from PyQt5.QtCore import QTimer, pyqtSignal, QThread, QObject
from keyboard import KeyboardEvent


class InactivityController:
    __DELAY_INACTIVITY = 60000
    __DELAY_MOUSE_DETECTION = 1000

    def __init__(self, window: QObject, inactivity_callback: Callable, activity_returns_callback: Callable):
        super().__init__()

        self.__inactivity_callback = inactivity_callback
        self.__activity_returns_callback = activity_returns_callback

        self.__is_activity_running = True
        # I don't know how to release keyboard.on_press, so it's running forever,
        # and I use this boolean to check if keyboard input must be processed.
        self.__is_started = False

        self.__keyboard_listener = KeyboardListener(window)
        # noinspection PyUnresolvedReferences
        self.__keyboard_listener.signal.on_key_pressed.connect(self.__on_key_pressed)

        self.__mouse_timer = self.__create_mouse_timer()
        self.__inactivity_timer = self.__create_inactivity_timer()

        self.__mouse_position = None

    def start(self):
        self.__is_started = True
        self.__is_activity_running = True
        self.__restart_timer()

    def stop(self):
        self.__is_started = False
        self.__inactivity_timer.stop()
        self.__mouse_timer.stop()

    def __on_activity_detected(self):
        if not self.__is_activity_running:
            self.__is_activity_running = True
            self.__activity_returns_callback()

        self.__restart_timer()

    def __on_inactivity_timer_end(self):
        # print("{}: __on_inactivity_timer_end".format(time.time()))
        self.__is_activity_running = False
        self.__inactivity_callback()

    def __on_key_pressed(self):
        if self.__is_started:
            # print("{}: activité clavier".format(time.time()))
            self.__on_activity_detected()

    def __check_cursor_move(self):
        pos = QtGui.QCursor.pos()
        if pos != self.__mouse_position:
            self.__mouse_position = pos
            # print("{}: activité souris".format(time.time()))
            self.__on_activity_detected()

    def __restart_timer(self):
        # print("{}: __restart_inactivity_timer".format(time.time()))
        self.__inactivity_timer.start()
        self.__mouse_timer.start()

    def __create_mouse_timer(self) -> QTimer:
        mouse_timer = QTimer()
        mouse_timer.setInterval(self.__DELAY_MOUSE_DETECTION)
        mouse_timer.timeout.connect(self.__check_cursor_move)
        return mouse_timer

    def __create_inactivity_timer(self) -> QTimer:
        inactivity_timer = QTimer()
        inactivity_timer.setSingleShot(True)
        inactivity_timer.setInterval(self.__DELAY_INACTIVITY)
        inactivity_timer.timeout.connect(self.__on_inactivity_timer_end)
        return inactivity_timer


class KeyPressedSignal(QObject):
    on_key_pressed = pyqtSignal()


class KeyboardListener(QThread):

    def __init__(self, parent):
        QThread.__init__(self, parent)
        self.signal = KeyPressedSignal()
        keyboard.on_press(self.__on_key_pressed)

    def __on_key_pressed(self, event: KeyboardEvent):
        # noinspection PyUnresolvedReferences
        self.signal.on_key_pressed.emit()
