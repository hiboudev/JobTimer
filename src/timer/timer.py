import datetime
from threading import Thread, Event
from types import FunctionType
from typing import Union

from data.job import Job


class JobTimer:

    def __init__(self, time_update_callback):
        self.__time_update_callback = time_update_callback
        self.__timer_flag = Event()
        self.__timer = None
        self.__counter = TimeCounter()
        self.__job: Union[Job, None] = None
        self.__is_running = False

    def set_job(self, job: Job):
        self.stop()
        self.__counter.reset()
        self.__job = job
        self.__counter.add_seconds(job.elapsed_time)

        self.__timer_callback()

    def start(self):
        self.__counter.stop()

        self.__timer_flag.clear()
        self.__counter.start()

        self.__timer = Timer(self.__timer_flag, self.__timer_callback)
        self.__timer.start()
        self.__is_running = True

    def stop(self):
        self.__timer_flag.set()
        self.__counter.stop()
        if self.__job is not None:
            self.__job.elapsed_time = self.__counter.get_total_seconds()
        self.__is_running = False

        self.__timer_callback()

    def __timer_callback(self):
        self.__time_update_callback(self.__counter.get_formatted_time())

    @property
    def is_running(self) -> bool:
        return self.__is_running


class TimeCounter:

    def __init__(self):
        self.__begin = None
        self.__additional_seconds = 0

    def reset(self):
        self.__begin = None
        self.__additional_seconds = 0

    def add_seconds(self, seconds: float):
        self.__additional_seconds += seconds

    def start(self):
        self.__begin = datetime.datetime.now()

    def stop(self):
        self.__additional_seconds += self.__get_current_elapsed_time()
        self.__begin = None

    def get_total_seconds(self) -> float:
        return self.__get_current_elapsed_time() + self.__additional_seconds

    def get_formatted_time(self) -> str:
        m, s = divmod(round(self.get_total_seconds()), 60)
        h, m = divmod(m, 60)
        return f'{h:02d}:{m:02d}:{s:02d}'

    def __get_current_elapsed_time(self) -> float:
        return 0 if self.__begin is None else (datetime.datetime.now() - self.__begin).total_seconds()


class Timer(Thread):
    def __init__(self, event: Event, callback: FunctionType):
        Thread.__init__(self)
        self.__stopped = event
        self.__callback = callback

    def run(self):
        while not self.__stopped.wait(0.5):
            self.__callback()
