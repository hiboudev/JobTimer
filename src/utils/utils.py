from typing import Tuple


def seconds_to_hms(time: float) -> Tuple[int, int, int]:
    m, s = divmod(round(time), 60)
    h, m = divmod(m, 60)
    return h, m, s


def hms_to_seconds(hours: int, minutes: int, seconds: int) -> int:
    return hours * 3600 + minutes * 60 + seconds
