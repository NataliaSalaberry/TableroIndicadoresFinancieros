import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Indicadores Financieros de Google",
    page_icon="📊",
    layout="wide"
)

# --- Extracción de Datos ---
@st.cache_data(ttl=3600)  # Guarda los datos en caché por 1 hora
def cargar_datos():
    ticker = "GOOGL"
    datos = yf.download(ticker, period="2y", interval="1d")

    if isinstance(datos.columns, pd.MultiIndex):
        datos = datos.xs(ticker, axis=1, level=1)
        
    datos = datos.reset_index()
    return datos

try:
    df = cargar_datos()
    ultimo_cierre = float(df['Close'].iloc[-1])
    cierre_anterior = float(df['Close'].iloc[-2])
    variacion = ultimo_cierre - cierre_anterior
    porcentaje_var = (variacion / cierre_anterior) * 100
except Exception as e:
    st.error("Error al cargar los datos de Yahoo Finance. Intenta más tarde.")
    st.sidebar.error(f"Detalle técnico: {e}")
    st.stop()

# --- Título Principal ---
st.title("📊 Dashboard de Indicadores Financieros: Alphabet Inc. (GOOGL)")
st.markdown("---")

# --- Creación de Pestañas (Tabs) ---
tab1, tab2, tab3 = st.tabs(["🎯 Presentación", "📈 Gráficos Financieros", "📑 Documentación"])

# ==========================================
# PESTAÑA 1: PRESENTACIÓN
# ==========================================
with tab1:
    st.header("Objetivo del Tablero")
    st.markdown("""
    Este dashboard interactivo se ha sido diseñado con el propósito de **monitorear, analizar y visualizar el comportamiento financiero de las acciones de Google (Alphabet Inc. - GOOGL)** en el mercado de valores para los dos últimos años, utilizando datos en tiempo real extraídos directamente de *Yahoo Finance*.
    
    ### ¿Qué permite hacer esta herramienta?
    * **Evaluar la tendencia de precios:** Identificar la dirección del mercado a través de gráficos de velas japonesas.
    * **Analizar el volumen de transacciones:** Observar el interés y la liquidez del activo en periodos específicos.
    * **Monitorear la volatilidad y medias móviles:** Analizar indicadores técnicos clave (como la Media Móvil Simple) que ayudan a identificar soportes, resistencias y posibles cambios de tendencia.
    
    *Utilice las pestañas de la parte superior para navegar entre las visualizaciones y la documentación.*
    """)
    
    # KPI actual 
    st.subheader("Estado Actual del Activo (Último Cierre)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Ticker", "GOOGL (NASDAQ)")
    col2.metric("Último Precio de Cierre", f"${ultimo_cierre:.2f}")
    col3.metric("Variación Diaria", f"${variacion:.2f}", f"{porcentaje_var:.2f}%")

