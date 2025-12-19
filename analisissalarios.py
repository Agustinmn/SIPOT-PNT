import pandas as pd
import re
import os

def limpiar_y_exportar_nomina_con_nombres(input_path, output_path="nomina_con_nombres.xlsx"):
    print(f"[1/5] Leyendo archivo crudo: {input_path}")
    
    # 1. DETECCIÓN DE ENCABEZADO
    df_raw = pd.read_excel(input_path, header=None)
    
    # Buscamos la fila que contiene los headers reales
    try:
        # Usamos 'PRIMER APELLIDO' como ancla segura
        idx_header = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains('PRIMER APELLIDO', case=False).any(), axis=1)].index[0]
    except IndexError:
        print("Error: No se encontró la fila de encabezados. Verifica el archivo.")
        return

    # 2. CARGA DE DATOS
    df = pd.read_excel(input_path, header=idx_header)
    
    # 3. LIMPIEZA DE FILAS BASURA (Repetición de headers por paginación)
    col_pivote = df.columns[0]
    # Si el valor de la celda es igual al nombre de la columna, es un header repetido
    df = df[df[col_pivote] != col_pivote]
    df.dropna(how='all', inplace=True)

    print(f"[2/5] Procesando {len(df)} registros...")

    # 4. SELECCIÓN DE COLUMNAS (AHORA INCLUYENDO NOMBRES)
    columnas_map = {
        'NOMBRE (S)': 'nombre',
        'PRIMER APELLIDO': 'primer_apellido',
        'SEGUNDO APELLIDO': 'segundo_apellido',
        'DENOMINACIÓN O DESCRIPCIÓN DEL PUESTO (REDACTADOS CON PERSPECTIVA DE GÉNERO)': 'puesto',
        'ÁREA DE ADSCRIPCIÓN': 'area_adscripcion',
        'SEXO (CATÁLOGO )': 'sexo',
        'MONTO DE LA REMUNERACIÓN MENSUAL BRUTA  DE CONFORMIDAD AL TABULADOR DE SUELDOS Y SALARIOS QUE CORRESPONDA': 'monto_bruto',
        'MONTO DE LA REMUNERACIÓN MENSUAL NETA  DE CONFORMIDAD AL TABULADOR DE SUELDOS Y SALARIOS QUE CORRESPONDA': 'monto_neto',
        'FECHA DE INICIO DEL PERIODO QUE SE INFORMA': 'periodo_inicio',
        'FECHA DE TÉRMINO DEL PERIODO QUE SE INFORMA': 'periodo_fin'
    }
    
    # Filtramos y renombramos
    cols_existentes = [c for c in columnas_map.keys() if c in df.columns]
    df_clean = df[cols_existentes].copy()
    df_clean.rename(columns=columnas_map, inplace=True)

    # 5. LIMPIEZA Y FORMATO
    
    # A) Nombres: Rellenar vacíos y estandarizar mayúsculas
    for col in ['nombre', 'primer_apellido', 'segundo_apellido']:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna('').astype(str).str.strip().str.upper()
    
    # B) Crear columna de Nombre Completo (Útil para búsquedas)
    if set(['nombre', 'primer_apellido', 'segundo_apellido']).issubset(df_clean.columns):
        df_clean['nombre_completo'] = (df_clean['nombre'] + ' ' + 
                                       df_clean['primer_apellido'] + ' ' + 
                                       df_clean['segundo_apellido']).str.strip()
        
        # Reordenamos para que el nombre completo aparezca al principio
        cols = ['nombre_completo'] + [c for c in df_clean.columns if c != 'nombre_completo']
        df_clean = df_clean[cols]

    # C) Dinero: Limpieza de $ y comas
    def limpiar_dinero(val):
        if pd.isna(val): return 0.0
        clean_str = re.sub(r'[$,\s]', '', str(val))
        try:
            return float(clean_str)
        except ValueError:
            return 0.0

    print("[3/5] Limpiando montos y textos...")
    for col in ['monto_bruto', 'monto_neto']:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].apply(limpiar_dinero)

    # D) Textos restantes
    for col in ['puesto', 'area_adscripcion', 'sexo']:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip().str.upper()

    # 6. EXPORTACIÓN
    print(f"[4/5] Guardando en: {output_path}")
    df_clean.to_excel(output_path, index=False)
    print(f"[5/5] Finalizado. {df_clean.shape[0]} registros limpios exportados.")
    
    return df_clean

if __name__ == "__main__":
    # Ajusta el nombre de tu archivo aquí
    archivo_entrada = "Formato 8 LGT_Art_70_Fr_VIII_3er trimestre_4523467_1.xlsx"
    
    if os.path.exists(archivo_entrada):
        limpiar_y_exportar_nomina_con_nombres(archivo_entrada)
    else:
        print(f"No encuentro {archivo_entrada}. Revisa la ruta.")