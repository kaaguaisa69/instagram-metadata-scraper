import os
from itertools import islice
from typing import List

import instaloader
from instaloader import Profile
from instaloader.exceptions import (
    BadCredentialsException,
    LoginException,
    TwoFactorAuthRequiredException,
)

from domain.contracts import PostScraper
from domain.post import Post


class InstagramScraper(PostScraper):
    """
    Implementación concreta del contrato PostScraper usando Instaloader.

    Responsabilidad de esta clase:
    - iniciar sesión en Instagram
    - manejar autenticación con 2FA si aplica
    - reutilizar una sesión guardada si ya existe
    - obtener publicaciones del perfil objetivo
    - transformar cada publicación al modelo Post
    """

    def __init__(self, login_username: str, login_password: str) -> None:
        # Usuario con el que se inicia sesión en Instagram.
        self.login_username = login_username

        # Contraseña del usuario autenticado.
        self.login_password = login_password

        # Archivo local donde se guardará la sesión.
        self.session_file = f"session-{self.login_username}"

        # Instancia principal de Instaloader.
        # Se desactivan descargas porque solo queremos metadata.
        self.loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
        )

    def login(self) -> None:
        """
        Inicia sesión en Instagram.

        Flujo:
        1. intenta reutilizar sesión guardada
        2. si no sirve, hace login con usuario y contraseña
        3. si pide 2FA, solicita el código
        4. guarda la sesión para próximas ejecuciones
        """

        if os.path.exists(self.session_file):
            try:
                self.loader.load_session_from_file(
                    self.login_username,
                    self.session_file
                )

                logged_user = self.loader.test_login()
                if logged_user:
                    print(f"Sesión reutilizada correctamente para: {logged_user}")
                    return

            except Exception:
                print(
                    "La sesión guardada no es válida o no pudo cargarse. "
                    "Se hará login nuevo."
                )

        try:
            self.loader.login(self.login_username, self.login_password)
            self.loader.save_session_to_file(self.session_file)
            print("Inicio de sesión completado correctamente.")
            return

        except TwoFactorAuthRequiredException:
            print("Instagram solicita autenticación en dos pasos (2FA).")

            two_factor_code = input(
                "Ingresa el código 2FA generado en Google Authenticator: "
            ).strip()

            try:
                self.loader.two_factor_login(two_factor_code)
                self.loader.save_session_to_file(self.session_file)
                print("Inicio de sesión con 2FA completado correctamente.")
                return

            except BadCredentialsException as error:
                raise ValueError(
                    "El código 2FA es inválido o expiró. "
                    "Cierra el programa y vuelve a intentarlo con un código nuevo."
                ) from error

        except BadCredentialsException as error:
            raise ValueError(
                "Usuario o contraseña de Instagram inválidos."
            ) from error

        except LoginException as error:
            raise RuntimeError(
                f"Error durante el login de Instagram: {error}"
            ) from error

    def get_latest_posts(self, username: str, limit: int) -> List[Post]:
        """
        Obtiene las publicaciones más recientes del perfil indicado.

        Parámetros:
        - username: nombre de usuario del perfil objetivo
        - limit: cantidad máxima de publicaciones a obtener

        Retorna:
        - Lista de objetos Post con metadata procesada
        """

        # Asegura que exista una sesión autenticada.
        self.login()

        # Si se consulta la misma cuenta autenticada, usa directamente
        # el perfil propio de la sesión.
        # Esto evita depender de una búsqueda por username.
        if username == self.login_username:
            profile = Profile.own_profile(self.loader.context)
        else:
            # Para otros perfiles, sí se busca por username.
            profile = Profile.from_username(self.loader.context, username)

        posts: List[Post] = []

        for post in islice(profile.get_posts(), limit):
            current_post = Post(
                # Código corto único de la publicación.
                shortcode=post.shortcode,

                # ID interno de la publicación.
                post_id=str(post.mediaid),

                # Enlace público directo del post.
                permalink=f"https://www.instagram.com/p/{post.shortcode}/",

                # Fecha en formato ISO UTC.
                date_utc=post.date_utc.isoformat() if post.date_utc else "",

                # Texto de la publicación.
                caption=post.caption,

                # Hashtags presentes en el caption.
                hashtags=list(post.caption_hashtags),

                # Menciones presentes en el caption.
                mentions=list(post.caption_mentions),

                # Tipo de publicación: imagen, video o carrusel.
                typename=post.typename,

                # Indica si es video.
                is_video=post.is_video,

                # Cantidad de likes.
                likes=post.likes,

                # Cantidad de comentarios.
                comments=post.comments,

                # URL del recurso principal.
                url=post.url,

                # Ubicación si existe.
                location=post.location.name if post.location else None,

                # Usuarios etiquetados.
                tagged_users=list(post.tagged_users),

                # Usuario propietario del contenido.
                owner_username=post.owner_username,
            )

            posts.append(current_post)

        return posts