import os
from typing import Dict


def build_headers(csrf_token: str, cookie_header: str, referer: str = "https://www.instagram.com/") -> Dict[str, str]:
    """
    Construye headers realistas para simular un cliente móvil Instagram.

    Parámetros:
    - csrf_token: token CSRF de la sesión
    - cookie_header: cadena completa para la cabecera Cookie
    - referer: sitio de origen (por defecto la home de Instagram)

    Retorna diccionario con headers.
    Usa user-agent móvil iPhone para simular aplicación Instagram real.
    """

    # User-Agent realista de Instagram mobile (iPhone)
    # Esto es crítico: muchos endpoints móviles devuelven datos distintos que desktop
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
        "X-CSRFToken": csrf_token,
        "Referer": referer,
        "Cookie": cookie_header,
    }

    return headers
