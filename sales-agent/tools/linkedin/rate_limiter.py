import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from collections import defaultdict


class LinkedInRateLimiter:
    """
    Rate limiter for LinkedIn actions to prevent account suspension

    Implements rolling window rate limiting with safety delays
    """

    # LinkedIn safety limits (conservative to avoid suspension)
    LIMITS = {
        "connection_request": {
            "per_day": 20,          # Conservative daily limit
            "per_week": 100,        # Weekly limit (resets after 7 days)
            "per_hour": 10,         # Hourly limit
            "min_delay": 120,       # Minimum 2 minutes between requests
            "max_delay": 300        # Maximum 5 minutes delay
        },
        "message": {
            "per_day": 50,
            "per_hour": 20,
            "per_minute": 5,
            "min_delay": 60,        # 1 minute between messages
            "max_delay": 180        # 3 minutes delay
        },
        "profile_visit": {
            "per_day": 80,
            "per_hour": 40,
            "min_delay": 30,        # 30 seconds between visits
            "max_delay": 90
        },
        "engagement": {
            "per_day": 100,
            "per_hour": 50,
            "min_delay": 20,        # 20 seconds between likes/comments
            "max_delay": 60
        },
        "search": {
            "per_day": 50,
            "per_hour": 20,
            "min_delay": 15,
            "max_delay": 45
        }
    }

    def __init__(self, db: Session = None):
        self.db = db
        self.action_history = defaultdict(list)  # In-memory tracking
        self.last_action_time = {}

    def can_perform_action(self, action_type: str) -> tuple[bool, Optional[str]]:
        """
        Check if action can be performed within rate limits

        Args:
            action_type: Type of action (connection_request, message, etc.)

        Returns:
            Tuple of (can_perform, reason_if_not)
        """
        if action_type not in self.LIMITS:
            return False, f"Unknown action type: {action_type}"

        limits = self.LIMITS[action_type]
        now = datetime.utcnow()

        # Check hourly limit
        if "per_hour" in limits:
            hour_ago = now - timedelta(hours=1)
            recent_actions = [
                ts for ts in self.action_history[action_type]
                if ts > hour_ago
            ]
            if len(recent_actions) >= limits["per_hour"]:
                return False, f"Hourly limit reached ({limits['per_hour']}/hour)"

        # Check daily limit
        if "per_day" in limits:
            day_ago = now - timedelta(days=1)
            recent_actions = [
                ts for ts in self.action_history[action_type]
                if ts > day_ago
            ]
            if len(recent_actions) >= limits["per_day"]:
                return False, f"Daily limit reached ({limits['per_day']}/day)"

        # Check weekly limit
        if "per_week" in limits:
            week_ago = now - timedelta(days=7)
            recent_actions = [
                ts for ts in self.action_history[action_type]
                if ts > week_ago
            ]
            if len(recent_actions) >= limits["per_week"]:
                return False, f"Weekly limit reached ({limits['per_week']}/week)"

        # Check minimum delay
        if action_type in self.last_action_time:
            time_since_last = (now - self.last_action_time[action_type]).total_seconds()
            min_delay = limits.get("min_delay", 0)

            if time_since_last < min_delay:
                wait_time = min_delay - time_since_last
                return False, f"Too soon. Wait {int(wait_time)} more seconds"

        return True, None

    def record_action(self, action_type: str):
        """
        Record that an action was performed

        Args:
            action_type: Type of action performed
        """
        now = datetime.utcnow()
        self.action_history[action_type].append(now)
        self.last_action_time[action_type] = now

        # Clean old entries (keep only last 7 days)
        week_ago = now - timedelta(days=7)
        self.action_history[action_type] = [
            ts for ts in self.action_history[action_type]
            if ts > week_ago
        ]

    def wait_if_needed(self, action_type: str) -> int:
        """
        Wait if necessary before performing action

        Args:
            action_type: Type of action to perform

        Returns:
            Seconds waited
        """
        can_perform, reason = self.can_perform_action(action_type)

        if not can_perform and "Wait" in reason:
            # Extract wait time from reason
            wait_seconds = int(reason.split()[1])
            time.sleep(wait_seconds)
            return wait_seconds

        # Add random delay for human-like behavior
        import random
        limits = self.LIMITS.get(action_type, {})
        min_delay = limits.get("min_delay", 10)
        max_delay = limits.get("max_delay", 30)

        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

        return int(delay)

    def get_stats(self, action_type: str = None) -> Dict:
        """
        Get current usage statistics

        Args:
            action_type: Optional specific action type

        Returns:
            Dictionary with usage stats
        """
        now = datetime.utcnow()
        stats = {}

        action_types = [action_type] if action_type else self.LIMITS.keys()

        for atype in action_types:
            hour_ago = now - timedelta(hours=1)
            day_ago = now - timedelta(days=1)
            week_ago = now - timedelta(days=7)

            actions = self.action_history.get(atype, [])

            stats[atype] = {
                "last_hour": len([ts for ts in actions if ts > hour_ago]),
                "last_day": len([ts for ts in actions if ts > day_ago]),
                "last_week": len([ts for ts in actions if ts > week_ago]),
                "limits": self.LIMITS.get(atype, {}),
                "can_perform": self.can_perform_action(atype)[0]
            }

        return stats

    def reset_action_type(self, action_type: str):
        """Reset tracking for specific action type (for testing)"""
        self.action_history[action_type] = []
        if action_type in self.last_action_time:
            del self.last_action_time[action_type]


class WarmupScheduler:
    """
    Gradual warmup schedule for new LinkedIn automation accounts

    Prevents immediate suspension by slowly increasing activity
    """

    WARMUP_SCHEDULE = {
        1: {"connections": 5, "messages": 10, "visits": 20},   # Week 1
        2: {"connections": 10, "messages": 20, "visits": 40},  # Week 2
        3: {"connections": 15, "messages": 35, "visits": 60},  # Week 3
        4: {"connections": 20, "messages": 50, "visits": 80},  # Week 4+
    }

    def __init__(self, start_date: datetime = None):
        self.start_date = start_date or datetime.utcnow()

    def get_current_limits(self) -> Dict[str, int]:
        """
        Get current limits based on warmup schedule

        Returns:
            Dictionary with action limits for current week
        """
        weeks_elapsed = (datetime.utcnow() - self.start_date).days // 7 + 1
        week_key = min(weeks_elapsed, 4)  # Cap at week 4

        return self.WARMUP_SCHEDULE[week_key]

    def is_action_allowed(self, action_type: str, current_count: int) -> bool:
        """
        Check if action is allowed based on warmup schedule

        Args:
            action_type: Type of action (connections, messages, visits)
            current_count: Current count for today

        Returns:
            True if action is allowed
        """
        limits = self.get_current_limits()

        action_map = {
            "connection_request": "connections",
            "message": "messages",
            "profile_visit": "visits"
        }

        limit_key = action_map.get(action_type, action_type)
        limit = limits.get(limit_key, 0)

        return current_count < limit
