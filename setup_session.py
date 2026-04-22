"""
Script de configuracion de sesion MEJORADO.
"""

import sys
import os
import instaloader
from dotenv import load_dotenv

load_dotenv()

def main() -> None:
    username = os.getenv("INSTAGRAM_USERNAME", "").strip()
    browser_name = os.getenv("INSTAGRAM_BROWSER", "firefox").lower()

    if not username:
        print("ERROR: Define INSTAGRAM_USERNAME en el .env")
        sys.exit(1)

    session_file = f"session-{username}"

    print("=" * 60)
    print(f"  Configurando sesion para: {username}")
    print(f"  Usando navegador: {browser_name}")
    print("=" * 60)

    try:
        import browser_cookie3
    except ImportError:
        print("ERROR: Ejecuta 'pip install browser-cookie3'")
        sys.exit(1)

    # Selección de navegador (Agregado Brave que es compatible con Chrome)
    browsers = {
        "firefox": browser_cookie3.firefox,
        "chrome": browser_cookie3.chrome,
        "brave": browser_cookie3.chrome, # Brave usa la misma estructura que Chrome
        "edge": browser_cookie3.edge,
        "opera": browser_cookie3.opera,
    }

    if browser_name not in browsers:
        print(f"ERROR: Navegador '{browser_name}' no soportado.")
        sys.exit(1)

    print(f"\n[1/3] Extrayendo cookies de {browser_name}...")
    try:
        # Intentamos obtener las cookies
        if browser_name == "brave":
            # Brave a veces requiere especificar la ruta o se comporta como chrome
            cj = browser_cookie3.chrome(domain_name=".instagram.com")
        else:
            cj = browsers[browser_name](domain_name=".instagram.com")
    except Exception as e:
        print(f"ERROR: No se pudo leer el navegador {browser_name}. Esta cerrado?")
        print(f"Detalle: {e}")
        sys.exit(1)

    loader = instaloader.Instaloader()
    
    # Inyectar cookies y listar cuáles encontramos para depurar
    found_cookies = []
    for cookie in cj:
        loader.context._session.cookies.set_cookie(cookie)
        found_cookies.append(cookie.name)
    
    print(f"  Cookies encontradas: {', '.join(found_cookies)}")
    
    if 'sessionid' not in found_cookies:
        print("\nADVERTENCIA: No se encontro la cookie 'sessionid'.")
        print("Esto significa que no estas logueado realmente en el navegador o")
        print("que el navegador no ha guardado la sesion en el disco.")
        print("\nSOLUCION:")
        print("1. Abre tu navegador y ve a Instagram.")
        print("2. Asegurate de marcar 'Recordar informacion de inicio de sesion'.")
        print("3. Navega un poco, cierra la pestaña y LUEGO cierra el navegador completo.")

    print("\n[2/3] Verificando sesion con Instagram...")
    try:
        # Forzamos el username en el contexto antes de probar
        loader.context.username = username
        test_user = loader.test_login()
        if test_user:
            print(f"  Sesion confirmada para: {test_user}")
        else:
            print("  La sesion no es valida (test_login devolvio None)")
            sys.exit(1)
    except Exception as e:
        print(f"  Error de conexion/validacion: {e}")
        sys.exit(1)

    print("\n[3/3] Guardando sesion localmente...")
    try:
        # Aseguramos que el contexto sepa quién es el usuario antes de guardar
        loader.save_session_to_file(session_file)
        print(f"  EXITO! Archivo '{session_file}' creado.")
        print("\nYa puedes ejecutar: python main.py")
    except Exception as e:
        print(f"  ERROR al guardar: {e}")
        print("\nTip: Intenta abrir Instagram en el navegador, cerrar sesion y")
        print("volver a entrar asegurandote de que no sea una ventana privada.")

if __name__ == "__main__":
    main()
