# Instagram Metadata Scraper - HTTP + Cookies (Refactor 2026)

## Descripción del Proyecto

Scraper en **Python puro** que extrae metadata de las últimas 10 publicaciones de una cuenta pública de Instagram mediante:

-- **Requests HTTP directos** (sin Selenium, BeautifulSoup ni APIs oficiales)
- **Cookies reales de sesión** (obtenidas del navegador)
- **Headers realistas** que simulan cliente móvil Instagram
- **Delays aleatorios** para evitar rate limiting
- **Arquitectura limpia por capas** con principios SOLID

### Metadata Extraída

Por cada post se obtiene:
- `shortcode`, `post_id`, `permalink`, `url`
- `caption`, `hashtags`, `mentions`
- `date_utc`, `likes`, `comments`
- `typename` (imagen, video, carrusel)
- `is_video`, `location`, `tagged_users`, `owner_username`

## Arquitectura

**Estructura por capas** (SOLID compliant):

```
project/
├── domain/                          # Contratos (interfaces)
│   ├── contracts.py                # PostScraper, PostRepository (ABC)
│   └── post.py                     # Modelo Post (dataclass)
├── app/                            # Lógica de aplicación
│   └── post_service.py             # Orquestador PostService
├── infrastructure/                 # Implementaciones concretas
│   ├── instagram_http_scraper.py   # Scraper con httpx
│   ├── cookie_manager.py           # Carga cookies desde .env
│   ├── headers.py                  # Headers realistas (iPhone)
│   ├── delay_manager.py            # Delays aleatorios
│   ├── config.py                   # Validación de configuración
│   ├── json_repository.py          # Guardado en JSON
│   └── __init__.py
├── main.py                         # Punto de entrada
├── requirements.txt                # Dependencias
├── .env.example                    # Plantilla de variables
└── REFACTOR.md                     # Documentación técnica del refactor
```

### Principios SOLID Aplicados

| Principio | Aplicación |
|-----------|-----------|
| **SRP** | Cada módulo tiene responsabilidad única: `cookie_manager` carga cookies, `headers` construye headers, etc. |
| **OCP** | Se pueden agregar nuevos `PostScraper` o `PostRepository` sin modificar `PostService` |
| **LSP** | `InstagramHttpScraper` implementa correctamente el contrato `PostScraper` |
| **ISP** | Contratos mínimos e independientes (`PostScraper`, `PostRepository`) |
| **DIP** | `PostService` depende de abstracciones (`ABC`), no de implementaciones |

## Tecnologías

- **Python 3.7+**
- **httpx** - Requests HTTP con soporte async
- **python-dotenv** - Carga de variables de entorno
- **JSON** - Formato de salida

## Configuración Rápida

### 1. Clonar / Descargar Proyecto

```bash
cd instagram-metadata-scraper
```

### 2. Crear Entorno Virtual

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
# o
source .venv/bin/activate  # Linux/Mac
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Obtener Cookies de Sesión

**En tu navegador:**

1. Abre https://www.instagram.com e inicia sesión
2. Abre DevTools (F12)
3. Ve a **Application** → **Cookies** → **www.instagram.com**
4. Busca y copia los valores de:
   - `sessionid`
   - `csrftoken`
   - `ds_user_id`

### 5. Configurar Variables de Entorno

Crea `.env` en la raíz del proyecto:

```bash
# Copiar desde plantilla
cp .env.example .env

# Editar con tus valores
INSTAGRAM_USERNAME=tu_usuario
INSTAGRAM_SESSIONID=abc123def456...
INSTAGRAM_CSRFTOKEN=xyz789...
INSTAGRAM_DS_USER_ID=123456789
```

### 6. Ejecutar Scraper

```bash
python main.py
```

**Salida esperada:**

