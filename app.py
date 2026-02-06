import streamlit as st
import pandas as pd
from core.engine import NormaDBEngine

# --- CONFIGURACIÓN DE ESTADO ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'df_original' not in st.session_state:
    st.session_state.df_original = None
if 'mapping' not in st.session_state:
    st.session_state.mapping = {}

st.set_page_config(page_title="NORMADB AI | Auditoría de Datos", layout="wide")


# --- LÓGICA DE DETECCIÓN INTELIGENTE ---
def suggest_mapping(columns):
    suggestions = {}
    keywords = {
        'nombre': ['nomb', 'razon', 'cliente', 'full_name', 'user'],
        'cedula': ['id', 'nit', 'cc', 'doc', 'identificacion', 'ced'],
        'email': ['correo', 'mail', 'contacto', '@'],
        'fecha': ['fecha', 'date', 'registro', 'creado']
    }
    for col in columns:
        col_lower = str(col).lower()
        for key, aliases in keywords.items():
            if any(alias in col_lower for alias in aliases):
                suggestions[key] = col
                break
    return suggestions


# --- INTERFAZ ---
st.title("🛡️ NORMADB AI - Diagnóstico Express")
st.write("Optimiza tus bases de datos en 3 pasos.")

# PASO 1: SUBIDA
if st.session_state.step == 1:
    st.header("1. Sube tu archivo")
    file = st.file_uploader("Arrastra tu Excel o CSV aquí", type=['xlsx', 'csv'])
    if file:
        df = pd.read_excel(file) if file.name.endswith('xlsx') else pd.read_csv(file)
        st.session_state.df_original = df
        st.session_state.step = 2
        st.rerun()

# PASO 2: MAPEO (La clave de la flexibilidad)
elif st.session_state.step == 2:
    st.header("2. Confirma la estructura de tus datos")
    df = st.session_state.df_original
    cols = df.columns.tolist()
    suggestions = suggest_mapping(cols)

    st.info("💡 Hemos detectado automáticamente estas columnas. Por favor, confirma o ajusta:")

    col1, col2 = st.columns(2)
    with col1:
        map_nombre = st.selectbox("Columna de Nombres:", [None] + cols,
                                  index=cols.index(suggestions['nombre']) + 1 if 'nombre' in suggestions else 0)
        map_cedula = st.selectbox("Columna de Identidad (NIT/CC):", [None] + cols,
                                  index=cols.index(suggestions['cedula']) + 1 if 'cedula' in suggestions else 0)
    with col2:
        map_email = st.selectbox("Columna de Email:", [None] + cols,
                                 index=cols.index(suggestions['email']) + 1 if 'email' in suggestions else 0)
        map_fecha = st.selectbox("Columna de Fecha:", [None] + cols,
                                 index=cols.index(suggestions['fecha']) + 1 if 'fecha' in suggestions else 0)

    if st.button("Todo correcto, iniciar limpieza ✨"):
        st.session_state.mapping = {
            'nombre': map_nombre,
            'cedula': map_cedula,
            'email': map_email,
            'fecha': map_fecha
        }
        st.session_state.step = 3
        st.rerun()

# PASO 3: RESULTADOS Y DESCARGA
elif st.session_state.step == 3:
    st.header("3. ¡Tu base de datos está lista!")

    # Aquí mapeamos los nombres elegidos por el usuario a los nombres internos
    df_to_process = st.session_state.df_original.rename(
        columns={v: k for k, v in st.session_state.mapping.items() if v})

    # Ejecutamos el motor modular
    engine = NormaDBEngine(use_layer1=True, use_layer2=True)
    df_final = engine.run(df_to_process)

    st.success("Limpieza, estandarización y diagnóstico completado.")
    st.dataframe(df_final.head(10))

    # Botón para volver a empezar
    if st.button("Limpiar otro archivo"):
        st.session_state.step = 1
        st.rerun()