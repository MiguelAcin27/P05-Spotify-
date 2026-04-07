"""
Spotify Playlist Analyzer – Premium Matplotlib Dashboard
==============================================================
Dashboard con visualizaciones de metadatos precisas y atractivas.
"""

import os
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Spotify",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Premium ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --spotify-green: #1DB954;
        --spotify-dark: #121212;
    }

    html, body, [class*="st-"] { font-family: 'Outfit', 'Inter', sans-serif; }

    .stApp {
        background: #121212;
        color: white;
    }

    .kpi-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--spotify-green);
        margin: 5px 0;
        line-height: 1.2;
    }
    .kpi-label {
        font-size: 0.75rem;
        color: #B3B3B3;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }

    .main-header { padding: 40px 0 20px 0; text-align: center; }
    .main-header h1 {
        font-weight: 900; font-size: 4.5rem;
        color: white; margin: 0; line-height: 1;
    }
    .main-header span { color: var(--spotify-green); }

    .chart-container {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 24px;
        padding: 25px;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 25px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px; background: rgba(255,255,255,0.03);
        padding: 8px 15px; border-radius: 100px;
    }

    /* Ocultar botón de colapso del sidebar (keyboard_double_arrow) */
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }

    /* Ocultar el control cuando está colapsado por si acaso */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Configuración OAuth ──────────────────────────────────────────────────────
REDIRECT_URI = "http://127.0.0.1:8501/callback"
SCOPE = "playlist-read-private playlist-read-collaborative"
load_dotenv()

# ── Utilidades ──────────────────────────────────────────────────────────────

def style_mpl_premium():
    plt.rcParams.update({
        'figure.facecolor': '#12121200',
        'axes.facecolor': '#12121200',
        'axes.edgecolor': '#333333',
        'axes.labelcolor': '#FFFFFF',
        'xtick.color': '#B3B3B3',
        'ytick.color': '#B3B3B3',
        'text.color': '#FFFFFF',
        'grid.color': '#222222',
        'axes.grid': False,
        'font.family': 'sans-serif'
    })

def render_kpi(value, label):
    st.markdown(f"""
    <div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>
    """, unsafe_allow_html=True)

def get_auth_manager(cid, csec):
    return SpotifyOAuth(client_id=cid, client_secret=csec, redirect_uri=REDIRECT_URI, scope=SCOPE, cache_path=".spotify_cache", show_dialog=True)

def extract_playlist_id(url_or_id):
    if not url_or_id: return None
    if "playlist/" in url_or_id:
        pid = url_or_id.split("playlist/")[1]
        return pid.split("?")[0] if "?" in pid else pid
    if ":" in url_or_id: return url_or_id.split(":")[-1]
    return url_or_id.strip()

@st.cache_data(ttl=600, show_spinner=False)
def fetch_playlist_data(_sp, playlist_id):
    try:
        results = _sp.playlist_tracks(playlist_id)
        if not results: return pd.DataFrame()
        items = results.get("items", [])
        while results.get("next"):
            results = _sp.next(results)
            items.extend(results.get("items", []))
    except Exception as e:
        st.error(f"❌ Error API: {e}")
        return pd.DataFrame()

    records = []
    for item in items:
        if not item: continue
        t = item.get("track") or item.get("item") or item
        if not isinstance(t, dict) or not t.get("id"): continue
        
        records.append({
            "nombre": t.get("name", "N/A"),
            "artista": t.get("artists", [{}])[0].get("name", "Desconocido"),
            "album": t.get("album", {}).get("name", "N/A") if t.get("album") else "N/A",
            "duracion_min": round(t.get("duration_ms", 0) / 60000, 2),
            "año": t.get("album", {}).get("release_date", "0000")[:4] if t.get("album") else "0000",
            "fecha_adicion": item.get("added_at", None)
        })
    return pd.DataFrame(records)

# ── Cargar Credenciales (Ocultas de la UI) ──
cid = os.getenv("SPOTIPY_CLIENT_ID")
csec = os.getenv("SPOTIPY_CLIENT_SECRET")

