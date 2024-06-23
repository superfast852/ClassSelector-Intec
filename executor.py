import json
from keys.garbler import decrypt
import os
import time
from main import signIn, Firefox
from threading import Thread
from multiprocessing import Process

codes = [code[:-5] for code in os.listdir() if code.endswith(".json")]


def get_classes(id):
    with open(f"{id}.json", "r") as f:
        user_data: dict = json.load(f)
    pwd: str = decrypt(user_data["password"])
    browser: Firefox = signIn(id, pwd)

threads = []
for code in codes:
    threads.append(Process(target=get_classes, args=(code,), daemon=True))
    threads[-1].start()


running = True
while running:
    for thread in threads:
        if thread.is_alive():
            break
    else:
        running = False