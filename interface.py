import dearpygui.dearpygui as dpg
from pickle import load, dump
import json
from main import Materia, signIn, By, NoSuchElementException, WebDriverWait, EC, TimeoutException
from keys.garbler import encrypt, decrypt
import os

dpg.create_context()
id = ""
user_data = {}
fields = ["Prioridad", "Clase", "Seccion", "Aula", "Profesor", "Lun", "Mar", "Mie", "Jue", "Vie", "Sab"]
class_names = []


# add a font registry
with dpg.font_registry():
    # first argument ids the path to the .ttf or .otf file
    default_font = dpg.add_font("Satoshi-Regular.otf", 20)
    second_font = dpg.add_font("Satoshi-Regular.otf", 14)


# ------------------- Login Window -------------------


# Function to handle login button click
def login_callback(sender, data):
    # Retrieve input values
    user_id = dpg.get_value("##ID")
    password = dpg.get_value("##Password")
    if user_id == "":
        popup("Please enter an ID", "Error")
        return
    if password == "":
        popup("Please enter a password", "Error")
        return

    # pop_item("time_table")
    try:
        # Try to load user data from file
        with open(f"{user_id}.json", "r") as f:
            global user_data
            user_data = json.load(f)
            if decrypt(user_data["password"]) == password:
                print("Login successful")
                global id, class_names
                id = user_id
                class_names = list(user_data.get("classes", {}).keys())
                create_main_menu()
                #tri = load_classes()
                #create_table(tri, list(tri.keys())[num])
                pop_item("login")
            else:
                popup("Incorrect password", "Error")
    except FileNotFoundError:
        # If file not found, create an empty dictionary
        popup("User not found", "Error")


def register_callback(sender, data):
    user_id = dpg.get_value("##ID")
    password = dpg.get_value("##Password")
    if (user_id + ".json") in os.listdir(".") or user_id == "":
        popup("User already exists", "Error")
    else:
        def postmortem(sender, data):
            pop_item("popup")
            pop_item("login")
            #tri = load_classes()
            #create_table(tri, list(tri.keys())[num])
            create_main_menu()


        # If file not found, create an empty dictionary
        global user_data
        user_data = {"password": encrypt(password).decode(), "classes": {}}
        with open(f"{user_id}.json", "w") as f:
            json.dump(user_data, f)
            global id
            id = user_id
            popup("User created successfully", "Success", callback=postmortem)


# ------------------- Main Menu ----------------------

def get_fetched_classes():
    global class_names
    if len(class_names) == 0:
        return []
    return [code[:-4] for code in os.listdir("./materias/") if code[:-4] in class_names]


# ---------- Time Fetching Utilities ----------------


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


# Define your fetch_callback function
def fetch_callback(sender, data):
    global class_names
    dpg.show_item("loader")
    not_found = []
    # Save all the registered class names in the json with empty dictionaries
    with open(f"{id}.json", "w") as f:
        user_data["classes"] = {class_name: {} for class_name in class_names}
        json.dump(user_data, f)

    try:
        browser = signIn(id, decrypt(user_data["password"]))
        # ------------------- Fetch the schedule

        # Conseguir las asignaturas en el curriculum y guardarlas en un archivo
        browser.find_element(By.XPATH, '//*[@id="OpOferta"]').click()  # Ir a la oferta academica
        box = browser.find_element(By.ID, 'txtSearch')  # Darle a la caja de busqueda

        for codigo in class_names:  # Para cada materia
            try:
                secciones = getClass(box, codigo, browser)  # Encuentra las secciones
            except TimeoutException:
                not_found.append(codigo)
                box.clear()
                continue
            box.clear()  # limpia la caja de busqueda
            GuardarSecciones(secciones, codigo)  # Guarda las secciones en un archivo pickle
        # Write a file with all the codes
        with open(f"codigos_{id}.txt", "w") as f:
            f.write("\n".join(class_names))
        browser.close()

        # This assumes that all classes have been found and saved.
        dpg.configure_item("class_lbx", items=class_names)  # Update the listbox to have all codes.
        if not_found:
            # TODO: Configure this properly.
            popup(f"Couldn't find the following classes: {', '.join(not_found)}", "Warning", 200, 100)
            with open(f"{id}.json", "w") as f:
                for clase in not_found:
                    user_data["classes"].pop(clase)
                json.dump(user_data, f)
    except Exception as e:
        print(f"[ERROR]: {e}: {e.args}")
    finally:
        dpg.hide_item("loader")


# Create the left section of the window
# noinspection PyArgumentList
def create_left_section():
    with dpg.group(horizontal=False):
        dpg.add_text("Select a class to view its schedule")
        dpg.add_listbox(tag="class_lbx", items=get_fetched_classes(), width=165, num_items=10)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Select Times", callback=open_scheduler_callback)
            dpg.add_button(label="Fetch Schedule", callback=fetch_callback)
        dpg.add_text("If you haven't yet, please press the 'Fetch Schedule' button to load the classes", wrap=200)
        dpg.add_text("[WARNING]: This will automatically connect to the INTEC portal under your account.", wrap=200)
        dpg.add_button(label="Exit", callback=lambda: dpg.stop_dearpygui(), pos=(5, 575))



# Create the right section of the window (similar to previous dynamic list creation)
# noinspection PyArgumentList
def create_right_section():
    with dpg.group(horizontal=False):
        dpg.add_text("Type in the codes for the classes you want to take")
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="##InputText", width=200)
            dpg.add_button(label="Add Item", callback=add_item_callback)
        dpg.add_listbox(tag="##ListBox", label="Classes", width=200, num_items=10, items=class_names)
        dpg.add_button(label="Remove Item", callback=remove_item_callback)
        dpg.add_text("Make sure to type in the code correctly.")


