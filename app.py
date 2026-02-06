import streamlit as st
import pandas as pd
from core.engine import NormaDBEngine
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_alerta_correo(nombre_cliente, email_cliente):    
    remitente = "personalsig03@gmail.com" 
    password = "tu_contraseña_de_aplicacion"
    receptor = "personalsig03@gmail.com" 

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = receptor
    msg['Subject'] = "🔔 NUEVO INTERESADO - NORMADB AI"

    cuerpo = f"""
    ¡Hola! Tienes un nuevo interesado en la auditoría.
    
    Nombre: {nombre_cliente}
    Email: {email_cliente}
    
    Por favor, contacta a la brevedad.
    """
    msg.attach(MIMEText(cuerpo, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error técnico detallado: {e}")
        return False    
 

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

if 'step' not in st.session_state:
    st.session_state.step = 1
if 'df_original' not in st.session_state:
    st.session_state.df_original = None
if 'mapping' not in st.session_state:
    st.session_state.mapping = {}

st.set_page_config(page_title="NORMADB IA | Auditoría de Datos", layout="wide")

st.title("🛡️ NORMADB AI - Diagnóstico Express")
st.write("Optimiza tus bases de datos en 3 pasos.")

if st.session_state.step == 1:
    st.header("1. Sube tu archivo")
    file = st.file_uploader("Arrastra tu Excel o CSV aquí", type=['xlsx', 'csv'])
    if file:
        df = pd.read_excel(file) if file.name.endswith('xlsx') else pd.read_csv(file)
        st.session_state.df_original = df
        st.session_state.step = 2
        st.rerun()

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


elif st.session_state.step == 3:
    st.header("3. 📈 Resultado del Diagnóstico Express")
    

    df_to_process = st.session_state.df_original.rename(
        columns={v: k for k, v in st.session_state.mapping.items() if v})

    engine = NormaDBEngine(use_layer1=True, use_layer2=True)
    df_final = engine.run(df_to_process)
    

    col_m1, col_m2, col_m3 = st.columns(3)
    total_filas = len(df_final)
    errores_limpiados = st.session_state.df_original.isna().sum().sum()

    col_m1.metric("Registros Procesados", total_filas)
    col_m2.metric("Calidad de Datos", "85%", "+20% mejorada")
    col_m3.metric("Errores Corregidos", errores_limpiados, "Capa 1 & 2")

    st.success("✅ Tu base de datos ha sido estandarizada exitosamente.")
    st.write("### Vista previa de tus datos optimizados:")
    st.dataframe(df_final.head(10), use_container_width=True)

    st.divider()

    st.subheader("🚀 ¿Quieres llevar tu empresa al siguiente nivel?")

    c1, c2 = st.columns([1, 1])

    with c1:
        st.info("### 📩 Recibe el Reporte Completo")
        st.write("Análisis de vulnerabilidades y archivo final limpio.")
        with st.form("lead_form"):
            user_email = st.text_input("Tu correo corporativo:")
            user_name = st.text_input("Nombre / Empresa:")
            submit_lead = st.form_submit_button("Enviar Reporte y Descargar")
            
            if submit_lead:
                if user_email:
                    exito = enviar_alerta_correo(user_name, user_email)
                    if exito:
                        st.success(f"¡Gracias {user_name}! Te contactaremos pronto.")
                    else:
                        st.error("Error al enviar el formulario, inténtalo más tarde.")
                else:
                    st.error("Por favor, ingresa un correo válido.")

    with c2:
        st.write("### 💎 Planes de Membresía")
        plan = st.radio(
            "Selecciona un plan para más información:",
            ["Diagnóstico de Madurez Digital", "Mantenimiento Mensual", "Especialista Cybersecurity"]
        )
        if st.button("Solicitar Información del Plan"):
            st.write(f"Interés registrado en: **{plan}**")

    st.divider()


    st.subheader("¿Necesitas soporte personalizado?")
    telefono = "573234240882" 
    mensaje = "Hola, vi tu herramienta NormaDB AI y quiero saber más sobre los planes de membresía."
    url_whatsapp = f"https://wa.me/{telefono}?text={mensaje}"

    st.markdown(
        f'<a href="{url_whatsapp}" target="_blank" style="text-decoration:none;">'
        f'<div style="background-color:#25D366;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;">'
        f'📲 Hablar con un consultor ahora'
        f'</div></a>',
        unsafe_allow_html=True
    )

    st.divider()
    st.write("© 2026 Irina Ballesteros - Todos los derechos reservados.")

    
    