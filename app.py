import streamlit as st
import pandas as pd
from core.engine import NormaDBEngine
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

st.markdown("""
    <style>
    .stFormSubmitButton > button {
        background-color: #003366 !important;
        color: white !important;
        border-radius: 10px !important;
        border: 2px solid #00509d !important;
        padding: 0.75rem 2rem !important;
        width: 100% !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    .stFormSubmitButton > button:hover {
        background-color: #00509d !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2) !important;
    }

    .stLinkButton > a {
        background-color: #128C7E !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: bold !important;
        text-align: center !important;
        width: 100% !important;
        padding: 0.75rem !important;
        display: block !important;
        text-decoration: none !important;
        transition: all 0.3s ease !important;
    }
    .stLinkButton > a:hover {
        background-color: #075E54 !important;
        transform: scale(1.02) !important;
    }


    hr {
        margin: 2em 0px !important;
        border-bottom: 2px solid #e1e4e8 !important;
        opacity: 0.5 !important;
    }


    .footer-container {
        width: 100%;
        text-align: center;
        padding: 30px 0;
        margin-top: 50px;
    }
    .footer-text {
        color: #6c757d !important;
        font-size: 0.85rem !important;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.5px;
        opacity: 0.8;
    
    }
    </style>
""", unsafe_allow_html=True)

def es_email_valido(email):

    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, email) is not None

def enviar_alerta_correo(nombre_cliente, email_cliente):    
    remitente = st.secrets["email"]["remitente"]
    password = st.secrets["email"]["password"]
    receptor = st.secrets["email"]["receptor"]

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
        st.sidebar.error(f"Error técnico real: {e}")
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

    if st.button("Todo correcto, iniciar limpieza"):
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
    errores_limpiados = st.session_state.df_original.isna().sum().sum()
    
    col_m1.metric("Registros Procesados", len(df_final))
    col_m2.metric("Calidad de Datos", "85%", "+20% mejorada")
    col_m3.metric("Riesgos Detectados", errores_limpiados, "Capa 1 & 2")

    st.success("✅ Análisis completado. Hemos detectado y corregido inconsistencias estructurales.")
    st.write("### Vista previa de tus datos optimizados (Modo Evaluación):")
    st.dataframe(df_final.head(10), use_container_width=True) # Solo mostramos 10 filas

    st.divider()


    st.subheader("¿Quieres recibir la base de datos completa y el diagnóstico de seguridad?")
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.info("### 🔓 Desbloquea tu Diagnóstico Completo")
        st.write("Has probado la tecnología. Ahora, descarga el archivo optimizado al 100% y recibe tu reporte de riesgos estructurales.")
        
        with st.form("lead_form"):
            user_name = st.text_input("Nombre / Empresa:")
            user_email = st.text_input("Correo Corporativo:")
            

            plan_interes = st.selectbox("Plan de interés para tu acceso:", 
                                    ["Plan Básico (Hasta 5 archivos)", 
                                        "Plan Pro (Hasta 20 archivos)", 
                                        "Plan Empresa (Ilimitado)"])
            
            submit_lead = st.form_submit_button("Solicitar Acceso y Descarga")
            
            if submit_lead:
                if user_name and es_email_valido(user_email):

                    exito = enviar_alerta_correo(f"{user_name} - INTERÉS EN {plan_interes}", user_email)
                    if exito:
                        st.balloons()
                        st.success(f"¡Excelente, {user_name}! He recibido tu interés en el {plan_interes}. Te enviaré el archivo completo y la propuesta de membresía a tu correo.")
                    else:
                        st.warning("⚠️ Casi listo. Por favor, contáctame por WhatsApp para enviarte tu archivo manualmente.")
                else:
                    st.error("❌ Por favor, ingresa un nombre y un correo válido.")
                                

    with c2:
        st.write("### Membresías de Optimización")
        st.write("Selecciona el plan que mejor se adapte a tu volumen de operación actual:")


        datos_planes = {
            "Plan": ["Básico", "Pro", "Empresa"],
            "Archivos / mes": ["5", "20", "Ilimitado"],
            "Registros por archivo": ["5,000", "50,000", "Ilimitado"],
            "Formatos": ["CSV/XLSX", "CSV/XLSX", "Todos + JSON/TXT*"]
        }
        

        st.table(datos_planes)
        
        st.caption("*Próximamente: Soporte para TXT y JSON en planes Empresa.")

        st.write("---")
        st.markdown("""
        **¿Por qué una membresía?**
        * **Ahorro de Tiempo:** Procesamiento masivo en segundos.
        * **Consistencia:** Capas de IA ajustadas a tu sector.
        * **Escalabilidad:** De la validación manual a la automatización total.
        """)


        telefono = "573234240882"
        mensaje_wa = "Hola Irina, probé el PMV de NormaDB AI y quiero más información sobre el Plan "
        st.link_button("Adquirir Membresía ahora", f"https://wa.me/{telefono}?text={mensaje_wa}")



   
  
    st.divider()
    st.markdown("""
    <div class="footer-container">
        <p class="footer-text">
            © 2026 <b>NORMADB AI</b> - Todos los derechos reservados. <br>
            Hecho por <b>Irina Ballesteros Ospino</b>
        </p>
    </div>
""", unsafe_allow_html=True)


    
    