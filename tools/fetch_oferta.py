from main import signIn, By, NoSuchElementException, WebDriverWait, EC, Materia
from pickle import dump
"""
This program fetches all the available classes from the curriculum and saves them in a csv file.
This is to be used later with pandas_analysis to select the desired classes.
"""

def getAssignments(codes="codigos_1123042.txt"):
    with open(codes, "r") as f:
        return [code for code in f.read().split("\n") if code]


def getClass(box, code, browser):
    # Buscar asignatura
    box.send_keys(code)
    browser.find_element(By.ID, 'btnBuscarAsignatura').click()

    # Si se encuentra la asignatura, abrir el area
    try:
        thead_element = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div[4]/div/table/thead/tr/td'))
        )
        browser.execute_script("arguments[0].scrollIntoView(true);", thead_element)
        thead_element.click()
    except NoSuchElementException:
        print(f"Asignatura {code} no encontrada.")

    # Darle click a la asignatura
    asignatura = browser.find_element(By.XPATH, f'/html/body/div/div[2]/div[4]/div/table/tbody/tr/td/table/tbody[1]/tr/td[2]')
    browser.execute_script("arguments[0].scrollIntoView(true);", asignatura)
    asignatura.click()

    tabla = browser.find_element(By.XPATH, '/html/body/div/div[2]/div[4]/div/table/tbody/tr/td/table/tbody[2]/tr/td/table/tbody')
    rows = tabla.find_elements(By.TAG_NAME, "tr")
    out = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        data = [code] + [cell.text for cell in cells[1:]]
        out.append(Materia(*data))
    return out


def GuardarSecciones(secciones, codigo):
    with open(f"./materias/{codigo}.pkl", "wb") as f:
        dump(secciones, f)


if __name__ == "__main__":
    import json
    from keys.garbler import decrypt

    id = "1123042"
    with open(f"{id}.json", "r") as f:
        user_data: dict = json.load(f)
        pwd = decrypt(user_data["password"])

    # Conseguir las asignaturas en el curriculum y guardarlas en un archivo
    materias = getAssignments()  # Lista de codigos de materias
    browser = signIn(id, pwd)  # Iniciar sesion en el sistema
    browser.find_element(By.XPATH, '//*[@id="OpOferta"]').click()  # Ir a la oferta academica
    box = browser.find_element(By.ID, 'txtSearch')  # Darle a la caja de busqueda

    for codigo in materias:  # Para cada materia
        secciones = getClass(box, codigo, browser)  # Encuentra las secciones
        box.clear()  # limpia la caja de busqueda
        GuardarSecciones(secciones, codigo)  # Guarda las secciones en un archivo pickle