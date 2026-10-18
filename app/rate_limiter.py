import time
from collections import defaultdict
from flask import request

# In-memory storage for rate limiting: ip -> list of timestamps
_ip_requests = defaultdict(list)


def is_rate_limited(max_requests=5, window_seconds=600):
    """
    Check if the current request IP has exceeded max_requests in window_seconds.
    Returns (is_limited: bool, remaining_seconds: int)
    """
    # Determine client IP (considering reverse proxies if headers present)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1')
    if ',' in ip:
        ip = ip.split(',')[0].strip()

    now = time.time()
    cutoff = now - window_seconds

    # Filter timestamps to keep only recent ones within window
    timestamps = [t for t in _ip_requests[ip] if t > cutoff]
    _ip_requests[ip] = timestamps

    if len(timestamps) >= max_requests:
        oldest_in_window = timestamps[0]
        remaining = int(window_seconds - (now - oldest_in_window))
        return True, max(1, remaining)

    # Record this request
    _ip_requests[ip].append(now)
    return False, 0
