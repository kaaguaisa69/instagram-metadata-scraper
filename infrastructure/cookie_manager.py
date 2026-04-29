from typing import Tuple, Dict
from infrastructure.config import get_instagram_cookies


def load_cookies_from_env() -> Tuple[Dict[str, str], str]:
    """
    Carga las cookies necesarias desde variables de entorno y
    construye la cabecera Cookie usada en requests.

    Retorna:
    - Tuple(cookies_dict, cookie_header_string)
    """

    cookies = get_instagram_cookies()

    cookie_header = (
        f"sessionid={cookies['sessionid']}; "
        f"csrftoken={cookies['csrftoken']}; "
        f"ds_user_id={cookies['ds_user_id']}"
    )

    return cookies, cookie_header
