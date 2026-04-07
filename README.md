🎵 Spotify Insights – Deep Metadata Analyzer
Esta es una aplicación de análisis de datos de alto rendimiento construida con Streamlit y Matplotlib. La herramienta permite realizar una auditoría completa de cualquier playlist de Spotify, extrayendo metadatos profundos y visualizándolos en un dashboard de diseño "Premium Dark".

🚀 Funcionalidades Principales
La aplicación se conecta a la API oficial de Spotify (Spotipy) para ofrecer:

Dashboard de KPIs en Tiempo Real:

Contador de Canciones: Total de pistas analizadas.

Diversidad de Artistas: Número de artistas únicos en la lista.

Top Artista: Identificación automática del artista con más presencia.

Tiempo Total: Suma de la duración de todas las pistas en minutos.

Mes Top: Identificación del mes con mayor actividad de adición de canciones.

Visualizaciones Avanzadas (Matplotlib):

Gráfico de Área: Tendencia temporal de actividad mensual.

Top 10 Artistas: Ranking horizontal de los artistas más escuchados.

Evolución Cronológica: Histograma de distribución por año de lanzamiento.

Variedad de Álbumes: Gráfico de tipo donut para ver la composición de la playlist.

Exportación de Datos: Incluye una pestaña de exploración para visualizar el dataset completo generado.

🛠️ Stack Tecnológico
Frontend: Streamlit con inyección de CSS personalizado para estética Spotify.

Procesamiento: Python & Pandas.

Visualización: Matplotlib (configurado con estilo premium dark).

Autenticación: Protocolo OAuth 2.0 a través de la API de Spotify.

📂 Estructura del Repositorio
/codigo: Contiene el motor de la app (app.py), los estilos y requerimientos.

/data: Repositorio del dataset exportado/generado durante el análisis.

🔧 Configuración para Desarrolladores
Para ejecutar este proyecto localmente:

Crea un entorno virtual: python -m venv .venv

Instala las dependencias: pip install -r codigo/requirements.txt

Configura tus credenciales en un archivo .env (usa .env.example como guía):

SPOTIPY_CLIENT_ID

SPOTIPY_CLIENT_SECRET

SPOTIPY_REDIRECT_URI=http://localhost:8501/callback

Lanza la aplicación: streamlit run codigo/app.py
