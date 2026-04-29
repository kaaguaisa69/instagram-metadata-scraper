import sys
import logging

from app.post_service import PostService
from infrastructure.config import get_instagram_username
# from infrastructure.instagram_scraper import InstagramScraper
from infrastructure.instagram_http_scraper import InstagramHttpScraper
from infrastructure.json_repository import JsonPostRepository


# Configurar logging a nivel INFO para ver todos los mensajes del scraper
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s | %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Función principal que orquesta el flujo de trabajo del scraper HTTP.
    
    Flujo:
    1. Configuración: Carga credenciales desde .env
    2. Inicialización: Crea scraper (httpx + cookies) y repositorio (JSON)
    3. Ejecución: PostService orquesta extracción y guardado
    4. Validación: Verifica que se obtuvieron posts
    
    NOTAS TÉCNICAS:
    - Usa endpoint móvil: https://i.instagram.com/api/v1/users/web_profile_info/
    - No usa Selenium, BeautifulSoup ni APIs oficiales
    - Simula navegador móvil iPhone con headers realistas
    - Incluye delays aleatorios para evitar rate limiting
    """

    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║   Instagram Metadata Scraper (HTTP + Cookies)             ║")
    logger.info("║   Endpoint: https://i.instagram.com/api/v1/users/web...   ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")

    # --- PASO 1: CONFIGURACION ---
    try:
        login_username = get_instagram_username()
    except ValueError as e:
        logger.error("✗ Error de configuración: %s", e)
        sys.exit(1)

    target_username = login_username
    limit = 10
    output_file = "output/latest_posts.json"

    logger.info("Configuración:")
    logger.info("  • Usuario autenticado: %s", login_username)
    logger.info("  • Perfil objetivo: %s", target_username)
    logger.info("  • Posts a obtener: %d", limit)
    logger.info("  • Archivo de salida: %s", output_file)
    logger.info("")

    # --- PASO 2: INICIALIZACION ---
    try:
        # scraper = InstagramScraper(login_username)
        scraper = InstagramHttpScraper()
        repository = JsonPostRepository()
        service = PostService(scraper, repository)
        logger.info("✓ Componentes inicializados correctamente")
        logger.info("")
    except Exception as e:
        logger.error("✗ Error al inicializar componentes: %s", e)
        sys.exit(1)

    # --- PASO 3: EJECUCION ---
    try:
        logger.info("Iniciando extracción de datos...")
        logger.info("")
        
        posts = service.extract_and_save_posts(
            profile_username=target_username,
            limit=limit,
            file_path=output_file,
        )
        
        logger.info("")
    except RuntimeError as e:
        logger.error("✗ Error de ejecución: %s", e)
        if "login_required" in str(e):
            logger.error("  Causa probable: Cookies expiradas o inválidas")
            logger.error("  Solución: Revisa las cookies en tu navegador y actualiza .env")
        elif "rate_limited" in str(e):
            logger.error("  Causa probable: Instagram está rate-limiting esta sesión")
            logger.error("  Solución: Espera unos minutos e intenta nuevamente")
        sys.exit(1)
    except ValueError as e:
        logger.error("✗ Error de validación: %s", e)
        if "user_not_found" in str(e):
            logger.error("  El usuario no existe o no es accesible")
        elif "empty_json" in str(e):
            logger.error("  La respuesta JSON está vacía")
        sys.exit(1)
    except Exception as e:
        logger.error("✗ Error inesperado: %s", e)
        sys.exit(1)

    # --- PASO 4: VALIDACION ---
    logger.info("╔════════════════════════════════════════════════════════════╗")
    if len(posts) > 0:
        logger.info("║  ✓ Proceso completado exitosamente                      ║")
    else:
        logger.warning("║  ⚠ Proceso completado sin posts (ver logs arriba)      ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    
    logger.info("")
    logger.info("Resultados:")
    logger.info("  • Posts extraídos: %d", len(posts))
    logger.info("  • Archivo guardado: %s", output_file)
    logger.info("")

    if len(posts) == 0:
        logger.warning("ADVERTENCIA: No se extrajeron posts")
        logger.warning("Revisa:")
        logger.warning("  1. Que las cookies en .env sean válidas")
        logger.warning("  2. Que la cuenta sea pública")
        logger.warning("  3. Los logs anteriores para más detalles")


if __name__ == "__main__":
    try:
        main()

    except FileNotFoundError as error:
        logger.error("✗ ERROR: Archivo no encontrado: %s", error)
        sys.exit(1)

    except ValueError as error:
        logger.error("✗ ERROR DE CONFIGURACIÓN: %s", error)
        sys.exit(1)

    except RuntimeError as error:
        logger.error("✗ ERROR DE EJECUCIÓN: %s", error)
        sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("⚠ Proceso interrumpido por el usuario (Ctrl+C)")
        sys.exit(0)

    except Exception as error:
        logger.error("✗ ERROR INESPERADO: %s", error)
        logger.error("Por favor, abre un issue con los logs anteriores")
        sys.exit(1)