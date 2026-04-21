from app.post_service import PostService
from infrastructure.config import get_instagram_credentials
from infrastructure.instagram_scraper import InstagramScraper
from infrastructure.json_repository import JsonPostRepository


def main() -> None:
    """
    Punto de entrada principal del programa.

    Flujo general:
    1. obtiene credenciales desde el archivo .env
    2. define el usuario objetivo a consultar
    3. define cuántas publicaciones traer
    4. define dónde se guardará el resultado
    5. crea las dependencias del sistema
    6. ejecuta el caso de uso principal
    7. muestra un resumen en consola
    """

    # Obtiene las credenciales de Instagram desde la configuración.
    # Retorna una tupla con:
    # - login_username = usuario que iniciará sesión
    # - login_password = contraseña del usuario que iniciará sesión
    login_username, login_password = get_instagram_credentials()

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

    # Crea la instancia concreta del scraper.
    # Esta clase sabe iniciar sesión en Instagram y obtener publicaciones.
    scraper = InstagramScraper(login_username, login_password)

    # Crea la instancia concreta del repositorio.
    # Esta clase sabe guardar la información en un archivo JSON.
    repository = JsonPostRepository()

    # Crea el servicio principal del sistema.
    # Este servicio coordina el proceso de extracción y guardado.
    service = PostService(scraper, repository)

    # Ejecuta el caso de uso principal:
    # - obtiene publicaciones
    # - las guarda en JSON
    # - retorna la lista procesada
    posts = service.extract_and_save_posts(
        profile_username=target_username,
        limit=limit,
        file_path=output_file,
    )

    # Muestra un mensaje final de confirmación.
    print("Proceso completado correctamente.")
    print(f"Se extrajeron {len(posts)} publicaciones.")
    print(f"Archivo generado: {output_file}")


if __name__ == "__main__":
    # Esta condición asegura que main() solo se ejecute
    # cuando este archivo se corre directamente.
    # Si el archivo se importa desde otro módulo, no se ejecutará automáticamente.
    main()