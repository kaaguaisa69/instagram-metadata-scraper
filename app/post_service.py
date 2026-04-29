from typing import List

from domain.contracts import PostRepository, PostScraper
from domain.post import Post


class PostService:
    """
    Servicio de aplicación que coordina el caso de uso principal del sistema.

    Responsabilidad de esta clase:
    - pedir publicaciones al scraper
    - enviar las publicaciones al repositorio
    - devolver el resultado al flujo principal

    Esta clase no conoce detalles internos de la implementación concreta del scraper.
    Esta clase NO conoce cómo se escribe el JSON internamente.
    Esta clase solo orquesta el proceso.
    """

    def __init__(self, scraper: PostScraper, repository: PostRepository) -> None:
        """
        Constructor del servicio.

        Parámetros:
        - scraper: componente que sabe obtener publicaciones
        - repository: componente que sabe guardar publicaciones

        Ambos se reciben como abstracciones para que el servicio
        no dependa de implementaciones concretas.
        """

        # Guarda la dependencia encargada de obtener publicaciones.
        self.scraper = scraper

        # Guarda la dependencia encargada de persistir publicaciones.
        self.repository = repository

    def extract_and_save_posts(
        self,
        profile_username: str,
        limit: int,
        file_path: str
    ) -> List[Post]:
        """
        Ejecuta el caso de uso principal del sistema:
        1. extraer publicaciones
        2. guardarlas en archivo
        3. devolverlas al llamador

        Parámetros:
        - profile_username: usuario de Instagram que se desea consultar
        - limit: cantidad máxima de publicaciones a obtener
        - file_path: ruta donde se guardará el archivo JSON

        Retorna:
        - lista de publicaciones obtenidas y procesadas
        """

        # Solicita al scraper las publicaciones más recientes del perfil indicado.
        posts = self.scraper.get_latest_posts(profile_username, limit)

        # Envía la lista resultante al repositorio para su almacenamiento.
        self.repository.save_posts(posts, file_path)

        # Devuelve la lista para que el flujo principal pueda usarla
        # en validaciones, impresiones o pasos posteriores.
        return posts