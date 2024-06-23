'''
This program is the main assignment picker. At a certain time, this program executes and picks the desired classes.
TODO: Make a polling mechanism to constantly try to enter the site when the time is right.
'''

# ------------------- SETUP

from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from time import sleep
import json
from dataclasses import dataclass

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


if __name__ == "__main__":
    from keys.garbler import decrypt
    from pickle import load
    id = "1123042"
    # ------------------- Get the class codes
    with open("codigos.txt", "r") as f:
        codigos = [code for code in f.read().split("\n") if code]
        print(codigos)

    with open(f"{id}.json", "r") as f:
        user_data: dict = json.load(f)
        pwd = decrypt(user_data["password"])
    # ------------------- Going into the selection screen
    browser = signIn(id, pwd)
    browser.find_element(By.ID, 'opProcesosAcademicos').click()
    browser.find_element(By.PARTIAL_LINK_TEXT, "Selección").click()
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

    # ------------------- Checking if the desired classes are available.
    tabla = waitGet(browser, "tblSeleccion")  # Go to the selection screen
    # For every class in there
    for i, element in enumerate(tabla.find_elements(By.TAG_NAME, "tbody")):
        # Open the sessions tabs for that class
        browser.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)
        materia = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable(element))  # This opens the individual tabs
        if i%2 == 0:
            continue
        # Get every session for that class
        secciones = materia.find_elements(By.TAG_NAME, "tr")
        for seccion in secciones:
            # TODO: Here goes the selection logic.
            # Here, we should click on the desired class, and then move on.
            print(seccion.text)

        print("\n-----------------\n")

    # Click on the Save button, very important
    #browser.close()


def main(id, p=True):
    from keys.garbler import decrypt
    with open(f"{id}.json", "r") as f:
        user_data: dict = json.load(f)
    pwd: str = decrypt(user_data["password"])
    browser: Firefox = signIn(id, pwd)

    # Navigate to selection
    browser.find_element(By.ID, 'opProcesosAcademicos').click()
    browser.find_element(By.PARTIAL_LINK_TEXT, "Selección").click()
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

    # Path 1
    if p:  # We search for every class individually and pick the time that way. This ensures that we have every class.
        box = browser.find_element(By.ID, 'txtSearch')  # Go to search box
        for code in list(user_data.get("classes", {}).keys()):
            box.send_keys(code)
            press_search()
            # TODO: This is very unfinished.
    else:  # First iterate through the preselected classes and then search for the missing ones.
        classes: dict = user_data["classes"]
        class_names: list = list(classes.keys())
        tabla = waitGet(browser, "tblSeleccion")  # Go to the selection screen
        # For every class in there
        for i, element in enumerate(tabla.find_elements(By.TAG_NAME, "tbody")):
            # Open the sessions tabs for that class
            try:
                # TODO: Make it so that 'element.text' is the actual code of the current iterated element (format it).
                user_times_path: str = classes[element.text]
                with open(user_times_path, "rb") as f:
                    user_times = load(f)
                    class_names.remove(element.text)

                browser.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)
                materia = WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable(element))  # This opens the individual tabs

                if i % 2 == 0:
                    continue

                # Get every session for that class
                secciones = materia.find_elements(By.TAG_NAME, "tr")
                for seccion in secciones:
                    # TODO: Here goes the selection logic.
                    # Here, we should click on the desired class, and then move on.
                    print(seccion.text)

                print("\n-----------------\n")
            except KeyError:
                continue


        # Click on the Save button, very important
        # browser.close()



def press_search():
    pass


def click_assignment():
    pass
