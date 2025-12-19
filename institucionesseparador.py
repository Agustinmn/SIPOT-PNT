import os

def separar_y_renumerar():
    print("--- CLASIFICADOR Y RENUMERADOR (Índice Secuencial) ---")
    archivo_entrada = input("Introduce el archivo generado por el Mapper (ej. instituciones_estado_31.txt): ").strip()

    if not os.path.exists(archivo_entrada):
        print(f"!! Error: No encuentro '{archivo_entrada}'")
        return

    carpeta_salida = "instituciones_procesadas"
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    print(f"--> Procesando '{archivo_entrada}'...")

    # Diccionario para guardar listas de líneas por estado
    # Clave: "VER", Valor: ["Texto Inst 1", "Texto Inst 2"...]
    datos_por_estado = {}

    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                if not linea: continue

                # El archivo actual tiene formato: ID_VIEJO [TAB] TEXTO
                # Ejemplo: 5642 [TAB] VER - Universidad Veracruzana
                partes = linea.split('\t')
                
                # Recuperamos solo el texto (el nombre de la institución)
                # Si el archivo tiene tabulador, tomamos la segunda parte. Si no, toda la línea.
                if len(partes) > 1:
                    texto_institucion = partes[1].strip()
                else:
                    texto_institucion = partes[0].strip()

                # DETECCIÓN DE ESTADO (Primeras 3 letras del nombre)
                # Ejemplo: "VER - Universidad..." -> "VER"
                if " - " in texto_institucion:
                    codigo_estado = texto_institucion.split(" - ")[0].strip().upper()
                else:
                    codigo_estado = texto_institucion[:3].upper() # Fallback

                # Filtro de seguridad (evitar estados basura)
                if len(codigo_estado) < 2 or len(codigo_estado) > 5:
                    codigo_estado = "OTROS"

                # Agregamos a la lista de ese estado
                if codigo_estado not in datos_por_estado:
                    datos_por_estado[codigo_estado] = []
                
                datos_por_estado[codigo_estado].append(texto_institucion)

        # ESCRIBIR ARCHIVOS CON NUEVOS IDs
        print("\n--> Generando archivos con IDs secuenciales (Line + 1)...")
        
        for estado, lista_nombres in datos_por_estado.items():
            nombre_archivo = os.path.join(carpeta_salida, f"instituciones_{estado}.txt")
            
            with open(nombre_archivo, 'w', encoding='utf-8') as f_out:
                # REGLA DE ORO: El ID corresponde a la línea + 1
                # Empezamos enumerate en 1 para que coincida con indices de Selenium (opción 0 suele ser "Selecciona")
                # Si en tu lista original la opción 0 ya era válida, cambiamos start=0. 
                # Pero normalmente en SIPOT la 0 es "--Seleccione--", así que la primera válida es la 1.
                
                for indice, nombre in enumerate(lista_nombres, start=1):
                    # Formato final: 1 [TAB] YUC - Ayuntamiento de Mérida
                    f_out.write(f"{indice}\t{nombre}\n")
            
            print(f"    -> {nombre_archivo}: {len(lista_nombres)} instituciones.")

        print("\n--> ¡Listo! Ahora los IDs coinciden con el orden de la lista.")

    except Exception as e:
        print(f"!! Error: {e}")

if __name__ == "__main__":
    separar_y_renumerar()