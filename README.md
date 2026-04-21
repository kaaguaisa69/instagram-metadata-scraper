# Instagram Metadata Scraper

## 1. Descripción del proyecto

Instagram Metadata Scraper es una solución en Python para extraer la metadata de las 10 publicaciones más recientes de una cuenta de Instagram y guardarla en formato JSON.

La extracción contempla campos clave para análisis de contenido, entre ellos:

- `caption`
- `hashtags`
- `likes`
- `comments` (comentarios)
- `typename` (tipo de publicación)
- `url`
- `date_utc` (fecha)

En la primera etapa se implementó extracción mediante scraping con Instaloader. Posteriormente, debido a restricciones de autenticación, bloqueo de endpoints y rate limiting, se evaluó la migración hacia la API oficial de Instagram como estrategia más estable para escenarios reales.

## 2. Arquitectura del proyecto

El proyecto está organizado con una arquitectura por capas para separar responsabilidades y facilitar mantenimiento:

- `domain`: modelos de negocio y contratos (interfaces).
- `app`: lógica de negocio y orquestación del caso de uso.
- `infrastructure`: implementaciones concretas (scraper, configuración y persistencia).
- `main.py`: punto de entrada y ensamblaje de dependencias.

### Principios SOLID aplicados

- **SRP (Single Responsibility Principle):** cada clase tiene una responsabilidad concreta (extraer, persistir, orquestar, modelar).
- **DIP (Dependency Inversion Principle):** `PostService` depende de abstracciones (`PostScraper`, `PostRepository`) y no de implementaciones concretas.
- **OCP (Open/Closed Principle):** se pueden añadir nuevas implementaciones (por ejemplo, repositorio SQL o scraper por API oficial) sin modificar la lógica central del servicio.

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

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 8.3 Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 8.4 Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```env
INSTAGRAM_USERNAME=tu_usuario_sin_arroba
INSTAGRAM_PASSWORD=tu_password
```

### 8.5 Ejecutar

```powershell
python main.py
```

Al finalizar, el sistema genera el archivo de salida en:

- `output/latest_posts.json`

## 9. Ejemplo de salida (JSON)

```json
[
	{
		"shortcode": "DABC123xyz",
		"post_id": "1234567890123456789",
		"permalink": "https://www.instagram.com/p/DABC123xyz/",
		"date_utc": "2026-04-20T15:42:10+00:00",
		"caption": "Ejemplo de publicación #python #data",
		"hashtags": ["python", "data"],
		"mentions": ["usuario_demo"],
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

## 10. Buenas prácticas aplicadas

- separación clara de responsabilidades por capa;
- uso de contratos (interfaces) para desacoplar lógica e implementación;
- manejo de credenciales mediante variables de entorno;
- captura y comunicación de errores relevantes en autenticación/login;
- persistencia estructurada para facilitar integraciones posteriores.

## 11. Posibles mejoras

- integración completa con Instagram Graph API oficial;
- estrategias de rate limiting y reintentos controlados;
- persistencia en base de datos (PostgreSQL/MySQL) para consultas analíticas;
- logging estructurado (JSON logs) con niveles y trazabilidad.

## 12. Nota de alcance

La versión actual cumple el objetivo de extracción de metadata en entorno controlado. Para uso productivo, la ruta recomendada es la migración a API oficial y la incorporación de monitoreo, observabilidad y controles de resiliencia.
