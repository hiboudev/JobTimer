class Job:

    def __init__(self, job_id: int, name: str, hourly_rate: int, elapsed_time: int):
        self.id = job_id
        self.name = name
        self.hourly_rate = hourly_rate
        self.elapsed_seconds = elapsed_time

    def __repr__(self):
        return f"[Job => id:{self.id}, name:{self.name}, hourly rate:{self.hourly_rate}, elapsed_time:{self.elapsed_seconds}]"
