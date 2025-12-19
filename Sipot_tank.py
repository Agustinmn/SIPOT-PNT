import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time

# -----------------------------------------------------------------------------
# CONFIGURACIÓN
# -----------------------------------------------------------------------------
# Puedes cambiar esto manualmente o usar input()
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

#Función seleccionar estado
def seleccionar_estado(estado_id):      
    print(f"--> Seleccionando estado...")
    # Este es el ID real del <select> oculto por Bootstrap
    id_select_estado = "formEntidadFederativa:selectEntidad"
    
    # Localizamos el elemento (aunque esté oculto)
    selector_estado = browser.find_element(By.ID, id_select_estado)
    
            # PASO A: Hacerlo visible para que Selenium pueda interactuar
    browser.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", selector_estado)
    
    # PASO B: Seleccionar el valor usando la librería estándar
    select = Select(selector_estado)
    select.select_by_value(ESTADO_ID)
    
    # PASO C (EL CRÍTICO): Disparar el evento 'change' manualmente
    # Sin esto, el sitio no sabe que seleccionaste nada y no cargará las instituciones.
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
        
        # 2. EXTRACCIÓN RELÁMPAGO (JAVASCRIPT)
        # En lugar de usar un bucle de Python lento, le pedimos al navegador
        # que nos devuelva una matriz pura de texto [[valor, nombre], [valor, nombre]...]
        # Esto evita el error StaleElementReferenceException porque no guardamos referencias, solo texto.
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

seleccionar_estado(ESTADO_ID)
seleccionar_institucion(institucion_id)
esperar_carga_instituciones()
seleccionar_year(year)
input("\n[PAUSA] El navegador está abierto. Presiona ENTER en esta terminal cuando estés listo para cerrar...")

