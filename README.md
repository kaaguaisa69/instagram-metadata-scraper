# Instagram Metadata Scraper

## 1. Descripción del proyecto

Instagram Metadata Scraper es una solución en Python para extraer la metadata de las publicaciones más recientes de una cuenta de Instagram y guardarla en formato JSON.

El proyecto extrae hasta 15 campos clave para el análisis de contenido, entre ellos:

- `shortcode`, `post_id`, `permalink`, `url`
- `typename` (tipo de publicación: imagen, video, carrusel)
- `date_utc` (fecha de publicación)
- `caption` (texto)
- `hashtags` y `mentions`
- `likes` y `comments`
- `is_video`
- `location` y `tagged_users`

Debido a las estrictas políticas anti-scraping de Instagram en 2025/2026, **el proyecto ha migrado de una autenticación tradicional (usuario/contraseña) a una autenticación basada en cookies de navegador**. Esto reduce significativamente el riesgo de bloqueos y evita problemas con la autenticación en dos pasos (2FA).

## 2. Arquitectura del proyecto y Principios SOLID

El proyecto está organizado con una arquitectura por capas para separar responsabilidades, facilitar el mantenimiento y cumplir con las mejores prácticas de la ingeniería de software:

- `domain`: Modelos de datos (`Post`) y contratos o interfaces (`PostScraper`, `PostRepository`).
- `app`: Contiene la lógica orquestadora (`PostService`).
- `infrastructure`: Implementaciones concretas (`InstagramScraper`, `JsonPostRepository`, `config.py`).
- `main.py`: Punto de entrada que ensambla las dependencias.
- `setup_session.py`: Script independiente para gestionar la importación de la sesión.

### Principios Aplicados:

- **SRP (Responsabilidad Única):** Cada clase tiene un único propósito. Por ejemplo, `JsonPostRepository` solo sabe cómo guardar archivos, no sabe cómo hacer scraping.
- **OCP (Abierto/Cerrado):** El sistema permite agregar nuevas formas de guardar datos (ej. un `CsvRepository` para Excel) sin modificar la lógica principal de `PostService`.
- **DIP (Inversión de Dependencias):** `PostService` depende de las interfaces (contratos) definidos en `domain`, no de las implementaciones directas de `infrastructure`.
- **Manejo de Errores Silencioso:** Se implementaron bloques `try-except` granulares. Si Instagram bloquea la extracción de un dato específico (como la ubicación geográfica), el scraper no falla; simplemente marca ese campo como nulo y continúa extrayendo el resto de la metadata de la publicación.

## 3. Tecnologías utilizadas

- **Python:** lenguaje principal para la implementación del flujo de extracción y procesamiento.
- **Instaloader:** librería usada para scraping de publicaciones y metadata de Instagram.
- **python-dotenv:** carga de variables de entorno desde `.env` para no hardcodear credenciales.
- **JSON:** formato de salida para persistir metadata de forma portable y fácil de consumir.
- **Virtual Environment (`.venv`):** aislamiento de dependencias para evitar conflictos entre proyectos.

## 4. Flujo del sistema

El flujo de ejecución actual es:

1. Se leen credenciales desde variables de entorno (`.env`).
2. Se instancia el scraper concreto (`InstagramScraper`).
3. Se solicitan las últimas publicaciones del perfil objetivo (límite: 10).
4. Cada publicación se transforma al modelo interno `Post`.
5. Se persiste el resultado en JSON mediante `JsonPostRepository`.
6. Se muestra un resumen en consola con total de publicaciones y archivo generado.

## 5. Problemas encontrados y resolución

Esta sección resume incidencias reales observadas durante la implementación y ejecución.

### 5.1 Error en PowerShell al crear estructura (`mkdir` y `type nul`)

- **Qué ocurrió:** comandos de creación de carpetas/archivos ejecutados con sintaxis no compatible según shell o contexto.
- **Causa:** diferencias entre CMD y PowerShell para redirecciones y creación rápida de archivos.
- **Mitigación:** usar comandos equivalentes en PowerShell (`New-Item -ItemType Directory/File`) o una sintaxis consistente por terminal.

