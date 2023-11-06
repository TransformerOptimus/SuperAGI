from datetime import datetime


def get_time_difference(timestamp1, timestamp2):
    time_format = "%Y-%m-%d %H:%M:%S.%f"

    # Parse the given timestamp
    parsed_timestamp1 = datetime.strptime(str(timestamp1), time_format)
    parsed_timestamp2 = datetime.strptime(timestamp2, time_format)

    # Calculate the time difference
    time_difference = parsed_timestamp2 - parsed_timestamp1

    # Convert time difference to total seconds
    total_seconds = int(time_difference.total_seconds())

    # Calculate years, months, days, hours, and minutes
    years, seconds_remainder = divmod(total_seconds, (365 * 24 * 60 * 60))  # 1 year = 365 days * 24 hours * 60 minutes * 60 seconds
    months, seconds_remainder = divmod(seconds_remainder,
                                       (30 * 24 * 60 * 60))  # 1 month = 30 days * 24 hours * 60 minutes * 60 seconds
    days, seconds_remainder = divmod(seconds_remainder, 24 * 60 * 60)  # 1 day = 24 hours * 60 minutes * 60 seconds
    hours, seconds_remainder = divmod(seconds_remainder, 60 * 60)  # 1 hour = 60 minutes * 60 seconds
    minutes, _ = divmod(seconds_remainder, 60)  # 1 minute = 60 seconds

    # Create a dictionary to store the time difference
    time_difference_dict = {
        "years": years,
        "months": months,
        "days": days,
        "hours": hours,
        "minutes": minutes
    }
    return time_difference_dict


def parse_interval_to_seconds(interval: str) -> int:
    units = {"Minutes": 60, "Hours": 3600, "Days": 86400, "Weeks": 604800, "Months": 2592000}
    interval = ' '.join(interval.split())
    value, unit = interval.split(" ")

    return int(value) * units[unit]


