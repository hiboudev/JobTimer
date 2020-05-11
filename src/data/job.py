class Job:

    def __init__(self, id: int, name: str, elapsed_time: int):
        self.id = id
        self.name = name
        self.elapsed_time = elapsed_time

    def __repr__(self):
        return f"[Job => id:{self.id}, name:{self.name}, elapsed_time:{self.elapsed_time}]"
