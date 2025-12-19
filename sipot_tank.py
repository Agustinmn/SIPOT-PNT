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

# -----------------------------------------------------------------------------
# INICIO DEL NAVEGADOR
# -----------------------------------------------------------------------------
print(f"--> Iniciando prueba de selección para el ID: {ESTADO_ID}")
options = uc.ChromeOptions()
browser = uc.Chrome(options=options)

try:
    # 1. NAVEGACIÓN
    url = "https://consultapublicamx.plataformadetransparencia.org.mx/vut-web/faces/view/consultaPublica.xhtml"
    browser.get(url)

    print("--> Esperando carga del sitio y Cloudflare...")
    wait = WebDriverWait(browser, 20)
    
    # Esperamos a que aparezca el contenedor principal del formulario
    wait.until(EC.presence_of_element_located((By.ID, "formEntidadFederativa")))
    print("--> Sitio cargado.")

    # -------------------------------------------------------------------------
    # 2. SELECCIÓN DEL ESTADO (Técnica: Inyección JS + Evento)
    # -------------------------------------------------------------------------
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
    print("--> Observa la ventana: El segundo menú (Institución) debería decir 'Cargando...' o habilitarse.")
    input("\n[PAUSA] El navegador está abierto. Presiona ENTER en esta terminal cuando estés listo para cerrar...")
    # Mantenemos la ventana abierta un momento para que verifiques visualmente
    time.sleep(100)

except Exception as e:
    print(f"!! ERROR: {e}")
    browser.save_screenshot("error_seleccion_estado.png")

finally:
    browser.quit()