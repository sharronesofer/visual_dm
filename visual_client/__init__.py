"""
Visual DM Frontend Application
"""

from visual_client.core.utils import *
from visual_client.ui import *
from visual_client.game import *

__all__ = [
    # Add other public exports as needed
]

"""
visual_client package initialiser.

• Wraps requests.get/post/… so every call gets a sensible timeout.
• Slow-path endpoints that hit GPT get a longer timeout automatically.
"""

import requests
from functools import wraps

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
DEFAULT_TIMEOUT = 10       # seconds for normal REST calls
GPT_TIMEOUT     = 60      # seconds for endpoints that wait on GPT

# Add or edit keywords here if your GPT routes change.
GPT_ENDPOINT_KEYWORDS = {
    "/dm_response",
    "/generate_portrait",
    "/gpt/",               # example pattern
}

# ------------------------------------------------------------------
# Wrapper
# ------------------------------------------------------------------
def _wrap(method_name):
    original = getattr(requests, method_name)

    @wraps(original)
    def wrapper(*args, **kwargs):
        # If caller already set timeout explicitly, keep it.
        if "timeout" in kwargs:
            return original(*args, **kwargs)

        # Infer timeout from URL.
        url = str(args[0]) if args else kwargs.get("url", "")
        timeout = (GPT_TIMEOUT if any(k in url for k in GPT_ENDPOINT_KEYWORDS)
                   else DEFAULT_TIMEOUT)
        kwargs["timeout"] = timeout
        return original(*args, **kwargs)

    return wrapper


for _m in ("get", "post", "put", "delete", "patch"):
    setattr(requests, _m, _wrap(_m))