### 5.2 Python no reconocido en sistema

- **Qué ocurrió:** el comando `python` no era reconocido inicialmente.
- **Causa:** Python no instalado correctamente o no agregado al `PATH`.
- **Mitigación:** instalar Python desde fuente oficial y marcar la opción para añadir al `PATH`, luego reiniciar terminal.

### 5.3 Entorno virtual no activado

- **Qué ocurrió:** dependencias instaladas fuera del entorno esperado o no disponibles.
- **Causa:** ejecución de comandos sin activar `.venv`.
- **Mitigación:** activar entorno antes de instalar/ejecutar (`.venv\Scripts\Activate.ps1` en PowerShell).

### 5.4 Módulo `dotenv` no encontrado

- **Qué ocurrió:** error `ModuleNotFoundError` al importar `dotenv`.
- **Causa:** paquete `python-dotenv` no instalado en el entorno activo.
- **Mitigación:** instalar dependencias desde `requirements.txt` con el entorno virtual activo.

### 5.5 Problemas con autenticación 2FA

- **Qué ocurrió:** Instagram solicitó autenticación de dos factores al hacer login.
- **Causa:** política de seguridad de la cuenta.
- **Mitigación:** se implementó flujo de ingreso manual del código 2FA y guardado de sesión reutilizable.

### 5.6 Códigos 2FA inválidos o expirados

- **Qué ocurrió:** códigos rechazados durante el proceso de login.
- **Causa:** ventanas de tiempo cortas en TOTP o desfase de hora del dispositivo.
- **Mitigación:** reintentar con código recién generado, validar hora del sistema y mejorar mensaje de error al usuario.

### 5.7 Uso de `@` en username

- **Qué ocurrió:** fallos al resolver perfil cuando el usuario se ingresaba con prefijo `@`.
- **Causa:** Instaloader espera username sin `@`.
- **Mitigación:** estandarizar entrada sin `@` (o normalizar eliminándolo antes de consulta).

### 5.8 `ProfileNotExistsException` aunque el perfil sí existía

- **Qué ocurrió:** excepción de perfil inexistente en cuentas reales.
- **Causa:** inconsistencias por sesión inválida, bloqueos temporales o restricciones de consulta.
- **Mitigación:** reutilizar sesión válida, forzar nuevo login cuando la sesión falle y reducir frecuencia de intentos.

### 5.9 Bloqueo de Instagram: "Please wait a few minutes before you try again"

- **Qué ocurrió:** bloqueo temporal por actividad detectada como automatizada.
- **Causa:** mecanismos anti-bot/rate limiting de Instagram.
- **Mitigación:** espaciar ejecuciones, reutilizar sesión, evitar intentos repetitivos y considerar migración a API oficial.

### 5.10 Restricción de endpoints GraphQL de Instagram

- **Qué ocurrió:** respuestas inconsistentes o bloqueos al consumir rutas no oficiales usadas por scraping.
- **Causa:** cambios no documentados y controles internos de plataforma.
- **Mitigación:** aceptar la limitación del enfoque, desacoplar arquitectura y preparar reemplazo por integración oficial.

### 5.11 Inestabilidad del scraping con herramientas no oficiales

- **Qué ocurrió:** comportamiento variable entre ejecuciones (autenticación, disponibilidad, consistencia).
- **Causa:** dependencia de mecanismos no soportados oficialmente por Meta.
- **Mitigación:** diseño por capas para facilitar migración y reducción del acoplamiento al scraper actual.

## 6. Limitaciones del enfoque con scraping

El scraping presenta limitaciones técnicas importantes:

- Instagram puede bloquear accesos automatizados sin previo aviso.
- Los endpoints utilizados no son oficiales ni estables.
- Existen límites de frecuencia (rate limiting) y validaciones anti-abuso.
- No es una estrategia confiable para entornos de producción con requerimientos de alta disponibilidad.

## 7. Decisión técnica final