```
INFO | ╔════════════════════════════════════════════════════════════╗
INFO | ║   Instagram Metadata Scraper (HTTP + Cookies)             ║
INFO | ║   Endpoint: https://i.instagram.com/api/v1/users/web...   ║
INFO | ╚════════════════════════════════════════════════════════════╝
INFO |
INFO | Configuración:
INFO |   • Usuario autenticado: tu_usuario
INFO |   • Perfil objetivo: tu_usuario
INFO |   • Posts a obtener: 10
INFO |   • Archivo de salida: output/latest_posts.json
INFO |
INFO | ✓ Componentes inicializados correctamente
INFO | ✓ Cookies cargadas desde .env
INFO | ✓ Cliente HTTP listo (delay: 1.0-3.0 segundos)
INFO |
INFO | [1/10] ✓ Procesado: shortcode_123 (likes: 250, comments: 15)
INFO | [2/10] ✓ Procesado: shortcode_456 (likes: 1200, comments: 87)
...
INFO |
INFO | ╔════════════════════════════════════════════════════════════╗
INFO | ║  ✓ Proceso completado exitosamente                      ║
INFO | ╚════════════════════════════════════════════════════════════╝
INFO |
INFO | Resultados:
INFO |   • Posts extraídos: 10
INFO |   • Archivo guardado: output/latest_posts.json
```

**Resultado en `output/latest_posts.json`:**

```json
[
  {
    "shortcode": "ABC123XYZ",
    "post_id": "1234567890",
    "permalink": "https://www.instagram.com/p/ABC123XYZ/",
    "date_utc": "2026-04-29T15:30:45",
    "caption": "Hello world! #instagram #scraping",
    "hashtags": ["instagram", "scraping"],
    "mentions": [],
    "typename": "GraphImage",
    "is_video": false,
    "likes": 250,
    "comments": 15,
    "url": "https://instagram.com/...jpg",
    "location": null,
    "tagged_users": [],
    "owner_username": "tu_usuario"
  },
  ...
]
```

## Seguridad y Privacidad

- **Sin almacenar credenciales:** Solo se guardan cookies en `.env` (archivo local, no versionado)
- **Sin login automático:** Se usan cookies existentes del navegador
- **Sin datos confidenciales:** Solo se extraen datos públicos (posts, likes, etc.)
- **Respeta rate limiting:** Detecta error 429 y detiene proceso

## Manejo de Errores

### Si no se extraen posts:

**Causa:** ` EMPTY EDGES - No posts in timeline`

**Soluciones:**

1. **Cookies expiradas**
   - Abre Instagram en tu navegador
   - Copia las cookies nuevamente
   - Actualiza `.env`

2. **Sesión no válida**
   - Inicia sesión nuevamente en Instagram
   - Asegúrate que las cookies sean recientes (hoy)

3. **Cuenta privada**
   - El endpoint solo devuelve posts públicos
   - Verifica que tu cuenta sea pública

4. **Rate limited**
   - Instagram limitó la sesión
   - Espera 1-2 horas
   - Reintenta con cookies actualizadas

**Ver logs completos:**

El scraper imprime logs detallados. Si hay error, revisa la salida para más detalles.

## Ejemplo de Uso Programático

```python
from infrastructure.instagram_http_scraper import InstagramHttpScraper
from infrastructure.json_repository import JsonPostRepository
from app.post_service import PostService

# Crear componentes
scraper = InstagramHttpScraper()
repository = JsonPostRepository()
service = PostService(scraper, repository)

# Extraer y guardar posts
posts = service.extract_and_save_posts(
    profile_username="target_user",
    limit=10,
    file_path="output/posts.json"
)

# Procesar posts
for post in posts:
    print(f"{post.shortcode}: {len(post.hashtags)} hashtags, {post.likes} likes")
```

## Implementación Técnica

### Flujo del Scraper

```
1. Cargar cookies desde .env
   ↓
2. Construir headers realistas (iPhone Instagram)
   ↓
3. Request HTTP a i.instagram.com endpoint
   ↓
4. Validar respuesta (status 200, JSON válido)
   ↓
5. Extraer timeline_media.edges
   ↓
6. Por cada edge: parsear JSON → objeto Post
   ↓
7. Aplicar delay aleatorio (1-3 segundos)
   ↓
8. Guardar lista en JSON
```

### Endpoint Crítico

**Antes (no funciona):**
```
https://www.instagram.com/api/v1/users/web_profile_info/?username=target
```

