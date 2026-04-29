import os
from typing import Dict


def build_headers(csrf_token: str | None, cookie_header: str | None, referer: str = "https://www.instagram.com/") -> Dict[str, str]:
    user_agent = os.getenv(
        "INSTAGRAM_USER_AGENT",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 246.0.0.0.0",
    )

    x_ig_app_id = os.getenv("INSTAGRAM_APP_ID", "936619743392459")

    headers = {
        "User-Agent": user_agent,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "x-ig-app-id": x_ig_app_id,
        "Referer": referer,
    }

    #SOLO agregar si existen (clave)
    if cookie_header:
        headers["Cookie"] = cookie_header

    if csrf_token:
        headers["X-CSRFToken"] = csrf_token

    return headers