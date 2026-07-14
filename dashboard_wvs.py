"""
TFM - World Values Survey
Dashboard interactivo de valores socioculturales
Universidad Complutense de Madrid
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================
st.set_page_config(
    page_title="WVS — Valores Socioculturales",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ESTILOS
# ============================================================
st.markdown("""
<style>
    /* Fuente y fondo */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .main { background-color: #F8F9FA; }

    /* Header */
    .header-box {
        background: linear-gradient(135deg, #1B3A6B 0%, #2E6DA4 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .header-box h1 {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    .header-box p {
        color: #B8D4F0;
        font-size: 0.95rem;
        margin: 0.4rem 0 0 0;
    }

    /* Tarjetas de métricas */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        border-left: 4px solid #2E6DA4;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        margin-bottom: 1rem;
    }
    .metric-card h3 {
        color: #1B3A6B;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0 0 0.3rem 0;
    }
    .metric-card .value {
        color: #1B3A6B;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .metric-card .delta {
        font-size: 0.8rem;
        color: #6C757D;
        margin: 0;
    }

    /* Sección */
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1B3A6B;
        border-bottom: 2px solid #2E6DA4;
        padding-bottom: 0.4rem;
        margin: 1.5rem 0 1rem 0;
    }

    /* Hallazgo destacado */
    .insight-box {
        background: #EEF4FB;
        border-left: 4px solid #2E6DA4;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: #1B3A6B;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #9AA0A6;
        font-size: 0.78rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #E0E0E0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATOS (introducidos directamente para no depender del CSV)
# Puedes sustituir por pd.read_csv() si quieres datos dinámicos
# ============================================================

# Valores por generación y ola (Europa Occidental)
datos_generacion = {
    'generacion':    ['Silent','Boomer','Gen X','Millennial','Gen Z'],
    'nacimiento':    ['≤1945','1946-64','1965-80','1981-96','≥1997'],
    'permisividad_ola6': [0.558, 0.662, 0.689, 0.691, None],
    'permisividad_ola7': [0.613, 0.740, 0.764, 0.761, 0.772],
    'genero_ola6':   [0.434, 0.415, 0.414, 0.414, None],
    'genero_ola7':   [0.416, 0.393, 0.384, 0.380, 0.371],
    'religion_ola6': [0.518, 0.433, 0.390, 0.329, None],
    'religion_ola7': [0.510, 0.399, 0.378, 0.359, 0.329],
    'democracia_ola6': [0.440, 0.409, 0.421, 0.433, None],
    'democracia_ola7': [0.423, 0.412, 0.422, 0.430, 0.413],
}
df_gen = pd.DataFrame(datos_generacion)

# Evolución por ola (media Europa Occidental)
olas_labels = ['1981','1990','1995','2000','2005','2010','2019']
olas_nums   = [1, 2, 3, 4, 5, 6, 7]

evolucion = {
    'Silent':     {'permisividad': [None,0.29,0.30,0.51,0.49,0.56,0.61],
                   'genero':       [None,0.56,0.46,0.46,0.44,0.43,0.42],
                   'religion':     [0.75,None,0.59,0.61,0.62,0.52,0.51],
                   'democracia':   [None,None,0.41,0.46,0.42,0.44,0.42]},
    'Boomer':     {'permisividad': [None,0.49,0.63,0.67,0.65,0.66,0.74],
                   'genero':       [None,0.62,0.41,0.43,0.42,0.41,0.39],
                   'religion':     [None,0.59,0.48,0.43,0.48,0.40,0.40],
                   'democracia':   [None,None,0.41,0.47,0.42,0.41,0.41]},
    'Gen X':      {'permisividad': [None,0.57,0.64,0.70,0.69,0.69,0.76],
                   'genero':       [None,0.65,0.42,0.43,0.42,0.41,0.38],
                   'religion':     [None,0.52,0.45,0.43,0.47,0.39,0.38],
                   'democracia':   [None,None,0.40,0.47,0.40,0.42,0.42]},
    'Millennial': {'permisividad': [None,None,0.59,0.64,0.65,0.69,0.76],
                   'genero':       [None,None,0.41,0.46,0.42,0.41,0.38],
                   'religion':     [None,None,None,0.46,0.40,0.33,0.36],
                   'democracia':   [None,None,0.39,0.48,0.42,0.43,0.43]},
}

# Proyecciones
proyecciones = {
    'años': [2019, 2030, 2040],
    'permisividad_A': [0.664, 0.721, 0.760],
    'permisividad_B': [0.660, 0.693, 0.701],
    'genero_A':       [0.412, 0.425, 0.445],
    'genero_B':       [0.409, 0.405, 0.403],
    'religion_A':     [0.463, 0.399, 0.352],
    'religion_B':     [0.465, 0.413, 0.381],
    'democracia_A':   [0.419, 0.414, 0.406],
    'democracia_B':   [0.419, 0.408, 0.393],
}

# Países (última ola disponible)
datos_paises = {
    'pais': ['NLD','SWE','GBR','NOR','DEU','ESP','FRA','CHE','FIN','ITA'],
    'permisividad': [0.82,0.81,0.73,0.69,0.66,0.64,0.52,0.52,0.56,0.33],
    'genero':       [0.38,0.43,0.40,0.38,0.40,0.45,0.39,0.39,0.47,0.44],
    'religion':     [0.36,0.35,0.37,0.42,0.47,0.47,0.42,0.58,0.56,0.77],
    'democracia':   [0.42,0.44,0.43,0.41,0.41,0.48,0.44,0.38,0.39,0.39],
}
df_paises = pd.DataFrame(datos_paises)

# Colores por generación
colores_gen = {
    'Silent':     '#2c7bb6',
    'Boomer':     '#74ADD1',
    'Gen X':      '#FDAE61',
    'Millennial': '#D7191C',
    'Gen Z':      '#1A9641'
}

indices_info = {
    'permisividad': {
        'label': 'Permisividad ética',
        'desc':  'Aceptación de homosexualidad, aborto y divorcio (0=conservador → 1=permisivo)',
        'color': '#2E6DA4'
    },
    'genero': {
        'label': 'Igualdad de género',
        'desc':  'Actitudes hacia igualdad de roles entre hombres y mujeres (0=sexista → 1=igualitario)',
        'color': '#C0392B'
    },
    'religion': {
        'label': 'Religiosidad',
        'desc':  'Importancia de Dios, asistencia religiosa y creencias (0=laico → 1=muy religioso)',
        'color': '#8E44AD'
    },
    'democracia': {
        'label': 'Preferencia democrática',
        'desc':  'Rechazo a líderes fuertes y gobierno militar (0=autoritario → 1=democrático)',
        'color': '#27AE60'
    },
}

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### 🌍 WVS Explorer")
    st.markdown("---")

    st.markdown("**Dimensión de valores**")
    indice_sel = st.selectbox(
        "",
        options=list(indices_info.keys()),
        format_func=lambda x: indices_info[x]['label'],
        label_visibility="collapsed"
    )

    st.markdown("**Generaciones a mostrar**")
    gens_sel = st.multiselect(
        "",
        options=['Silent','Boomer','Gen X','Millennial'],
        default=['Silent','Boomer','Gen X','Millennial'],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**Sobre este dashboard**")
    st.markdown("""
    Análisis del *World Values Survey*
    (1981–2022) para Europa Occidental.

    **TFM — Data Science**
    Universidad Complutense de Madrid
    """)

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="header-box">
    <h1>🌍 Valores Socioculturales en Europa Occidental</h1>
    <p>World Values Survey 1981–2022 · 443.488 entrevistas · 7 olas · 108 países</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# MÉTRICAS RESUMEN
# ============================================================
col1, col2, col3, col4 = st.columns(4)

metricas = {
    'permisividad': {'actual': 0.730, 'anterior': 0.650, 'fmt': '.2f'},
    'genero':       {'actual': 0.389, 'anterior': 0.419, 'fmt': '.2f'},
    'religion':     {'actual': 0.395, 'anterior': 0.418, 'fmt': '.2f'},
    'democracia':   {'actual': 0.420, 'anterior': 0.426, 'fmt': '.2f'},
}

for col, (idx, info) in zip([col1,col2,col3,col4], indices_info.items()):
    m = metricas[idx]
    delta = m['actual'] - m['anterior']
    delta_str = f"{'↑' if delta > 0 else '↓'} {abs(delta):.3f} vs ola anterior"
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{info['label']}</h3>
            <p class="value">{m['actual']:.2f}</p>
            <p class="delta">{delta_str}</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# SECCIÓN 1: EVOLUCIÓN GENERACIONAL
# ============================================================
st.markdown(f"""
<div class="section-title">
    📈 Evolución por generación — {indices_info[indice_sel]['label']}
</div>
""", unsafe_allow_html=True)

st.markdown(f"*{indices_info[indice_sel]['desc']}*")

col_graf, col_info = st.columns([3, 1])

with col_graf:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#F8F9FA')

    for gen in gens_sel:
        if gen in evolucion:
            vals = evolucion[gen][indice_sel]
            x_plot, y_plot = [], []
            for x, y in zip(olas_nums, vals):
                if y is not None:
                    x_plot.append(x)
                    y_plot.append(y)
            if len(x_plot) >= 2:
                ax.plot(x_plot, y_plot,
                        marker='o', label=gen,
                        color=colores_gen[gen],
                        linewidth=2.5, markersize=7)
                ax.annotate(f"{y_plot[-1]:.2f}",
                           (x_plot[-1], y_plot[-1]),
                           textcoords='offset points',
                           xytext=(8, 0), fontsize=8,
                           color=colores_gen[gen], fontweight='bold')

    ax.set_xticks(olas_nums)
    ax.set_xticklabels(olas_labels, fontsize=9)
    ax.set_ylim(0, 1)
    ax.set_ylabel('Índice medio (0–1)', fontsize=9)
    ax.set_xlabel('Ola WVS', fontsize=9)
    ax.legend(fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines[['top','right']].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_info:
    # Tabla resumen ola 7
    st.markdown("**Ola 7 (2019)**")
    for gen in ['Silent','Boomer','Gen X','Millennial','Gen Z']:
        col_key = f"{indice_sel}_ola7"
        val = df_gen[df_gen['generacion'] == gen][col_key].values
        if len(val) > 0 and not pd.isna(val[0]):
            color = colores_gen.get(gen, '#666')
            st.markdown(
                f"<span style='color:{color};font-weight:600'>{gen}</span>: "
                f"<strong>{val[0]:.3f}</strong>",
                unsafe_allow_html=True
            )

# ============================================================
# SECCIÓN 2: COMPARATIVA POR PAÍS
# ============================================================
st.subheader(f"🗺️ Comparativa por país — {indices_info[indice_sel]['label']}")

# Datos por país Y generación (para filtrar por generación seleccionada)
datos_paises_gen = {
    'Silent': {
        'pais': ['NLD','SWE','GBR','NOR','DEU','ESP','FRA','CHE','FIN','ITA'],
        'permisividad': [0.53,0.65,0.44,0.46,0.44,0.45,0.41,0.26,0.45,0.28],
        'genero':       [0.43,0.47,0.38,0.39,0.42,0.43,0.41,0.43,0.44,0.44],
        'religion':     [0.51,0.51,0.53,0.55,0.52,0.54,0.46,0.68,0.64,0.82],
        'democracia':   [0.41,0.42,0.40,0.39,0.39,0.45,0.42,0.36,0.37,0.37],
    },
    'Boomer': {
        'pais': ['NLD','SWE','GBR','NOR','DEU','ESP','FRA','CHE','FIN','ITA'],
        'permisividad': [0.84,0.82,0.73,0.70,0.68,0.62,0.52,0.53,0.57,0.33],
        'genero':       [0.37,0.42,0.39,0.38,0.39,0.43,0.38,0.38,0.46,0.43],
        'religion':     [0.38,0.37,0.39,0.43,0.47,0.47,0.42,0.60,0.57,0.78],
        'democracia':   [0.42,0.44,0.43,0.41,0.41,0.48,0.44,0.38,0.39,0.39],
    },
    'Gen X': {
        'pais': ['NLD','SWE','GBR','NOR','DEU','ESP','FRA','CHE','FIN','ITA'],
        'permisividad': [0.85,0.84,0.76,0.72,0.69,0.67,0.54,0.55,0.59,0.35],
        'genero':       [0.36,0.41,0.38,0.37,0.38,0.44,0.37,0.37,0.46,0.42],
        'religion':     [0.33,0.31,0.34,0.39,0.44,0.44,0.39,0.55,0.52,0.74],
        'democracia':   [0.43,0.45,0.43,0.42,0.42,0.49,0.45,0.39,0.40,0.40],
    },
    'Millennial': {
        'pais': ['NLD','SWE','GBR','NOR','DEU','ESP','FRA','CHE','FIN','ITA'],
        'permisividad': [0.87,0.86,0.78,0.74,0.71,0.70,0.55,0.56,0.60,0.36],
        'genero':       [0.34,0.40,0.38,0.35,0.37,0.43,0.36,0.36,0.45,0.41],
        'religion':     [0.28,0.26,0.29,0.34,0.39,0.39,0.34,0.50,0.47,0.70],
        'democracia':   [0.43,0.45,0.44,0.42,0.42,0.49,0.45,0.39,0.40,0.40],
    },
}

col_p1, col_p2 = st.columns([3, 1])

with col_p1:
    # Calcular media de las generaciones seleccionadas por país
    if gens_sel:
        # Construir dataframe con media de generaciones seleccionadas
        paises_lista = datos_paises_gen['Boomer']['pais']
        valores_filtrados = []
        for pais in paises_lista:
            vals = []
            for gen in gens_sel:
                if gen in datos_paises_gen:
                    idx_pais = datos_paises_gen[gen]['pais'].index(pais)
                    vals.append(datos_paises_gen[gen][indice_sel][idx_pais])
            valores_filtrados.append(np.mean(vals) if vals else np.nan)

        df_paises_filtrado = pd.DataFrame({
            'pais': paises_lista,
            indice_sel: valores_filtrados
        }).dropna().sort_values(indice_sel, ascending=True)
    else:
        df_paises_filtrado = df_paises.sort_values(indice_sel, ascending=True)

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    fig2.patch.set_facecolor('white')
    ax2.set_facecolor('#F8F9FA')

    bars = ax2.barh(df_paises_filtrado['pais'],
                    df_paises_filtrado[indice_sel],
                    color=indices_info[indice_sel]['color'],
                    alpha=0.85, edgecolor='white')
    media = df_paises_filtrado[indice_sel].mean()
    ax2.axvline(x=media, color='#E74C3C', linestyle='--',
                linewidth=1.5, label=f'Media: {media:.2f}')
    for bar, val in zip(bars, df_paises_filtrado[indice_sel]):
        ax2.text(val + 0.01, bar.get_y() + bar.get_height()/2,
                 f'{val:.2f}', va='center', fontsize=9, fontweight='600')
    ax2.set_xlim(0, 1)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3, axis='x', linestyle='--')
    ax2.spines[['top','right']].set_visible(False)

    # Título dinámico según generaciones seleccionadas
    gens_texto = ', '.join(gens_sel) if gens_sel else 'Todas las generaciones'
    ax2.set_title(f'Generaciones: {gens_texto}', fontsize=9, color='gray')

    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

with col_p2:
    st.markdown("**Ranking**")
    datos_rank = df_paises_filtrado.sort_values(
        indice_sel, ascending=False).reset_index(drop=True)
    for i, row in datos_rank.iterrows():
        medalla = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
        st.markdown(f"{medalla} **{row['pais']}** — {row[indice_sel]:.2f}")

# ============================================================
# SECCIÓN 3: PROYECCIÓN 2030–2040
# ============================================================
st.markdown(f"""
<div class="section-title">
    🔮 Proyección 2030–2040 — {indices_info[indice_sel]['label']}
</div>
""", unsafe_allow_html=True)

col_proy, col_proy_info = st.columns([3, 1])

with col_proy:
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    fig3.patch.set_facecolor('white')
    ax3.set_facecolor('#F8F9FA')

    años = proyecciones['años']
    vals_A = proyecciones[f'{indice_sel}_A']
    vals_B = proyecciones[f'{indice_sel}_B']

    ax3.plot(años, vals_A, marker='o', color='#1A9641',
             linewidth=2.5, markersize=8,
             label='Escenario A — Modernización continua')
    ax3.plot(años, vals_B, marker='o', color='#D7191C',
             linewidth=2.5, markersize=8,
             label='Escenario B — Giro conservador Gen Z')

    # Sombrear zona de incertidumbre
    ax3.fill_between(años, vals_B, vals_A,
                     alpha=0.12, color='#2E6DA4',
                     label='Rango de incertidumbre')

    for val, año in zip(vals_A, años):
        ax3.annotate(f"{val:.2f}", (año, val),
                    textcoords='offset points', xytext=(0, 10),
                    ha='center', fontsize=9, color='#1A9641', fontweight='bold')
    for val, año in zip(vals_B, años):
        ax3.annotate(f"{val:.2f}", (año, val),
                    textcoords='offset points', xytext=(0, -16),
                    ha='center', fontsize=9, color='#D7191C', fontweight='bold')

    ax3.axvline(x=2022, color='gray', linestyle=':', alpha=0.6)
    ax3.text(2022.3, ax3.get_ylim()[0] + 0.01,
             'Proyección →', fontsize=8, color='gray')

    ax3.set_xlim(2017, 2043)
    ax3.set_ylim(0, 1)
    ax3.set_xticks([2019, 2030, 2040])
    ax3.set_ylabel('Índice medio (0–1)', fontsize=9)
    ax3.set_xlabel('Año', fontsize=9)
    ax3.legend(fontsize=8, framealpha=0.9)
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.spines[['top','right']].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

with col_proy_info:
    st.markdown("**Valores proyectados**")
    diferencia_2040 = abs(vals_A[-1] - vals_B[-1])
    st.markdown(f"""
    | Año | Esc. A | Esc. B |
    |-----|--------|--------|
    | 2019 | {vals_A[0]:.2f} | {vals_B[0]:.2f} |
    | 2030 | {vals_A[1]:.2f} | {vals_B[1]:.2f} |
    | 2040 | {vals_A[2]:.2f} | {vals_B[2]:.2f} |
    """)
    st.markdown(f"**Divergencia en 2040:** {diferencia_2040:.2f} puntos")

# ============================================================
# HALLAZGOS CLAVE
# ============================================================
hallazgos = {
    'permisividad': """
    📊 **Hallazgo clave:** La permisividad ética sigue aumentando en Europa Occidental
    en todas las generaciones. Los Millennials lideran con 0.76, seguidos de Gen Z (0.77).
    El modelo proyecta una subida a 0.76–0.82 en 2040 según el escenario.
    El error de validación fue del 14.3%, indicando un fuerte efecto de periodo
    (eventos sociales que liberalizan a todas las generaciones simultáneamente).
    """,
    'genero': """
    📊 **Hallazgo clave:** Las actitudes de género están estancadas en ~0.40 en Europa
    Occidental desde los años 2000, sin diferencias generacionales significativas.
    El análisis SHAP revela que **Sexo × Cohorte** es el predictor más importante:
    las mujeres jóvenes son más igualitarias que los hombres jóvenes, confirmando
    una brecha de género dentro de la misma generación.
    """,
    'religion': """
    📊 **Hallazgo clave:** La secularización es el fenómeno más predecible y consistente.
    Cada generación es menos religiosa que la anterior (Silent: 0.51, Gen Z: 0.33).
    El modelo proyecta una caída a 0.35–0.38 en 2040. La religiosidad es el
    predictor más fuerte de la permisividad ética (SHAP: 0.52).
    """,
    'democracia': """
    📊 **Hallazgo clave:** La preferencia democrática es sorprendentemente plana (~0.42)
    en todas las generaciones y países. La desafección democrática es un fenómeno
    transversal, no generacional. El modelo proyecta una ligera caída a 0.39–0.41
    en 2040, siendo la educación y el país los predictores más relevantes (R²=0.07).
    """,
}

st.markdown(f"""
<div class="insight-box">
{hallazgos[indice_sel]}
</div>
""", unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="footer">
    Datos: World Values Survey Time-Series 1981–2022 (v5.0) ·
    Análisis: Europa Occidental (10 países, 64.000+ respondentes) ·
    TFM Data Science — UCM
</div>
""", unsafe_allow_html=True)
