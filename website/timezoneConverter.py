from datetime import datetime, timedelta
import pytz
from babel.dates import format_timedelta
import re
import time

def parse_struct_time_string(time_string):
    # Regular expression to extract the numeric values from the string
    match = re.search(
        r'time\.struct_time\(tm_year=(\d+), tm_mon=(\d+), tm_mday=(\d+), '
        r'tm_hour=(\d+), tm_min=(\d+), tm_sec=(\d+), tm_wday=(\d+), '
        r'tm_yday=(\d+), tm_isdst=(-?\d+)\)',
        time_string
    )
    if not match:
        raise ValueError("Invalid time.struct_time string format")
    
    # Extract the values and convert them to integers
    values = tuple(map(int, match.groups()))
    
    # Convert the extracted values to a time.struct_time
    return time.struct_time(values)


def time_since(struct_time, user_timezone):
    #Convert struct_time from string to array:
    try:
        struct_time = parse_struct_time_string(struct_time)
    except:
        struct_time=time.struct_time((2024, 1, 1, 16, 0, 6, 0, 1, -1))
        pass

    # Convert struct_time to UTC datetime
    
    utc_time = datetime(*struct_time[:6])
    utc_time = pytz.utc.localize(utc_time)
    
    # Convert UTC to user's timezone
    user_tz = pytz.timezone(user_timezone)
    local_time = utc_time.astimezone(user_tz)
    
    # Calculate the time difference
    now = datetime.now(user_tz)
    delta = now - local_time
    
    # Format the time difference
    return format_timedelta(delta, granularity='minute', locale='en')

if __name__ == '__main__':
    print(time_since('time.struct_time(tm_year=2025, tm_mon=1, tm_mday=27, tm_hour=16, tm_min=0, tm_sec=6, tm_wday=0, tm_yday=1, tm_isdst=0)','UTC'))