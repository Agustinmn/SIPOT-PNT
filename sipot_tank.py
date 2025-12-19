import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time

# -----------------------------------------------------------------------------
# CONFIGURACIÓN
# -----------------------------------------------------------------------------
ESTADO_ID = input("Introduce el ID del Estado (ej. 31): ").strip()
INSTITUCION_ID = input("Introduce el ID de la institución (Valor interno): ").strip()
YEAR = input("Introduce el año (ej. 2024): ").strip()

print(f"--> Iniciando navegador...")
options = uc.ChromeOptions()
# options.add_argument('--headless') # Descomenta para modo fantasma
browser = uc.Chrome(options=options)
wait = WebDriverWait(browser, 20)

try:
    url = "https://consultapublicamx.plataformadetransparencia.org.mx/vut-web/faces/view/consultaPublica.xhtml"
    browser.get(url)

    # -------------------------------------------------------------------------
    # FUNCIONES TÁCTICAS
    # -------------------------------------------------------------------------
    
    def esperar_desbloqueo_ajax(driver):
        """
        EL SEMÁFORO:
        1. Espera un momento para dar tiempo a que aparezca la cortina.
        2. Si aparece, espera a que se vaya.
        3. Si no aparece, asume que el camino está libre.
        """
        # PAUSA TÁCTICA: Vital para que la cortina tenga tiempo de aparecer tras el clic
        time.sleep(0.8) 
        
        print("--> [SEMÁFORO] Verificando bloqueos de pantalla...")
        
        # Lista de posibles culpables que bloquean la pantalla
        selectores_bloqueo = [
            (By.CSS_SELECTOR, "div.capaBloqueaPantalla"), # El clásico del PNT
            (By.ID, "status"),
            (By.CLASS_NAME, "blockUI") 
        ]
        
        for tipo, selector in selectores_bloqueo:
            try:
                # Esperamos hasta 10 segundos a que el elemento DESAPAREZCA (invisibility)
                # Si el elemento no existe, esta condición se cumple de inmediato (éxito).
                # Si existe, el script se pausa aquí hasta que se vaya.
                WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((tipo, selector)))
            except Exception:
                # Si ocurre un timeout, solo imprimimos advertencia pero seguimos
                # (A veces el bloqueo se queda pegado visualmente pero ya es interactuable)
                print(f"!! Advertencia: El bloqueo '{selector}' tardó demasiado, intentando continuar...")
                pass
        
        print("--> [SEMÁFORO] Luz verde. Continuamos.")

    def seleccionar_estado(estado_id):      
        print(f"--> [ACCIÓN] Seleccionando estado {estado_id}...")
        id_select = "formEntidadFederativa:selectEntidad"
        
        # 1. Esperamos y desbloqueamos
        wait.until(EC.presence_of_element_located((By.ID, id_select)))
        esperar_desbloqueo_ajax(browser)
        
        # 2. Interactuamos
        elem = browser.find_element(By.ID, id_select)
        browser.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", elem)
        
        select = Select(elem)
        select.select_by_value(estado_id)
        
        # 3. Disparamos el evento
        print("--> [DISPARO] Enviando señal de cambio al servidor...")
        browser.execute_script("arguments[0].dispatchEvent(new Event('change'));", elem)
        
        # 4. Esperamos la reacción (La cortina que mencionaste)
        esperar_desbloqueo_ajax(browser)

    def esperar_llenado_instituciones():
        print("--> [DATA] Esperando que la lista de instituciones se llene...")
        id_select = "formEntidadFederativa:cboSujetoObligado"
        
        def menu_tiene_datos(driver):
            elem = driver.find_element(By.ID, id_select)
            driver.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", elem)
            return len(Select(elem).options) > 1

        wait.until(menu_tiene_datos)
        print("--> [DATA] ¡Datos recibidos!")

    def seleccionar_institucion(inst_id):  
        print(f"--> [ACCIÓN] Seleccionando institución {inst_id}...")
        id_select = "formEntidadFederativa:cboSujetoObligado"
        elem = browser.find_element(By.ID, id_select)
        
        browser.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", elem)
        
        select = Select(elem)
        select.select_by_value(inst_id)
        browser.execute_script("arguments[0].dispatchEvent(new Event('change'));", elem)
        
        # Esperamos bloqueo post-selección (a veces recarga el año)
        esperar_desbloqueo_ajax(browser)

    def seleccionar_year(year_target):
        print(f"--> [ACCIÓN] Seleccionando año {year_target}...")
        id_select = "formEntidadFederativa:cboEjercicio"
        wait.until(EC.presence_of_element_located((By.ID, id_select)))
        
        elem = browser.find_element(By.ID, id_select)
        browser.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", elem)

        select = Select(elem)
        select.select_by_value(year_target)
        browser.execute_script("arguments[0].dispatchEvent(new Event('change'));", elem)
        
        esperar_desbloqueo_ajax(browser)
        print(f"--> Año fijado.")

    # -------------------------------------------------------------------------
    # EJECUCIÓN 
    # -------------------------------------------------------------------------
    
    # 1. Carga Inicial
    print("--> Esperando carga del formulario principal...")
    wait.until(EC.presence_of_element_located((By.ID, "formEntidadFederativa")))
    
    # 2. Seleccionar Estado (La función ya incluye la espera del bloqueo)
    seleccionar_estado(ESTADO_ID)

    # 3. Confirmar datos
    esperar_llenado_instituciones()

    # 4. Seleccionar Institución
    seleccionar_institucion(INSTITUCION_ID)

    # 5. Seleccionar Año
    seleccionar_year(YEAR)

    print("\n" + "="*40)
    print("   ¡MISIÓN CUMPLIDA!   ")
    print("="*40)
    input("\n[PAUSA] Presiona ENTER para cerrar...")

except Exception as e:
    print(f"!! ERROR: {e}")
    browser.save_screenshot("error_final.png")
finally:
    browser.quit()