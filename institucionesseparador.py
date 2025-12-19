import os

def separar_con_ids_reales():
    print("--- CLASIFICADOR PRESERVANDO ID REALES ---")
    archivo_entrada = input("Introduce el archivo generado por el Mapper (ej. instituciones_estado_31.txt): ").strip()

    if not os.path.exists(archivo_entrada):
        print(f"!! Error: No encuentro '{archivo_entrada}'")
        return

    carpeta_salida = "instituciones_procesadas_ids"
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    print(f"--> Procesando '{archivo_entrada}'...")

    # Diccionario para guardar listas de TUPLAS por estado
    # Clave: "VER", Valor: [("5642", "VER - Universidad..."), ("1234", "VER - Otra...")]
    datos_por_estado = {}

    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                if not linea: continue

                # El archivo del Mapper tiene formato: ID_REAL [TAB] NOMBRE
                partes = linea.split('\t')
                
                # Validamos que la línea tenga al menos dos partes (ID y Nombre)
                if len(partes) >= 2:
                    id_real = partes[0].strip()
                    nombre_institucion = partes[1].strip()
                else:
                    # Si la línea está rota, la saltamos o la manejamos
                    continue

                # DETECCIÓN DE ESTADO (Primeras 3 letras del nombre)
                if " - " in nombre_institucion:
                    codigo_estado = nombre_institucion.split(" - ")[0].strip().upper()
                else:
                    codigo_estado = nombre_institucion[:3].upper()

                # Filtro de seguridad
                if len(codigo_estado) < 2 or len(codigo_estado) > 5:
                    codigo_estado = "OTROS"

                # Agregamos a la lista del estado si no existe
                if codigo_estado not in datos_por_estado:
                    datos_por_estado[codigo_estado] = []
                
                # GUARDAMOS LA TUPLA (ID, NOMBRE)
                datos_por_estado[codigo_estado].append((id_real, nombre_institucion))

        # ESCRIBIR ARCHIVOS
        print("\n--> Generando archivos clasificados con IDs ORIGINALES...")
        
        for estado, lista_tuplas in datos_por_estado.items():
            nombre_archivo = os.path.join(carpeta_salida, f"instituciones_{estado}.txt")
            
            with open(nombre_archivo, 'w', encoding='utf-8') as f_out:
                for id_real, nombre in lista_tuplas:
                    # Escribimos: ID_REAL [TAB] NOMBRE
                    f_out.write(f"{id_real}\t{nombre}\n")
            
            print(f"    -> {nombre_archivo}: {len(lista_tuplas)} instituciones.")

        print("\n--> ¡Listo! Los archivos ahora contienen los IDs necesarios para 'select_by_value'.")

    except Exception as e:
        print(f"!! Error: {e}")

if __name__ == "__main__":
    separar_con_ids_reales()