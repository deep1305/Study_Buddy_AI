from __future__ import annotations

import sys
import traceback
from typing import Optional


class CustomException(Exception):
    """
    Exception wrapper that adds location (file/line) details.

    Best usage:
        try:
            ...
        except Exception as e:
            raise CustomException("Something failed", e) from e
    """

    def __init__(self, message: str, error_detail: Optional[BaseException] = None):
        self.message = message
        self.error_detail = error_detail
        self.error_message = self.get_detailed_error_message(message, error_detail)
        super().__init__(self.error_message)

    @staticmethod
    def _extract_location(err: Optional[BaseException]) -> tuple[str, str]:
        """
        Return (filename, lineno) for the most relevant traceback frame.
        """
        tb = err.__traceback__ if err is not None else sys.exc_info()[2]
        if tb is None:
            return ("Unknown File", "Unknown Line")

        frames = traceback.extract_tb(tb)
        if not frames:
            return ("Unknown File", "Unknown Line")

        last = frames[-1]
        return (last.filename, str(last.lineno))

    @classmethod
    def get_detailed_error_message(
        cls,
        message: str,
        error_detail: Optional[BaseException],
    ) -> str:
        file_name, line_number = cls._extract_location(error_detail)
        return (
            f"{message} | Error: {error_detail} | File: {file_name} | Line: {line_number}"
        )

    def __str__(self) -> str:
        return self.error_message