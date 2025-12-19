import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time

# -----------------------------------------------------------------------------
# CONFIGURACIÓN
# -----------------------------------------------------------------------------
ESTADO_ID = input("Introduce el ID del Estado (ej. 31 para Yucatán): ").strip()
institucion_id = input("Introduce el id de la institución a seleccionar: ").strip()
year = input("Introduce el año a seleccionar (ej. 2023): ").strip()
# -----------------------------------------------------------------------------
# INICIO DEL NAVEGADOR
# -----------------------------------------------------------------------------
print(f"--> Iniciando prueba de selección para el ID: {ESTADO_ID}")
options = uc.ChromeOptions()
browser = uc.Chrome(options=options)

    # 1. NAVEGACIÓN
    
url = "https://consultapublicamx.plataformadetransparencia.org.mx/vut-web/faces/view/consultaPublica.xhtml"
browser.get(url)

print("--> Esperando carga del sitio y Cloudflare...")
wait = WebDriverWait(browser, 20)
    # Esperamos a que aparezca el contenedor principal del formulario
wait.until(EC.presence_of_element_located((By.ID, "formEntidadFederativa")))
print("--> Sitio cargado.")



def esperar_estabilidad(driver):
        """Espera a que el sitio termine de cargar y muestre el botón 'Arriba'"""
        print("--> [RELOJ] Esperando estabilización del sitio (Btn 'js_up')...")
        
        # 1. Espera técnica
        WebDriverWait(driver, 40).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        
        # 2. Espera visual (Tu hallazgo clave)
        # Esperamos a que el botón de ir arriba sea visible.
        wait.until(EC.visibility_of_element_located((By.ID, "js_up")))
        
        # 3. Pequeña pausa de seguridad
        time.sleep(1.5)
        print("--> [RELOJ] Sitio estable.")


#Función seleccionar estado
def seleccionar_estado(estado_id):      
    print(f"--> Seleccionando estado...")
    id_select_estado = "formEntidadFederativa:selectEntidad"
    
    selector_estado = browser.find_element(By.ID, id_select_estado)
    browser.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", selector_estado)
    
    # PASO B: Seleccionar el valor usando la librería estándar
    select = Select(selector_estado)
    select.select_by_value(ESTADO_ID)
    
    browser.execute_script("arguments[0].dispatchEvent(new Event('change'));", selector_estado)
    
    print(f"--> ¡HECHO! Estado {ESTADO_ID} seleccionado y evento disparado.")
    
    


def seleccionar_institucion(institucion_id):  
    
    id_select_institucion = "formEntidadFederativa:cboSujetoObligado"
    
    selector_institucion = browser.find_element(By.ID, id_select_institucion)

    browser.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", selector_institucion)

    select = Select(selector_institucion)
    select.select_by_value(institucion_id)
    
    browser.execute_script("arguments[0].dispatchEvent(new Event('change'));", selector_institucion)
    
    print(f"--> ¡HECHO! Institución {institucion_id} seleccionada y evento disparado.")
    
    pass

def esperar_carga_instituciones():
        """Función puente: Espera a que el menú de instituciones tenga datos reales."""
        id_select = "formEntidadFederativa:cboSujetoObligado"
        
        # Esperamos a que el elemento exista
        wait.until(EC.presence_of_element_located((By.ID, id_select)))
        
        # Lógica de espera: ¿Tiene más de 1 opción? (La opción 0 es "Selecciona")
        def menu_tiene_datos(driver):
            elem = driver.find_element(By.ID, id_select)
            # Aseguramos visibilidad para lectura correcta
            driver.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", elem)
            sel = Select(elem)
            return len(sel.options) > 1

        wait.until(menu_tiene_datos)
        print("--> ¡Datos de instituciones recibidos!")


