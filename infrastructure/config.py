import os
from dotenv import load_dotenv


# Carga en memoria las variables definidas dentro del archivo .env
# Esto permite leer usuario y contraseña sin escribirlos directo en el código.
load_dotenv()


def get_instagram_username() -> str:
    """
    Obtiene el username de Instagram desde variables de entorno.

    Retorna:
    - El nombre de usuario de Instagram

    Lanza:
    - ValueError si falta la credencial en el archivo .env
    """

    # Lee el valor de la variable INSTAGRAM_USERNAME.
    # Si no existe, devuelve una cadena vacía.
    username = os.getenv("INSTAGRAM_USERNAME", "")

    # Valida que el username exista antes de continuar.
    if not username:
        raise ValueError(
            "Falta INSTAGRAM_USERNAME en el archivo .env.\n"
            "Ejemplo de contenido del .env:\n"
            "INSTAGRAM_USERNAME=tu_usuario_sin_arroba"
        )

    # Retorna el username ya validado.
    return username


def get_browser_name() -> str:
    """
    Obtiene el nombre del navegador desde variables de entorno.

    Retorna:
    - Nombre del navegador (por defecto: firefox)
    """

    return os.getenv("INSTAGRAM_BROWSER", "firefox").lower()


def get_instagram_cookies() -> dict:
    """
    Lee las cookies necesarias para usar una sesión de Instagram

    Retorna:
    - Dict con claves: sessionid, csrftoken, ds_user_id

    Lanza:
    - ValueError si falta alguna variable obligatoria en el .env
    """

    sessionid = os.getenv("INSTAGRAM_SESSIONID", "")
    csrftoken = os.getenv("INSTAGRAM_CSRFTOKEN", "")
    ds_user_id = os.getenv("INSTAGRAM_DS_USER_ID", "")

    missing = []
    if not sessionid:
        missing.append("INSTAGRAM_SESSIONID")
    if not csrftoken:
        missing.append("INSTAGRAM_CSRFTOKEN")
    if not ds_user_id:
        missing.append("INSTAGRAM_DS_USER_ID")

    if missing:
        raise ValueError(
            "Faltan variables de entorno obligatorias: " + ", ".join(missing)
        )

    return {
        "sessionid": sessionid,
        "csrftoken": csrftoken,
        "ds_user_id": ds_user_id,
    }