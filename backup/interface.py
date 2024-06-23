import dearpygui.dearpygui as dpg
from pickle import load, dump
import json
from main import Materia
from keys.garbler import encrypt, decrypt
import os

dpg.create_context()
id = ""
user_data = None
fields = ["Prioridad", "Clase", "Seccion", "Aula", "Profesor", "Lun", "Mar", "Mie", "Jue", "Vie", "Sab"]
num = 0


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

    pop_item("main")
    try:
        # Try to load user data from file
        with open(f"{user_id}.json", "r") as f:
            global user_data
            user_data = json.load(f)
            if decrypt(user_data["password"]) == password:
                print("Login successful")
                global id
                id = user_id
                # TODO: Create the main interface. This leads to the table window
                tri = load_classes()
                create_table(tri, list(tri.keys())[num])
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
            # TODO: Create the main interface. This leads to the table window
            # This will crash, since a new user obviously won't have any classes
            tri = load_classes()
            create_table(tri, list(tri.keys())[num])

        # If file not found, create an empty dictionary
        global user_data
        user_data = {"password": encrypt(password).decode(), "classes": {}}
        with open(f"{user_id}.json", "w") as f:
            json.dump(user_data, f)
            global id
            id = user_id
            popup("User created successfully", "Success", callback=postmortem)


# Login Window
with dpg.window(tag="login", width=500, height=500):
    dpg.add_text("Login")
    dpg.add_input_text(tag="##ID", label="ID")
    dpg.add_input_text(tag="##Password", label="Password", password=True)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Login", callback=login_callback)
        dpg.add_button(label="Register", callback=register_callback)


# ------------------- Table Window -------------------


def Materia_To_List(materia):
    return [materia.Clase, materia.Seccion, materia.Aula, materia.Profesor, materia.Lun, materia.Mar, materia.Mie,
            materia.Jue, materia.Vie, materia.Sab]


def load_classes():
    tri = {}
    try:
        with open(f"codigos_{id}.txt", "r") as f:
            codigos = [code for code in f.read().split("\n") if code]
        for codigo in codigos:
            print(f"Codigo: {codigo}")
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
    user_classes, selection = dpg.get_item_user_data(sender)
    save_pkl = f"./materias/{id}_{selection}_organized.pkl"

    def postmortem(sender, data):
        pop_item("popup")
        pop_item("main")

    # TODO: Figure out how we're gonna save the picks for the user in the json file
    organized = list(range(len(user_classes[selection])))  # Make an empty list with n elements for classes

    for i, seccion in enumerate(user_classes[selection]):  # For every class available
        tag = f"##CBX{seccion.Clase}_{seccion.Seccion}"

        # If the position as set by the cmb value already has a class, insert it in the next position
        if isinstance(organized[int(dpg.get_value(tag)) - 1], Materia):
            organized.insert(int(dpg.get_value(tag)), seccion)

        else:  # If the position is empty, insert the class there
            organized[int(dpg.get_value(tag)) - 1] = seccion

    organized = [item for item in organized if isinstance(item, Materia)]  # Filter out numbers

    with open(save_pkl, "wb") as f:  # Save the organized classes to a pkl
        dump(organized, f)

    if user_data is None:
        with open(f"{id}.json", "r") as f:  # Load the user data
            user_data = json.load(f)
    user_data["classes"][selection] = save_pkl
    with open(f"{id}.json", "w") as f:
        json.dump(user_data, f)

    popup("Classes Saved successfully!", "Success", 150, 50, postmortem)


def pop_item(tag):
    dpg.delete_item(tag)


def create_table(tri, selection):
    # Table window
    with dpg.window(tag="main", label="Seleccion de Clases"):
        with dpg.table(row_background=False,
                       borders_innerH=True, borders_outerH=True, borders_innerV=True,
                       borders_outerV=True, policy=dpg.mvTable_SizingFixedFit, no_host_extendX=True):
            # use add_table_column to add columns to the table,
            for field in fields:
                dpg.add_table_column(label=field)

            # add_table_next_column will jump to the next row
            # once it reaches the end of the columns
            # table next column use slot 1
            for i, seccion in enumerate(tri[selection]):
                datos = Materia_To_List(seccion)
                with dpg.table_row():
                    dpg.add_combo(tag=f"##CBX{seccion.Clase}_{seccion.Seccion}", items=["1", "2", "3", "4", "5"], width=50,
                                  default_value=str(i+1))
                    for dato in datos:
                        dpg.add_text(dato)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Save", callback=save_callback, user_data=[tri, selection])
            dpg.add_button(label="Cancel", callback=lambda sender, data: pop_item("main"))


# Rendering stuff
dpg.create_viewport(title="GG's Automatic Class Selector", width=1280, height=720)
dpg.bind_font(second_font)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("login", True)
dpg.start_dearpygui()
dpg.destroy_context()