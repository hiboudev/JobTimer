import os
import sqlite3
from typing import List

from data.job import Job


class Database:
    # DB_NAME = "../sql/jobs_database.db"
    DB_NAME = "jobs_database.db"

    def __init__(self):
        self.__check_database()

    def add_job(self, job_name: str, hourly_rate: int) -> Job:
        connection = sqlite3.connect(self.DB_NAME)
        cursor = connection.cursor()

        cursor.execute(f'''INSERT INTO jobs (name, hourlyRate, elapsedTime) VALUES(?, ?, ?)''',
                       [job_name, hourly_rate, 0])

        job = Job(cursor.lastrowid, job_name, hourly_rate, 0)

        connection.commit()
        connection.close()

        return job

    def get_jobs(self) -> List[Job]:
        connection = sqlite3.connect(self.DB_NAME)
        cursor = connection.cursor()

        cursor.execute('''SELECT id, name, hourlyRate, elapsedTime FROM jobs''')

        jobs = []
        rows = cursor.fetchall()
        for row in rows:
            job = Job(row[0], row[1], row[2], row[3])
            jobs.append(job)

        connection.close()

        return jobs

    def update_job_elapsed_time(self, job: Job):
        connection = sqlite3.connect(self.DB_NAME)
        cursor = connection.cursor()

        cursor.execute('''UPDATE jobs SET elapsedTime=? WHERE id=?''',
                       [job.elapsed_time, job.id])

        connection.commit()
        connection.close()

    def edit_job(self, job_id: int, name: str, hourly_rate: int):
        connection = sqlite3.connect(self.DB_NAME)
        cursor = connection.cursor()

        cursor.execute('''UPDATE jobs SET name=?, hourlyRate=? WHERE id=?''',
                       [name, hourly_rate, job_id])

        connection.commit()
        connection.close()

    def delete_job(self, job):
        connection = sqlite3.connect(self.DB_NAME)
        cursor = connection.cursor()

        cursor.execute('''DELETE FROM jobs WHERE id=?''',
                       [job.id])

        connection.commit()
        connection.close()

    def __check_database(self):
        if not os.path.isfile(self.DB_NAME):
            connection = sqlite3.connect(self.DB_NAME)
            cursor = connection.cursor()

            cursor.execute('''
                        CREATE TABLE jobs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        hourlyRate INTEGER NOT NULL,
                        elapsedTime INTEGER DEFAULT 0)
                         ''')

            connection.commit()
            connection.close()