def guardar_instituciones():
        id_select_instituciones = "formEntidadFederativa:cboSujetoObligado"
        
        # 1. Localizar el elemento
        elem_inst = browser.find_element(By.ID, id_select_instituciones)
        
       
    
        print("--> Extrayendo datos masivos vía JavaScript (esto es instantáneo)...")
        
        datos_crudos = browser.execute_script("""
            var select = document.getElementById(arguments[0]);
            var datos = [];
            // Recorremos las opciones directamente en el motor de Chrome
            for (var i = 0; i < select.options.length; i++) {
                var opt = select.options[i];
                datos.push([opt.value, opt.text]);
            }
            return datos;
        """, id_select_instituciones)

        cant = len(datos_crudos)
        nombre_archivo = f"instituciones_estado_{ESTADO_ID}.txt"
        
        print(f"--> Guardando {cant} instituciones en '{nombre_archivo}'...")

        with open(nombre_archivo, "w", encoding="utf-8") as f:
            for item in datos_crudos:
                valor = item[0]
                texto = item[1].strip() # Limpiamos espacios basura
                
                # Filtramos la opción vacía o "Selecciona"
                if valor and "Selecciona" not in texto:
                    f.write(f"{valor}\t{texto}\n")
        
        print(f"--> ¡Archivo guardado con éxito!")

def seleccionar_year(year):
    id_select_year = "formEntidadFederativa:cboEjercicio"
    
    selector_year = browser.find_element(By.ID, id_select_year)

    browser.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", selector_year)

    select = Select(selector_year)
    select.select_by_value(year)
    
    browser.execute_script("arguments[0].dispatchEvent(new Event('change'));", selector_year)
    
    print(f"--> ¡HECHO! Año {year} seleccionado y evento disparado.")
    
def esperar_carga_inicial(driver):
    print("--> Sincronizando: Esperando carga total del sistema...")
    wait = WebDriverWait(driver, 40) 

    # 1. Esperar a que el navegador diga "Ya descargué el HTML"
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')

    # 2. ANCLAJE VISUAL (Tu hallazgo): Esperamos al botón "Arriba"
    # En tu imagen se ve claramente que el ID es "js_up"
    print("--> Esperando señal de estabilidad (Botón 'Ir Arriba')...")
    
    # Esperamos a que sea visible (no solo presente en el código, sino visible al ojo)
    wait.until(EC.visibility_of_element_located((By.ID, "js_up")))
    
    # 3. TIEMPO DE ASENTAMIENTO (BUFFER)
    # Aunque el botón ya salió, a veces los menús tardan medio segundo más en desbloquearse.
    # Una pequeña pausa aquí es higiénica y segura.
    time.sleep(2)

    print("--> Sistema ESTABILIZADO. Procediendo al ataque.")

    print("--> Sistema LISTO y OPERATIVO.")
    
    
esperar_estabilidad(browser)    

try:
        seleccionar_estado(ESTADO_ID)
except:
        pass 

    # 3. Esperamos a que el sitio se calme otra vez
esperar_estabilidad(browser)

    # 4. SEGUNDA SELECCIÓN DE ESTADO (La Definitiva)
    # Ahora que el sitio ya cargó todo lo suyo, imponemos nuestra voluntad.
seleccionar_estado(ESTADO_ID)
    
    # 5. Esperamos a que lleguen los datos de las instituciones
esperar_llenado_instituciones()

    # 6. Seleccionamos Institución
seleccionar_institucion(INSTITUCION_ID)

    # 7. Esperamos un momento (El año suele recargarse al cambiar de institución)
time.sleep(2)
    
    # 8. Seleccionamos Año
seleccionar_year(YEAR)

print("\n--> ¡CONFIGURACIÓN COMPLETA! Esperando panel de obligaciones...")
    # Aquí podrías esperar a que aparezcan los botones de obligaciones
    
input("\n[PAUSA] Presiona ENTER para cerrar...")
    
input("\n[PAUSA] El navegador está abierto. Presiona ENTER en esta terminal cuando estés listo para cerrar...")

