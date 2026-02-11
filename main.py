import pandas as pd
import os
from processors.layer_1_rules import Layer1Rules
from processors.layer_2_ai import Layer2AI

def cargar_y_validar_archivo(ruta_archivo):
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

      
        columnas_requeridas = ['nombre', 'cedula', 'email']
        columnas_actuales = [c.lower() for c in df.columns]

        mapeo = {
            'nombres': 'nombre',
            'identificacion': 'cedula',
            'nit': 'cedula',
            'correo': 'email',
            'e-mail': 'email'
        }

        df.columns = [c.lower() for c in df.columns]
        df.rename(columns=mapeo, inplace=True)


        faltantes = [col for col in columnas_requeridas if col not in df.columns]

        if faltantes:
            print(f"⚠️ Advertencia: Faltan las siguientes columnas: {faltantes}")
           
            for col in faltantes:
                df[col] = None

        return df

    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return None


ruta = "data/mi_archivo_real.xlsx" 
df_sucio = cargar_y_validar_archivo(ruta)

if df_sucio is not None:

    l1 = Layer1Standardizer()
    df_l1 = l1.apply(df_sucio)

    l2 = Layer2Intelligence()
    df_l2 = l2.apply(df_l1)

    ruta_salida = "data/resultado_limpio.xlsx"
    df_l2.to_excel(ruta_salida, index=False)
    print(f"🚀 Proceso terminado. Archivo guardado en: {ruta_salida}")