Debido a las limitaciones anteriores, la recomendación técnica es migrar hacia la **Instagram Graph API oficial** para cuentas **Business/Creator**.

Razones:

- mayor estabilidad operativa;
- soporte oficial por Meta;
- menor probabilidad de bloqueos por automatización;
- mejor proyección para producción, auditoría y mantenimiento.

## 8. Cómo ejecutar el proyecto

### 8.1 Prerrequisitos

- Python 3.10+ instalado.
- PowerShell o terminal compatible.

### 8.2 Crear y activar entorno virtual

1. Crea el entorno virtual:
   ```powershell
   python -m venv .venv
   ```

2. Activa el entorno virtual:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Instala las dependencias:
   ```powershell
   pip install -r requirements.txt
   ```

### 8.3 Configurar las variables de entorno

Crea un archivo llamado `.env` en la raíz del proyecto (junto a `main.py`). Añade lo siguiente:

```env
INSTAGRAM_USERNAME=tu_usuario_sin_arroba
INSTAGRAM_BROWSER=firefox
```

_(Puedes cambiar `firefox` por `chrome`, `brave`, `edge` u `opera` dependiendo del navegador que vayas a usar)._

### 8.4 Iniciar Sesión Manualmente en el Navegador

1. Abre el navegador web que pusiste en el `.env` (ej. Firefox).
2. Entra a [https://www.instagram.com](https://www.instagram.com).
3. **Inicia sesión** con tu cuenta.
4. Si te pregunta "¿Guardar información de inicio de sesión?", haz clic en **Guardar/Aceptar** (esto es crucial para generar la cookie persistente).
5. Navega un par de segundos viendo fotos.
6. **CIERRA EL NAVEGADOR POR COMPLETO.** (No debe quedar abierto ni en segundo plano).

### 8.5 Importar la Sesión al Proyecto

Con el navegador cerrado y el entorno virtual activado, ejecuta:

```powershell
python setup_session.py
```

Este script leerá tu navegador, extraerá la cookie de sesión y creará un archivo local (`session-tuusuario`). Verás mensajes de "OK" validando la sesión.

---

## 9. Ejecución del Scraper

Una vez que el archivo de sesión ha sido generado con éxito, simplemente ejecuta:

```powershell
python main.py
```

El script cargará la sesión almacenada, buscará las últimas 10 publicaciones, procesará los 15 campos de metadata (imprimiendo un resumen limpio en la consola) y guardará el resultado final en `output/latest_posts.json`.

---

## 10. Resolución de Problemas Frecuentes

- **Error: "Navegador bloqueado o base de datos en uso" al ejecutar `setup_session.py`**
  El navegador sigue abierto. Ciérralo completamente desde el Administrador de Tareas.
- **Error: "La sesión cargada no es válida" o "Login required"**
  Instagram invalidó tu sesión o la cookie expiró. Abre tu navegador, entra a Instagram, cierra sesión, vuelve a iniciar sesión (marcando "Recordar cuenta"), cierra el navegador y vuelve a ejecutar `python setup_session.py`.
- **Mensaje en consola: "Error al procesar ubicación (201 Created)"**
  Instagram a menudo bloquea las peticiones de geolocalización a los scrapers. El script está diseñado para interceptar este error, dejar la ubicación vacía y continuar guardando los likes, comentarios, etc., sin detener la ejecución.

---

## 11. Ejemplo de Estructura de Salida (JSON)

El archivo generado en `output/latest_posts.json` se verá así:

```json
[
  {
    "shortcode": "BzKHTrlF_jS",
    "post_id": "1234567890123456789",
    "permalink": "https://www.instagram.com/p/BzKHTrlF_jS/",
    "date_utc": "2026-04-22T15:42:10+00:00",
    "caption": "Ejemplo de publicación #python",
    "hashtags": ["python", "data"],
    "mentions": [],
    "typename": "GraphImage",
    "is_video": false,
    "likes": 230,
    "comments": 18,
    "url": "https://instagram.example/cdn/post.jpg",
    "location": null,
    "tagged_users": [],
    "owner_username": "cuenta_objetivo"
  }
]
```
