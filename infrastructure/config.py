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