# ── Sidebar ──
with st.sidebar:
    st.image("https://storage.googleapis.com/pr-newsroom-wp/1/2023/05/Spotify_Primary_Logo_RGB_Green.png", width=140)
    st.markdown("---")
    
    # Notificamos si faltan las credenciales internas
    if not cid or not csec:
        st.error("🔑 Credenciales de API no detectadas (.env)")
    
    st.markdown("### 🔌 Conectar")
    purl = st.text_input("Playlist URL", placeholder="https://open.spotify.com/...")
    analyze_btn = st.button("🚀 ANALIZAR PLAYLIST", use_container_width=True)
    if st.session_state.get("spotify_token") and st.button("🚪 Logout", use_container_width=True):
        st.session_state.pop("spotify_token", None); st.rerun()

# ── Autenticación ──
if cid and csec:
    am = get_auth_manager(cid, csec)
    if auth_code := st.query_params.get("code"):
        if not st.session_state.get("spotify_token"):
            try:
                st.session_state["spotify_token"] = am.get_access_token(auth_code, as_dict=True)
                st.query_params.clear(); st.rerun()
            except: pass
    if not st.session_state.get("spotify_token"):
        auth_url = am.get_authorize_url()
        st.sidebar.markdown(f'<a href="{auth_url}" target="_self" style="display:block; text-align:center; background:#1DB954; color:black; font-weight:800; padding:15px; border-radius:50px; text-decoration:none; margin-top:15px;">🔐 LOGIN SPOTIFY</a>', unsafe_allow_html=True)

# ── Main UI ──
st.markdown('<div class="main-header"><h1>Spotify<span>Insights</span></h1><p>Deep Metadata Analysis</p></div>', unsafe_allow_html=True)

