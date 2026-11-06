from cryptography.fernet import Fernet

# 🔑 CLAVE FIJA (NO CAMBIAR)
clave = b"YUqDSoiZNBxZyP3fmEWF4V0-cwH4p0vKOUhwY_q61m8="

fernet = Fernet(clave)


def encriptar(texto):
    return fernet.encrypt(texto.encode()).decode()


def desencriptar(texto):
    return fernet.decrypt(texto.encode()).decode()
