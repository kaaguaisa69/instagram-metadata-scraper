import os
from dotenv import load_dotenv


# Carga en memoria las variables definidas dentro del archivo .env
# Esto permite leer usuario y contraseña sin escribirlos directo en el código.
load_dotenv()


def get_instagram_credentials() -> tuple[str, str]:
    """
    Obtiene las credenciales de Instagram desde variables de entorno.

    Retorna:
    - Una tupla con:
        1. username -> nombre de usuario de Instagram
        2. password -> contraseña de Instagram

    Lanza:
    - ValueError si falta alguna credencial en el archivo .env
    """

    # Lee el valor de la variable INSTAGRAM_USERNAME.
    # Si no existe, devuelve una cadena vacía.
    username = os.getenv("INSTAGRAM_USERNAME", "")

    # Lee el valor de la variable INSTAGRAM_PASSWORD.
    # Si no existe, devuelve una cadena vacía.
    password = os.getenv("INSTAGRAM_PASSWORD", "")

    # Valida que ambas credenciales existan antes de continuar.
    # Esto evita que el programa falle más adelante con errores menos claros.
    if not username or not password:
        raise ValueError(
            "Faltan credenciales en el archivo .env. "
            "Debes definir INSTAGRAM_USERNAME e INSTAGRAM_PASSWORD."
        )

    # Retorna las credenciales ya validadas.
    return username, password