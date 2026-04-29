import logging
import re
from datetime import datetime
from typing import List

import httpx

from domain.contracts import PostScraper
from domain.post import Post
from infrastructure.cookie_manager import load_cookies_from_env
from infrastructure.headers import build_headers
from infrastructure.delay_manager import human_delay


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class InstagramHttpScraper(PostScraper):
    """
    Scraper que usa requests HTTP directas (httpx) hacia endpoints internos
    de Instagram. Cumple el contrato `PostScraper`.

    Principios aplicados:
    - SRP: esta clase solo orquesta requests y mapea JSON a `Post`.
    - DIP: recibe la configuración desde módulos de infraestructura.
    """

    DEFAULT_MIN_DELAY = 1.0
    DEFAULT_MAX_DELAY = 3.0

    def __init__(self, min_delay: float = None, max_delay: float = None) -> None:
        # Carga cookies y construye headers realistas
        logger.info("Inicializando InstagramHttpScraper...")
        try:
            cookies, cookie_header = load_cookies_from_env()
            logger.info("✓ Cookies cargadas desde .env")
        except ValueError as e:
            logger.error("✗ Error al cargar cookies: %s", e)
            raise

        self.csrf_token = cookies.get("csrftoken")
        self.headers = build_headers(self.csrf_token, cookie_header)

        logger.debug("Headers construidos con user-agent móvil")

        # Cliente HTTP reutilizable
        self.client = httpx.Client(headers=self.headers, timeout=15.0)

        # Delays configurables
        self.min_delay = min_delay or self.DEFAULT_MIN_DELAY
        self.max_delay = max_delay or self.DEFAULT_MAX_DELAY
        
        logger.info("✓ Cliente HTTP listo (delay: %.1f-%.1f segundos)", self.min_delay, self.max_delay)

    def _request_profile_json(self, username: str) -> dict:
        """
        Realiza la request HTTP al endpoint interno de Instagram que devuelve JSON del perfil.
        
        IMPORTANTE: Usa el endpoint móvil (i.instagram.com) que devuelve datos completos
        incluyendo timeline, a diferencia de www.instagram.com que tiene restricciones.
        
        Maneja errores comunes: login_required, rate limiting, respuestas inválidas.
        """

        # ENDPOINT CRÍTICO: i.instagram.com devuelve timeline completa
        # www.instagram.com es limitado y suele devolver edges vacío
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"

        logger.info("Requesting: %s", url)

        # Delay previo para simular interacción humana
        human_delay(self.min_delay / 2.0, self.max_delay / 2.0)

        try:
            response = self.client.get(url)
        except Exception as error:
            logger.exception("Error durante la request HTTP")
            raise RuntimeError(f"http_request_failed: {error}") from error

        # Manejo de rate limiting
        if response.status_code == 429:
            logger.error("Rate limited by Instagram (429)")
            raise RuntimeError("rate_limited")

        # Manejo de autenticación fallida
        if response.status_code == 401:
            logger.error("Unauthorized (401) - sesión inválida o expirada")
            raise RuntimeError("unauthorized")

        if response.status_code != 200:
            logger.error("Unexpected status: %d", response.status_code)
            logger.debug("Response body: %s", response.text[:500])
            raise RuntimeError(f"unexpected_status_{response.status_code}")

        # Parseamos JSON
        try:
            data = response.json()
        except Exception as error:
            logger.exception("Invalid JSON response")
            logger.debug("Response text: %s", response.text[:1000])
            raise ValueError("invalid_json") from error

        if not data:
            logger.warning("Empty JSON response")
            raise ValueError("empty_json")

        # Comprobación de sesión inválida
        if isinstance(data, dict) and data.get("message") == "login_required":
            logger.error("Session invalid: Instagram says login_required")
            raise RuntimeError("login_required")

        # Log de estructura JSON para debugging (si no hay status de error)
        if isinstance(data, dict):
            logger.debug("JSON structure: keys=%s", list(data.keys()))
            if "data" in data and isinstance(data["data"], dict):
                logger.debug("data keys: %s", list(data["data"].keys()))

        return data

    def _parse_node(self, node: dict, owner_username: str) -> Post:
        """Convierte un nodo JSON de Instagram en un objeto `Post`
        
        Extrae campos críticos de forma segura, manejando variaciones en la estructura JSON.
        """

        caption = ""
        try:
            caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
            if caption_edges:
                caption = caption_edges[0].get("node", {}).get("text", "")
            if not caption:
                caption = node.get("caption", "")
        except Exception:
            caption = ""

        hashtags = re.findall(r"#(\w+)", caption or "")
        mentions = re.findall(r"@(\w+)", caption or "")

        ts = node.get("taken_at_timestamp")
        if ts:
            try:
                date_utc = datetime.utcfromtimestamp(int(ts)).isoformat()
            except Exception:
                date_utc = str(ts)
        else:
            date_utc = ""

        shortcode = node.get("shortcode", "")
        post_id = node.get("id", "")
        permalink = f"https://www.instagram.com/p/{shortcode}/"
        typename = node.get("__typename", node.get("typename", ""))
        is_video = bool(node.get("is_video", False))
        likes = node.get("edge_liked_by", {}).get("count", 0) or node.get("like_count", 0) or 0
        comments = node.get("edge_media_to_comment", {}).get("count", 0) or node.get("comments", 0) or 0
        url = node.get("display_url") or node.get("display_src") or ""

        location = None
        try:
            if node.get("location") and isinstance(node.get("location"), dict):
                location = node.get("location", {}).get("name")
        except Exception:
            location = None

        tagged_users = []
        try:
            for tag in node.get("edge_media_to_tagged_user", {}).get("edges", []):
                user = tag.get("node", {}).get("user", {})
                if user.get("username"):
                    tagged_users.append(user.get("username"))
        except Exception:
            tagged_users = []

        owner = owner_username or node.get("owner", {}).get("username", "")

        return Post(
            shortcode=shortcode,
            post_id=str(post_id),
            permalink=permalink,
            date_utc=date_utc,
            caption=caption,
            hashtags=hashtags,
            mentions=mentions,
            typename=typename,
            is_video=is_video,
            likes=int(likes),
            comments=int(comments),
            url=url,
            location=location,
            tagged_users=tagged_users,
            owner_username=owner,
        )

    def get_latest_posts(self, username: str, limit: int) -> List[Post]:
        """
        Implementación del contrato: obtiene las últimas `limit` publicaciones
        de `username` usando requests HTTP y mapea a `Post`.
        
        Valida que el JSON contenga timeline_media y extrae posts correctamente.
        Si edges está vacío, loga advertencia y datos de debugging.
        """

        logger.info("========================================")
        logger.info("Iniciando scraping para username: %s", username)
        logger.info("Límite de posts: %d", limit)
        logger.info("========================================")

        # Request al endpoint
        data = self._request_profile_json(username)

        # Extrae el objeto user del JSON
        user = data.get("data", {}).get("user") or data.get("user")
        if not user:
            logger.error("No user object found in JSON response")
            logger.debug("Full JSON keys: %s", list(data.keys()))
            raise ValueError("user_not_found_in_json")

        owner_username = user.get("username", username)
        logger.info("Usuario encontrado: %s", owner_username)

        # Intenta extraer timeline
        timeline = user.get("edge_owner_to_timeline_media", {})
        
        if not timeline:
            logger.warning("No timeline found. Checking alternative fields...")
            logger.debug("User keys available: %s", list(user.keys())[:10])
            timeline = {}

        edges = timeline.get("edges", [])
        
        logger.info("Timeline edges found: %d", len(edges))

        if not edges:
            logger.warning("⚠️ EMPTY EDGES - No posts in timeline")
            logger.warning("This could mean:")
            logger.warning("  - Account is private or restricted")
            logger.warning("  - Session cookies are invalid or expired")
            logger.warning("  - Instagram is rate-limiting this session")
            logger.warning("  - Account has no public posts")
            logger.debug("Full user object keys: %s", list(user.keys()))
            logger.debug("Timeline object: %s", str(timeline)[:500])

        posts: List[Post] = []

        # Itera por las aristas y mapea cada nodo
        for index, edge in enumerate(edges[:limit], start=1):
            node = edge.get("node", edge)

            try:
                post = self._parse_node(node, owner_username)
                posts.append(post)
                logger.info("[%d/%d] ✓ Procesado: %s (likes: %d, comments: %d)", 
                           index, min(limit, len(edges)), post.shortcode, post.likes, post.comments)
            except Exception as error:
                logger.exception("Error parsing node %d: %s", index, error)
                continue

            # Delay entre procesamiento
            if index < min(limit, len(edges)):
                delay_time = human_delay(self.min_delay, self.max_delay)
                logger.debug("Applied delay: %.2f seconds", delay_time)

        logger.info("========================================")
        logger.info("Scraping completado: %d posts extraídos", len(posts))
        logger.info("========================================")

        return posts