# ==========================================
# PESTAÑA 2: GRÁFICOS FINANCIEROS
# ==========================================
with tab2:
    st.header("Visualización de Indicadores del Mercado")
    
    # Selector de rango de tiempo a visualizar por parte del usuario
    st.subheader("Configuración del Gráfico")
    dias_a_mostrar = st.slider("Selecciona el número de días históricos a visualizar:", 
                               min_value=30, max_value=len(df), value=180, step=10)
    
    # Filtrar el DataFrame según el slider
    df_filtrado = df.tail(dias_a_mostrar)
    
    # Cálculo de Indicadores Técnicos
    # Media Móvil Simple (SMA) de 20 y 50 días
    df_filtrado = df_filtrado.copy()
    df_filtrado['SMA_20'] = df_filtrado['Close'].rolling(window=20).mean()
    df_filtrado['SMA_50'] = df_filtrado['Close'].rolling(window=50).mean()

    # Construcción del Gráfico con Plotly 
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.15, 
        subplot_titles=('Precio de la Acción y Medias Móviles (USD)', 'Volumen de Transacciones'),
        row_width=[0.3, 0.7] # Distribución de tamaño (30% volumen, 70% precio)
    )

    # 1. Gráfico de Velas (Candlestick)
    fig.add_trace(
        go.Candlestick(
            x=df_filtrado['Date'],
            open=df_filtrado['Open'],
            high=df_filtrado['High'],
            low=df_filtrado['Low'],
            close=df_filtrado['Close'],
            name="Precio de Vela"
        ),
        row=1, col=1
    )

    # 2. Línea de Media Móvil 20 días
    fig.add_trace(
        go.Scatter(
            x=df_filtrado['Date'], 
            y=df_filtrado['SMA_20'], 
            mode='lines', 
            name='SMA 20 días', 
            line=dict(color='orange', width=1.5)
        ),
        row=1, col=1
    )

    # 3. Línea de Media Móvil 50 días
    fig.add_trace(
        go.Scatter(
            x=df_filtrado['Date'], 
            y=df_filtrado['SMA_50'], 
            mode='lines', 
            name='SMA 50 días', 
            line=dict(color='blue', width=1.5)
        ),
        row=1, col=1
    )

    # 4. Gráfico de Barras para el Volumen
    fig.add_trace(
        go.Bar(
            x=df_filtrado['Date'], 
            y=df_filtrado['Volume'], 
            name='Volumen',
            marker=dict(color='purple')
        ),
        row=2, col=1
    )

    fig.update_layout(
        xaxis_rangeslider_visible=False, 
        margin=dict(l=50, r=50, b=50, t=50),
        hovermode='x unified',
        template="plotly_dark" 
    )

    # Mostrar el gráfico interactivo 
    st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar tabla de datos si el usuario lo desea
    with st.expander("Ver datos históricos tabulados (Últimos registros)"):
        st.dataframe(df_filtrado[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].tail(10), use_container_width=True)

# ==========================================
# PESTAÑA 3: DOCUMENTACIÓN
# ==========================================
with tab3:
    st.header("Documentación Técnica y Glosario")
    
    st.subheader("1. Origen de Datos")
    st.markdown("""
    Los datos se obtienen dinámicamente mediante la API de **Yahoo Finance** a través de la librería de código abierto `yfinance`.
    Se extrae el historial diario de precios de Alphabet Inc. (`GOOGL`), el cual incluye las variables: *Apertura (Open), Máximo (High), Mínimo (Low), Cierre (Close) y Volumen*.
    """)
    
    st.subheader("2. Glosario de Indicadores")
    st.markdown("""
    * **Gráfico de Velas (Candlestick):** Muestra de forma compacta cuatro precios clave del día. El cuerpo de la vela representa la apertura y el cierre (verde si subió, rojo si bajó), y las líneas finas muestran los máximos y mínimos alcanzados.
    * **Media Móvil Simple (SMA):** Es el promedio aritmético de los precios de cierre de un número determinado de días hacia atrás. Ayuda a suavizar las fluctuaciones de corto plazo para ver la tendencia limpia.
        * *SMA 20:* Tendencia de corto plazo.
        * *SMA 50:* Tendencia de mediano plazo.
    * **Volumen:** Cantidad total de acciones que cambiaron de manos durante la jornada bursátil. Picos altos de volumen suelen validar la fuerza de un movimiento de precios.
    """)
    
    st.subheader("3. Tecnologías Utilizadas")
    st.markdown("""
    * **Streamlit:** Framework de Python utilizado para renderizar la interfaz de usuario web de manera ágil.
    * **Plotly:** Librería gráfica interactiva que permite hacer zoom, paneo y lecturas precisas al pasar el cursor (hover) por las velas o barras.
    * **Pandas:** Utilizada para la estructuración y cálculo matemático de las medias móviles.
    """)

    st.info("Desarrollado como prototipo funcional para análisis financiero automatizado.")
