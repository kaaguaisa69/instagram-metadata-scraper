import os
import time
import random
from itertools import islice
from typing import List

import instaloader
from instaloader import Profile
from instaloader.exceptions import ProfileNotExistsException

from domain.contracts import PostScraper
from domain.post import Post


class InstagramScraper(PostScraper):
    """
    Implementación concreta del contrato PostScraper usando Instaloader.

    Responsabilidad de esta clase:
    - cargar sesión previamente importada desde cookies del navegador
    - verificar que la sesión sea válida
    - obtener publicaciones del perfil objetivo
    - transformar cada publicación al modelo Post
    - aplicar delays entre requests para evitar rate limiting
    """

    # Rango de delay (segundos) entre cada publicación procesada.
    # Esto reduce la probabilidad de que Instagram bloquee la sesión.
    MIN_DELAY = 1.5
    MAX_DELAY = 3.5

    def __init__(self, login_username: str) -> None:
        """
        Inicializa el scraper con el usuario que proporcionara las cookies.
        
        Funcionamiento:
        Crea una instancia de Instaloader configurada para no descargar archivos multimedia
        (imagenes/videos), optimizando asi la velocidad y el ancho de banda, ya que
        solo nos interesa la metadata (texto y estadisticas).
        """
        self.login_username = login_username

        # Archivo local donde se guardó la sesión importada.
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

    def _load_session(self) -> None:
        """
        Carga la sesion de autenticacion desde un archivo local.
        
        Funcionamiento:
        Busca el archivo de sesion generado previamente por setup_session.py. 
        Si el archivo existe, lo carga en el motor de Instaloader para evitar 
        tener que iniciar sesion nuevamente y reducir el riesgo de bloqueo.
        """

        if not os.path.exists(self.session_file):
            raise FileNotFoundError(
                f"No se encontró el archivo de sesión '{self.session_file}'.\n"
                f"Ejecuta primero: python setup_session.py"
            )

        try:
            self.loader.load_session_from_file(
                self.login_username,
                self.session_file
            )
        except Exception as error:
            raise RuntimeError(
                f"No se pudo cargar la sesión desde '{self.session_file}'.\n"
                f"El archivo puede estar corrupto.\n"
                f"Ejecuta: python setup_session.py\n"
                f"Detalle: {error}"
            ) from error

        # Verifica que la sesión cargada sea válida.
        logged_user = self.loader.test_login()
        if not logged_user:
            raise RuntimeError(
                "La sesión cargada no es válida o ha expirado.\n"
                "Inicia sesión en Instagram desde tu navegador "
                "y ejecuta: python setup_session.py"
            )

        print(f"Sesion cargada correctamente para: {logged_user}")

    def get_latest_posts(self, username: str, limit: int) -> List[Post]:
        """
        Obtiene las publicaciones más recientes del perfil indicado.

        Parámetros:
        - username: nombre de usuario del perfil objetivo
        - limit: cantidad máxima de publicaciones a obtener

        Retorna:
        - Lista de objetos Post con metadata procesada
        """

        # Asegura que exista una sesión válida.
        self._load_session()

        # Obtiene el perfil objetivo.
        print(f"Obteniendo perfil de: {username}")

        try:
            if username == self.login_username:
                profile = Profile.own_profile(self.loader.context)
            else:
                profile = Profile.from_username(self.loader.context, username)
        except ProfileNotExistsException:
            raise ValueError(
                f"El perfil '{username}' no existe o no es accesible."
            )
        except Exception as error:
            raise RuntimeError(
                f"Error al obtener el perfil '{username}': {error}"
            ) from error

        print(f"Perfil encontrado: {profile.username} ({profile.full_name})")
        print(f"Publicaciones totales: {profile.mediacount}")
        print(f"Extrayendo las últimas {limit} publicaciones...")
        print()

        posts: List[Post] = []

        for index, post in enumerate(islice(profile.get_posts(), limit), start=1):
            try:
                # Intentamos obtener la ubicacion de forma segura.
                # Si falla (error 201), la dejamos como None para no perder el resto del post.
                location_name = None
                try:
                    if post.location:
                        location_name = post.location.name
                except Exception:
                    location_name = "No disponible"

                current_post = Post(
                    shortcode=post.shortcode,
                    post_id=str(post.mediaid),
                    permalink=f"https://www.instagram.com/p/{post.shortcode}/",
                    date_utc=post.date_utc.isoformat() if post.date_utc else "",
                    caption=post.caption,
                    hashtags=list(post.caption_hashtags),
                    mentions=list(post.caption_mentions),
                    typename=post.typename,
                    is_video=post.is_video,
                    likes=post.likes,
                    comments=post.comments,
                    url=post.url,
                    location=location_name,
                    tagged_users=list(post.tagged_users),
                    owner_username=post.owner_username,
                )

                posts.append(current_post)
                
                # Mostramos mas informacion en la consola para que veas el avance real
                print(f"  [{index}/{limit}] Procesado: {current_post.shortcode}")
                print(f"      Tipo: {current_post.typename} | Likes: {current_post.likes} | Comentarios: {current_post.comments}")
                if current_post.hashtags:
                    print(f"      Hashtags: {', '.join(current_post.hashtags[:3])}...")
                print(f"      Fecha: {current_post.date_utc}")
                print("-" * 40)

            except Exception as error:
                print(f"  [{index}/{limit}] Error critico al procesar: {error}")
                continue

            # Delay aleatorio entre requests para evitar rate limiting.
            # Solo aplica si no es la última publicación.
            if index < limit:
                delay = random.uniform(self.MIN_DELAY, self.MAX_DELAY)
                time.sleep(delay)

        return posts