if analyze_btn or st.session_state.get("analyzed"):
    if not st.session_state.get("spotify_token"):
        st.warning("⚠️ Inicia sesión en la barra lateral.")
    elif not purl and not st.session_state.get("analyzed"):
        st.info("💡 Pega una URL de playlist.")
    else:
        st.session_state["analyzed"] = True
        if purl: st.session_state["current_purl"] = purl
        
        try:
            with st.spinner("Analizando metadatos..."):
                am_run = get_auth_manager(cid, csec)
                am_run.token_info = st.session_state["spotify_token"]
                sp = spotipy.Spotify(auth_manager=am_run)
                
                pid_clean = extract_playlist_id(st.session_state.get("current_purl"))
                df = fetch_playlist_data(sp, pid_clean)
                
                if not df.empty:
                    # KPIs
                    top_artist = df['artista'].mode()[0] if not df['artista'].empty else "N/A"
                    unique_artists = df['artista'].nunique()
                    
                    # Nuevo KPI: Mes más activo (basado en fecha de adición)
                    mes_top = "N/A"
                    if "fecha_adicion" in df.columns and df["fecha_adicion"].notnull().any():
                        df['dt_adicion'] = pd.to_datetime(df['fecha_adicion'])
                        df['mes_año'] = df['dt_adicion'].dt.strftime('%b %Y')
                        mes_top = df['mes_año'].mode()[0] if not df['mes_año'].empty else "N/A"
                    
                    c1, c2, c3, c4, c5 = st.columns(5)
                    with c1: render_kpi(len(df), "CANCIONES")
                    with c2: render_kpi(unique_artists, "ARTISTAS")
                    with c3: render_kpi(top_artist, "TOP ARTISTA")
                    with c4: render_kpi(int(df['duracion_min'].sum()), "MINUTOS")
                    with c5: render_kpi(mes_top, "MES TOP")

                    st.markdown("<br>", unsafe_allow_html=True)
                    t_mat, t_exp = st.tabs(["KPIs :)", "📋 TRACKLIST"])
                    
                    with t_mat:
                        style_mpl_premium()
                        
                        # 0. Gráfico de Área: Actividad Mensual (Minutos añadidos)
                        if "mes_año" in df.columns:
                            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                            st.subheader("📈 Actividad Mensual")
                            # Agrupar y ordenar cronológicamente
                            df_m = df.groupby(['mes_año', 'dt_adicion']).agg({'duracion_min':'sum'}).reset_index()
                            # Re-agrupar solo por mes_año para el gráfico pero manteniendo el orden temporal
                            df_m = df.groupby('mes_año')['duracion_min'].sum().reset_index()
                            # Nota: Para que el orden sea correcto, podríamos necesitar una columna temporal real
                            df_m['temp_date'] = pd.to_datetime(df_m['mes_año'], format='%b %Y')
                            df_m = df_m.sort_values('temp_date')
                            
                            fig, ax = plt.subplots(figsize=(12, 4))
                            ax.fill_between(df_m['mes_año'], df_m['duracion_min'], color='#1DB954', alpha=0.2)
                            ax.plot(df_m['mes_año'], df_m['duracion_min'], color='#1DB954', marker='o', linewidth=3, markersize=8)
                            
                            ax.spines['top'].set_visible(False)
                            ax.spines['right'].set_visible(False)
                            ax.spines['left'].set_alpha(0.3)
                            ax.spines['bottom'].set_alpha(0.3)
                            plt.xticks(rotation=0)
                            
                            # Añadir etiquetas de valor
                            for i, val in enumerate(df_m['duracion_min']):
                                ax.text(i, val + (df_m['duracion_min'].max()*0.05), f'{int(val)}min', 
                                        ha='center', color='white', fontweight='bold', fontsize=9)
                            
                            st.pyplot(fig); plt.close(fig)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # 1. Gráfico de Barras Horizontal: Top 10 Artistas
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        st.subheader("🏆 El Top 10 de tu Playlist")
                        top10 = df['artista'].value_counts().head(10).sort_values(ascending=True)
                        fig, ax = plt.subplots(figsize=(10, 5))
                        bars = ax.barh(top10.index, top10.values, color='#1DB954', height=0.6)
                        ax.spines['top'].set_visible(False)
                        ax.spines['right'].set_visible(False)
                        ax.xaxis.set_visible(False)
                        for bar in bars:
                            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                                    f'{int(bar.get_width())}', va='center', color='white', fontweight='bold')
                        st.pyplot(fig); plt.close(fig)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # 2. SECCIÓN DE AÑOS Y ÁLBUMES
                        p1, p2 = st.columns(2)
                        with p1:
                            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                            st.subheader("📅 Evolución por Años")
                            # Contar por años individuales (últimos 15 que tengan canciones)
                            años = df[df['año'] != '0000']['año'].value_counts().sort_index().tail(15)
                            fig, ax = plt.subplots(figsize=(6, 6))
                            if not años.empty:
                                bars_v = ax.bar(años.index, años.values, color='#1DB954', alpha=0.8)
                                plt.xticks(rotation=45, color='white')
                                ax.spines['top'].set_visible(False)
                                ax.spines['right'].set_visible(False)
                                for b in bars_v:
                                    yval = b.get_height()
                                    ax.text(b.get_x() + b.get_width()/2, yval + 0.1, int(yval), 
                                            ha='center', va='bottom', color='white', fontsize=10)
                            st.pyplot(fig); plt.close(fig)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with p2:
                            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                            st.subheader("💿 Variedad de Álbumes")
                            sh = df['album'].value_counts().head(6)
                            fig, ax = plt.subplots(figsize=(6, 6))
                            ax.pie(sh.values, labels=sh.index, wedgeprops=dict(width=0.4),
                                   colors=plt.cm.Greens(np.linspace(0.9, 0.3, len(sh))),
                                   textprops={'color':"white"})
                            st.pyplot(fig); plt.close(fig)
                            st.markdown('</div>', unsafe_allow_html=True)

                    with t_exp:
                        st.dataframe(df[['nombre', 'artista', 'album', 'duracion_min', 'año']], use_container_width=True)
                else:
                    st.error("📉 No hay datos para mostrar.")
        except Exception as e:
            st.error(f"⚠️ Error: {e}"); st.session_state["analyzed"] = False
else:
    st.markdown('<div style="text-align:center; padding: 100px 0;"><h1 style="font-size:3.5rem; color:#1DB954; font-weight:800;">DATA MINING.</h1><p style="color:#666; font-size:1.2rem;">Conecta tu cuenta y analiza tus colecciones musicales de forma profesional.</p></div>', unsafe_allow_html=True)
