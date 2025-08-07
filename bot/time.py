from datetime import datetime
from pathlib import Path
from email.utils import parsedate_to_datetime


class Clock:
    file_path: Path

    def __init__(self):
        self.file_path = Path.cwd().joinpath("config").joinpath("time.txt")

    def get_time_log(self) -> str | None:
        """
        Get the time stored on `./config/time.txt`
        """
        if not self.file_path.exists():
            return None
        return self.file_path.read_text().strip()

    def convert_to_datetime(self, date_str: str) -> datetime:
        """
        Convert `Thu, 07 Aug 2025 12:20:31 GMT` like format to `2025-08-07 17:02:50.820296+00:00`
        """
        return parsedate_to_datetime(date_str)

    # Compares arg_time with base_time. if arg_time is > base_time then returns True
    def compare_time(self, arg_time: str | datetime, base_time: str) -> bool:
        """
        Compares the time of format `2025-08-07 17:02:50.820296+00:00`. Returns true if arg_time is greater (more recent) than base_time
        """
        if not isinstance(arg_time, datetime):
            arg_time = datetime.fromisoformat(arg_time)

        base_time: datetime = datetime.fromisoformat(base_time)

        return arg_time > base_time

    def save_time_log(self, data: str):
        """
        Saves the time to `./config/time.txt`
        """
        self.file_path.write_text(data)
