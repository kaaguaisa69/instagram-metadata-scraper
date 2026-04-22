import sys

from app.post_service import PostService
from infrastructure.config import get_instagram_username
from infrastructure.instagram_scraper import InstagramScraper
from infrastructure.json_repository import JsonPostRepository


def main() -> None:
    """
    Funcion principal que orquesta el flujo de trabajo del scraper.
    
    El flujo sigue estos pasos logicamente separados:
    1. Configuracion: Carga de credenciales y definicion de rutas.
    2. Inicializacion: Creacion de los componentes (Scraper y Repositorio).
    3. Ejecucion: El servicio coordina la extraccion y el guardado.
    4. Cierre: Notificacion al usuario de los resultados.
    """

    # --- PASO 1: CONFIGURACION ---
    # Obtenemos el nombre de usuario desde el archivo .env para seguridad.
    login_username = get_instagram_username()

    # Define el perfil objetivo que se quiere consultar.
    # En esta primera versión se usa el mismo usuario autenticado.
    # Más adelante podrías cambiar esto por otro username si lo necesitas.
    target_username = login_username

    # Define el número máximo de publicaciones recientes a obtener.
    # En este proyecto nos pidieron trabajar con las 10 más recientes.
    limit = 10
    
    # Define la ruta del archivo de salida.
    # El resultado final se guardará en formato JSON dentro de la carpeta output.
    output_file = "output/latest_posts.json"

    # Definimos la ruta de salida. Usamos CSV para que sea facil de abrir en Excel.
    output_file = "output/metadata_instagram.csv"

    # Muestra encabezado con la configuración actual.
    print("=" * 60)
    print("  Instagram Metadata Scraper")
    print("=" * 60)
    print(f"  Usuario autenticado : {login_username}")
    print(f"  Perfil objetivo     : {target_username}")
    print(f"  Publicaciones       : {limit}")
    print(f"  Archivo de salida   : {output_file}")
    print("=" * 60)
    print()

    # --- PASO 2: INICIALIZACION DE COMPONENTES ---
    # El Scraper se encarga de la comunicacion con Instagram usando la sesion guardada.
    scraper = InstagramScraper(login_username)

    # Crea la instancia concreta del repositorio.
    # Esta clase sabe guardar la información en un archivo JSON.
    repository = JsonPostRepository()

    # Crea el servicio principal del sistema.
    # Este servicio coordina el proceso de extracción y guardado.
    service = PostService(scraper, repository)

    # Ejecuta el caso de uso principal:
    # - carga sesión desde cookies
    # - obtiene publicaciones
    # - las guarda en JSON
    # - retorna la lista procesada
    posts = service.extract_and_save_posts(
        profile_username=target_username,
        limit=limit,
        file_path=output_file,
    )

    # Muestra un resumen final de confirmación.
    print()
    print("=" * 60)
    print("  Proceso completado correctamente")
    print("=" * 60)
    print(f"  Publicaciones extraídas : {len(posts)}")
    print(f"  Archivo generado        : {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    # Esta condición asegura que main() solo se ejecute
    # cuando este archivo se corre directamente.
    # Si el archivo se importa desde otro módulo, no se ejecutará automáticamente.
    try:
        main()

    except FileNotFoundError as error:
        # Error cuando no existe el archivo de sesión.
        print()
        print(f"ERROR DE SESIÓN: {error}")
        sys.exit(1)

    except ValueError as error:
        # Error de configuración o perfil no encontrado.
        print()
        print(f"ERROR DE CONFIGURACIÓN: {error}")
        sys.exit(1)

    except RuntimeError as error:
        # Error durante la ejecución del scraper.
        print()
        print(f"ERROR DE EJECUCIÓN: {error}")
        sys.exit(1)

    except KeyboardInterrupt:
        # El usuario interrumpió el proceso con Ctrl+C.
        print()
        print("Proceso interrumpido por el usuario.")
        sys.exit(0)

    except Exception as error:
        # Cualquier otro error no previsto.
        print()
        print(f"ERROR INESPERADO: {error}")
        print(
            "Si el problema persiste, revisa la configuración "
            "y vuelve a ejecutar: python setup_session.py"
        )
        sys.exit(1)