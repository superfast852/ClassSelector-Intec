from cryptography.fernet import Fernet

with open("./keys/.key", "rb") as f:
    key = f.read()


def encrypt(text):
    pass


def decrypt(text):
    pass


crypter = Fernet(key)
with open("./keys/algo.py", 'rb') as f:
    file = crypter.decrypt(f.read()[1:-1])
    exec(file)
