from datetime import datetime, timedelta
import pytz
from babel.dates import format_timedelta

def time_since(struct_time, user_timezone):
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
    return format_timedelta(delta, granularity='minute', locale='no')