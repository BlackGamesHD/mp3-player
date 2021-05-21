def duration_from_seconds(s):
    """Module to get the convert Seconds to a time like format."""
    s = s
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    time_minutes = "{:02d}:{:02d}".format(int(m),
                                          int(s))
    return time_minutes