# Callback for adding items to the dynamic list
def add_item_callback(sender, data):
    new_item: str = dpg.get_value("##InputText")
    if new_item == "":
        return
    class_names.append(new_item.upper().strip())
    if new_item:
        dpg.configure_item("##ListBox", items=class_names)
        dpg.set_value("##InputText", "")  # Clear the input field after adding the item


def remove_item_callback(sender, data):
    selected_item: str = dpg.get_value("##ListBox")
    if selected_item in class_names:
        class_names.remove(selected_item)
        dpg.configure_item("##ListBox", items=class_names)
        dpg.set_value("##InputText", "")  # Clear the input field after adding the item


def open_scheduler_callback(sender, data):
    code = dpg.get_value("class_lbx")
    if code == "":
        return
    with open(f"./materias/{code}.pkl", "rb") as f:
        times = load(f)
    pop_item("time_table")
    create_table(code, times)


# noinspection PyArgumentList
def create_main_menu():
    # Call the function to create the window
    with dpg.window(tag="main", label="Main Menu", height=600, width=800):
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=20)
            dpg.add_text("Schedule Selector")
            dpg.add_spacer(width=150)
            dpg.add_text("Class List")
        with dpg.group(tag="boxes", horizontal=True):
            create_left_section()
            create_right_section()
        with dpg.popup(parent="boxes", tag="loader", modal=True):
            dpg.add_text("Fetching items...")

# ------------------- Table Window -------------------


def Materia_To_List(materia):
    return [materia.Clase, materia.Seccion, materia.Aula, materia.Profesor, materia.Lun, materia.Mar, materia.Mie,
            materia.Jue, materia.Vie, materia.Sab]


# Note: we may not need to load every single class at all, just the one that the user wants to check out.
def load_classes():
    '''
    This fetches every class picked and loads the times for each into the tri dictionary.
    :return:
    '''
    tri = {}
    try:
        codigos = list(user_data.get("classes", {}).keys())
        for codigo in codigos:
            with open(f"materias/{codigo}.pkl", "rb") as f:
                secciones = load(f)
            tri[codigo] = secciones
        return tri
    except FileNotFoundError:
        return None


def popup(message, label, width=150, height=50, callback=None):
    if callback is None:
        def self_callback(sender, data):
            pop_item("popup")
        callback = self_callback

    with dpg.window(tag="popup", label=label, width=width, height=height, pos=(400-(width//2), 300-(height//2))):
        dpg.add_text(message)
        dpg.add_button(label="OK", callback=callback)


def save_callback(sender, data):
    global user_data

    # Get the class number
    class_times, class_code = dpg.get_item_user_data(sender)
    save_pkl = f"./materias/{id}_{class_code}_organized.pkl"

    def postmortem(sender, data):
        pop_item("popup")
        pop_item("time_table")

    organized = list(range(len(class_times)))  # Make an empty list with n elements for classes
    for i, seccion in enumerate(class_times):  # For every class available
        tag = f"##CBX{seccion.Clase}_{seccion.Seccion}"

        # If the position as set by the cmb value already has a class, insert it in the next position
        if isinstance(organized[int(dpg.get_value(tag)) - 1], Materia):
            organized.insert(int(dpg.get_value(tag)), seccion)

        else:  # If the position is empty, insert the class there
            organized[int(dpg.get_value(tag)) - 1] = seccion

    organized = [item for item in organized if isinstance(item, Materia)]  # Filter out numbers

    with open(save_pkl, "wb") as f:  # Save the organized classes to a pkl
        dump(organized, f)

    user_data["classes"][class_code] = save_pkl
    with open(f"{id}.json", "w") as f:
        json.dump(user_data, f)

    popup("Classes Saved successfully!", "Success", 150, 50, postmortem)


def pop_item(tag):
    dpg.delete_item(tag)


# noinspection PyArgumentList
def create_table(class_code, class_times):
    '''
    This function creates a table with the classes available for the user to pick.
    :param tri: A dictionary containing every class and their sections
    :param selection: The specific class that the user wants to analyze
    :return: None, it renders out the window.
    '''
    # Table window
    with dpg.window(tag="time_table", label="Seleccion de Clases"):
        with dpg.table(row_background=False,
                       borders_innerH=True, borders_outerH=True, borders_innerV=True,
                       borders_outerV=True, policy=dpg.mvTable_SizingFixedFit, no_host_extendX=True):
            # use add_table_column to add columns to the table,
            for field in fields:
                dpg.add_table_column(label=field)

            # add_table_next_column will jump to the next row
            # once it reaches the end of the columns
            # table next column use slot 1
            for i, seccion in enumerate(class_times):
                datos = Materia_To_List(seccion)
                with dpg.table_row():
                    dpg.add_combo(tag=f"##CBX{seccion.Clase}_{seccion.Seccion}", items=["1", "2", "3", "4", "5"], width=50,
                                  default_value=str(i+1))
                    for dato in datos:
                        dpg.add_text(dato)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Save", callback=save_callback, user_data=[class_times, class_code])
            dpg.add_button(label="Cancel", callback=lambda sender, data: pop_item("time_table"))


# ----------- Entrypoint


# Login Window
with dpg.window(tag="login", width=500, height=500):
    dpg.add_text("Login")
    dpg.add_input_text(tag="##ID", label="ID")
    dpg.add_input_text(tag="##Password", label="Password", password=True)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Login", callback=login_callback)
        dpg.add_button(label="Register", callback=register_callback)


# Rendering stuff
dpg.create_viewport(title="GG's Automatic Class Selector", width=1280, height=720)
dpg.bind_font(second_font)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("login", True)
dpg.start_dearpygui()
dpg.destroy_context()