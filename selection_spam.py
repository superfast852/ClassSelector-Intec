from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from time import sleep
import json
from dataclasses import dataclass
from keys.garbler import decrypt


options = FirefoxOptions()
'These are the executional options. Build a JSON format for the options set by the user'
#options.add_argument("--headless")
#options.add_argument("--disable-gpu")

@dataclass
class Materia:
    Clase: str
    Seccion: str
    Aula: str
    Profesor: str
    Lun: str
    Mar: str
    Mie: str
    Jue: str
    Vie: str
    Sab: str


def signIn(id, pwd):  # very simple
    browser = Firefox(options=options)
    browser.get("https://procesos.intec.edu.do")
    browser.find_element(By.ID, 'txtID').send_keys(id)
    browser.find_element(By.ID, 'txtUserPass').send_keys(pwd)
    browser.find_element(By.ID, 'btnEntrar').click()
    return browser


def getClass(browser, id):
    browser.find_element(By.XPATH, f'//*[@id="Asignatura-{id}"]')


def waitGet(browser, id):
    thead_element = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.XPATH, f'//*[@id="{id}"]')))
    return thead_element


id = 1123042
code = "IDS345L"
section = "01"
with open(f"{id}.json", "r") as f:
    user_data: dict = json.load(f)
pwd: str = decrypt(user_data["password"])
browser: Firefox = signIn(id, pwd)  # Log In

browser.find_element(By.ID, 'opProcesosAcademicos').click()
browser.find_element(By.PARTIAL_LINK_TEXT, "Selección").click()  # Go There
try:
    WebDriverWait(browser, 0.5).until(EC.alert_is_present(),
                                   'Timed out waiting for PA creation ' +
                                   'confirmation popup to appear.')

    alert = browser.switch_to.alert
    if alert.text.find("¿Desea continuar?") != -1:
        alert.accept()
        print("alert accepted")
except TimeoutException:
    print("no alert")
    
tabla = waitGet(browser, "tblSeleccion")  # Go to the selection screen
# For every class in there
for i, element in enumerate(tabla.find_elements(By.TAG_NAME, "tbody")):
    # Open the sessions tabs for that class
    if code not in element.text:
        continue
    materia = WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable(element))  # This opens the individual tabs
    browser.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", materia)
    if i%2 == 0:
        continue
    # Get every session for that class
    secciones = materia.find_elements(By.TAG_NAME, "tr")
    for seccion in secciones:
        # TODO: Here goes the selection logic.
        # Here, we should click on the desired class, and then move on.
        """if code not in element.text:
            continue"""
        if section in seccion.text:
            found = True
            while found:
                clickable = seccion.find_elements(By.TAG_NAME, "td")[0]
                please_work = clickable.find_element(By.XPATH, f'//*[@id="{code[:3]}  {code[3:]} {section}                  "]')
                browser.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", please_work)
                try:

                    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH,
                                                                                '/html/body/div[3]/div/div[3]/button[1]')), "Banner not clickable")
                    banner = browser.find_element(By.XPATH, '/html/body/div[3]/div/div[3]/button[1]')
                    banner.click()
                    print("Found Alert.")
                    sleep(5)
                except TimeoutException:
                    found = False
            break
    print("\n-----------------\n")
browser.find_element(By.ID, "btnGuardar").click()

