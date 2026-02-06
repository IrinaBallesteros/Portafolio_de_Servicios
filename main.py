import pandas as pd
import os
from processors.layer_1_rules import Layer1Standardizer
from processors.layer_2_ai import Layer2Intelligence


def cargar_y_validar_archivo(ruta_archivo):
    # 1. Detectar extensión y cargar
    extension = os.path.splitext(ruta_archivo)[1].lower()

    try:
        if extension == '.csv':
            df = pd.read_csv(ruta_archivo)
        elif extension in ['.xlsx', '.xls']:
            df = pd.read_excel(ruta_archivo)
        else:
            print("❌ Formato no soportado.")
            return None

        print(f"✅ Archivo cargado exitosamente. Filas: {len(df)}")

        # 2. VALIDACIÓN: Comprobar columnas mínimas
        # Aquí definimos qué columnas necesita NORMADB para trabajar
        columnas_requeridas = ['nombre', 'cedula', 'email']
        columnas_actuales = [c.lower() for c in df.columns]

        # Diccionario de traducción (Mapeo inteligente simple)
        mapeo = {
            'nombres': 'nombre',
            'identificacion': 'cedula',
            'nit': 'cedula',
            'correo': 'email',
            'e-mail': 'email'
        }

        # Renombrar columnas automáticamente si coinciden con el mapeo
        df.columns = [c.lower() for c in df.columns]
        df.rename(columns=mapeo, inplace=True)

        # Verificar si después del mapeo faltan columnas
        faltantes = [col for col in columnas_requeridas if col not in df.columns]

        if faltantes:
            print(f"⚠️ Advertencia: Faltan las siguientes columnas: {faltantes}")
            # Podrías crear las columnas vacías para que el código no falle
            for col in faltantes:
                df[col] = None

        return df

    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return None


# --- FLUJO DE EJECUCIÓN ---

ruta = "data/mi_archivo_real.xlsx"  # <--- Cambia esto por el nombre de tu archivo
df_sucio = cargar_y_validar_archivo(ruta)

if df_sucio is not None:
    # CAPA 1
    l1 = Layer1Standardizer()
    df_l1 = l1.apply(df_sucio)

    # CAPA 2
    l2 = Layer2Intelligence()
    df_l2 = l2.apply(df_l1)

    # Guardar resultado
    ruta_salida = "data/resultado_limpio.xlsx"
    df_l2.to_excel(ruta_salida, index=False)
    print(f"🚀 Proceso terminado. Archivo guardado en: {ruta_salida}")