**Ahora (funciona):**
```
https://i.instagram.com/api/v1/users/web_profile_info/?username=target
```

`i.instagram.com` es el servidor móvil que devuelve datos completos cuando se usan headers móviles.

### Headers Realistas

```python
{
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 246.0.0.0.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "x-ig-app-id": "936619743392459",
    "X-CSRFToken": "{csrf_token}",
    "Referer": "https://www.instagram.com/",
    "Cookie": "sessionid=...; csrftoken=...; ds_user_id=..."
}
```

### Delays Aleatorios

```python
def human_delay(min_s=1.0, max_s=3.0):
    """Espera tiempo aleatorio para simular navegación humana"""
    time.sleep(random.uniform(min_s, max_s))
```

Se aplica entre posts para evitar patrones detectables de bots.

## Estructura JSON Esperada

El endpoint devuelve JSON con estructura:

```
data
└── user
    ├── username
    ├── id
    ├── full_name
    └── edge_owner_to_timeline_media
        └── edges[]
            ├── node (post)
            │   ├── shortcode
            │   ├── id
            │   ├── taken_at_timestamp
            │   ├── caption (con hashtags)
            │   ├── edge_media_to_caption
            │   ├── edge_liked_by (likes)
            │   ├── edge_media_to_comment (comments)
            │   ├── display_url
            │   └── ...
```

## 🎓 Principios Académicos

### ¿Por qué este enfoque?

1. **HTTP + Cookies** (no Selenium)
   - Más eficiente (sin cargar navegador completo)
   - Más rápido (milisegundos vs segundos)
   - Fácil de debuggear (ver requests/responses)

2. **Headers realistas** (no APIs oficiales)
   - Simula cliente legítimo
   - Instagram reconoce como navegador móvil
   - No requiere API key o permiso oficial

3. **Arquitectura limpia** (SOLID)
   - Código mantenible y escalable
   - Fácil de testear
   - Separación clara de responsabilidades

4. **Manejo robusto** (no asumir JSON perfecto)
   - Validación en todos los pasos
   - Extrae datos alternativos si campos cambian
   - Logging detallado para debugging

## Archivos Importantes

| Archivo | Propósito |
|---------|-----------|
| `main.py` | Punto de entrada, orquestación |
| `infrastructure/instagram_http_scraper.py` | Lógica de scraping |
| `infrastructure/headers.py` | Construcción de headers |
| `infrastructure/cookie_manager.py` | Carga de cookies |
| `infrastructure/delay_manager.py` | Delays aleatorios |
| `app/post_service.py` | Orquestador de casos de uso |
| `domain/contracts.py` | Interfaces/contratos |
| `.env` | Variables de entorno (no versionado) |
| `REFACTOR.md` | Documentación técnica detallada |

## Debugging

**Ver logs detallados:**

```bash
# Los logs se muestran automáticamente en consola
# Incluyen:
# - Inicio y fin de cada paso
# - Requests realizadas
# - Estructuras JSON recibidas
# - Errores específicos
```

**Si edges está vacío:**

```
WARNING | EMPTY EDGES - No posts in timeline
WARNING | This could mean:
WARNING |   - Account is private or restricted
WARNING |   - Session cookies are invalid or expired
WARNING |   - Instagram is rate-limiting this session
WARNING |   - Account has no public posts
```

## Referencias

- [RFC 7231 - HTTP/1.1 Semantics](https://tools.ietf.org/html/rfc7231)
- [RFC 6265 - HTTP State Management](https://tools.ietf.org/html/rfc6265)
- [httpx Documentation](https://www.python-httpx.org/)

## Disclaimer Académico y Legal

Este proyecto es **estrictamente para fines educativos** en contextos académicos que requieren demostrar conocimiento de:

- Protocolos HTTP
- Gestión de cookies y sesiones
- Parsing de JSON
- Arquitectura de software

**No constituye:**
- Sistema de scraping a escala
- Intención de evadir protecciones de Instagram
- Violación de Términos de Servicio

**Respeta:**
- Rate limiting (detecta 429)
- Privacidad de datos (solo datos públicos)
- Términos de Servicio de Instagram (uso personal, educativo)

---
