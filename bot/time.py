from datetime import datetime, timezone
from pathlib import Path
from email.utils import parsedate_to_datetime
import logging


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

    def convert_to_datetime(self, date_str: str) -> datetime | None:
        """
        Convert `Thu, 07 Aug 2025 12:20:31 GMT` like format to `2025-08-07 17:02:50.820296+00:00`
        """
        try:
            return parsedate_to_datetime(date_str)
        except (TypeError, ValueError):
            try:
                return datetime.fromisoformat(date_str)
            except ValueError:
                logging.error("Failed to parse the time")
                return None

    # Compares arg_time with base_time. if arg_time is > base_time then returns True
    def compare_time(self, arg_time: str | datetime, base_time: str) -> bool:
        """
        Compares the time of format `2025-08-07 17:02:50.820296+00:00`. Returns true if arg_time is greater (more recent) than base_time
        """
        if not isinstance(arg_time, datetime):
            arg_time = datetime.fromisoformat(arg_time)

        base_time: datetime = datetime.fromisoformat(base_time)

        return arg_time > base_time

    def save_time_log(self):
        """
        Saves the time to `./config/time.txt`
        """
        dt: str = str(datetime.now(timezone.utc))
        self.file_path.write_text(dt)
