from abc import ABC, abstractmethod
from typing import List
from domain.post import Post


class PostScraper(ABC):
    """
    Contrato (interfaz) que define cómo se deben obtener publicaciones de Instagram.

    Este contrato NO implementa lógica.
    Solo define qué métodos deben existir.

    Cualquier clase que haga scraping (Instaloader, API, etc.)
    debe cumplir con este contrato.
    """

    @abstractmethod
    def get_latest_posts(self, username: str, limit: int) -> List[Post]:
        """
        Método obligatorio que debe implementar cualquier scraper.

        Parámetros:
        - username: nombre de usuario de Instagram del cual se obtendrán las publicaciones
        - limit: número máximo de publicaciones a traer

        Retorna:
        - Lista de objetos tipo Post con la metadata ya procesada
        """
        pass


class PostRepository(ABC):
    """
    Contrato (interfaz) que define cómo se deben guardar las publicaciones.

    Permite cambiar fácilmente la forma de persistencia:
    - JSON
    - Base de datos
    - Excel
    - API externa

    sin modificar la lógica principal del sistema.
    """

    @abstractmethod
    def save_posts(self, posts: List[Post], file_path: str) -> None:
        """
        Método obligatorio para guardar publicaciones.

        Parámetros:
        - posts: lista de objetos Post que se van a guardar
        - file_path: ruta donde se almacenarán los datos

        Retorna:
        - No retorna nada (None), solo realiza la acción de guardado
        """
        pass