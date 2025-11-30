from datetime import datetime, timedelta
from typing import Dict

from fastapi import HTTPException, status
from app.core.config import GLOBAL_RATE_LIMIT, PER_USER_RATE_LIMIT, WINDOW_SECONDS


class FixedWindowRateLimiter:
    def __init__(self, global_limit: int, user_limit: int, window_seconds: int) -> None:
        self.global_limit = global_limit
        self.user_limit = user_limit
        self.window = timedelta(seconds=window_seconds)
        self.global_count: int = 0
        self.global_window_start: datetime = datetime.utcnow()
        self.user_counters: Dict[str, int] = {}
        self.user_window_start: Dict[str, datetime] = {}

    def _reset_window_if_needed(self) -> None:
        now = datetime.utcnow()
        if now - self.global_window_start >= self.window:
            self.global_window_start = now
            self.global_count = 0
            self.user_counters.clear()
            self.user_window_start.clear()

    def _increment_user(self, user_id: str) -> None:
        current = self.user_counters.get(user_id, 0)
        self.user_counters[user_id] = current + 1
        if user_id not in self.user_window_start:
            self.user_window_start[user_id] = datetime.utcnow()

    def check(self, user_id: str) -> None:
        self._reset_window_if_needed()
        
        if self.global_count >= self.global_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests (global limit). Please try again later.",
            )
        
        user_count = self.user_counters.get(user_id, 0)
        if user_count >= self.user_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests for this user. Please try again later.",
            )
        
        self.global_count += 1
        self._increment_user(user_id)


rate_limiter = FixedWindowRateLimiter(
    global_limit=GLOBAL_RATE_LIMIT,
    user_limit=PER_USER_RATE_LIMIT,
    window_seconds=WINDOW_SECONDS,
)


def check_rate_limit(user_id: str) -> None:
    rate_limiter.check(user_id)
