"""
Helper for time related functions
"""

# Standard Library
from datetime import datetime


def get_time_delta(then, now=datetime.now(), interval="default"):
    """
    Returns a duration as specified by variable interval
    functions, except total_duration, returns [quotient, remainder]
    :param then:
    :type then:
    :param now:
    :type now:
    :param interval:
    :type interval:
    :return:
    :rtype:
    """

    duration = now.replace(tzinfo=None) - then.replace(tzinfo=None)
    duration_in_seconds = duration.total_seconds()

    def years():
        """
        Return years
        :return:
        :rtype:
        """

        return divmod(duration_in_seconds, 31536000)  # Seconds in a year = 31536000.

    def days(from_seconds=None):
        """
        Return days
        :param from_seconds:
        :type from_seconds:
        :return:
        :rtype:
        """

        return divmod(
            from_seconds if from_seconds is not None else duration_in_seconds, 86400
        )  # Seconds in a day = 86400

    def hours(from_seconds=None):
        """
        Return hours
        :param from_seconds:
        :type from_seconds:
        :return:
        :rtype:
        """

        return divmod(
            from_seconds if from_seconds is not None else duration_in_seconds, 3600
        )  # Seconds in an hour = 3600

    def minutes(from_seconds=None):
        """
        Return minutes
        :param from_seconds:
        :type from_seconds:
        :return:
        :rtype:
        """

        return divmod(
            from_seconds if from_seconds is not None else duration_in_seconds, 60
        )  # Seconds in a minute = 60

    def seconds(from_seconds=None):
        """
        Return seconds
        :param from_seconds:
        :type from_seconds:
        :return:
        :rtype:
        """

        if from_seconds is not None:
            return divmod(from_seconds, 1)
        return duration_in_seconds

    def total_duration():
        """
        Return total time difference
        :return:
        :rtype:
        """

        duration_years = years()
        duration_days = days(duration_years[1])
        duration_hours = hours(duration_days[1])
        duration_minutes = minutes(duration_hours[1])
        duration_seconds = seconds(duration_minutes[1])

        return (
            f"{duration_years[0]} years, "
            f"{duration_days[0]} days, "
            f"{duration_hours[0]} hours, "
            f"{duration_minutes[0]} minutes and "
            f"{duration_seconds[0]} seconds"
        )

    return {
        "years": int(years()[0]),
        "days": int(days()[0]),
        "hours": int(hours()[0]),
        "minutes": int(minutes()[0]),
        "seconds": int(seconds()),
        "default": total_duration(),
    }[interval]
