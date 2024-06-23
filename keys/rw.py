from cryptography.fernet import Fernet

try:
    with open("./keys/.key", "rb") as f:
        key = f.read()
except FileNotFoundError:
    with open(".key", "rb") as f:
        key = f.read()

crypter = Fernet(key)


def lock():
    with open("./keys/algo.py", 'rb') as f:
        file = crypter.encrypt(f.read())
    with open("./keys/algo.py", 'wb') as f:
        f.write(b'"' + file + b'"')


def unlock():
    with open("./keys/algo.py", "rb") as f:
        file = crypter.decrypt(f.read()[1:-1])
    with open("./keys/algo.py", 'wb') as f:
        f.write(file)


if __name__ == '__main__':
    unlock()