from cryptography.fernet import Fernet

def encrypt_env():
    key = Fernet.generate_key()

    # ✅ Solo corregimos "rb" → "wb", la ruta se queda igual
    with open(r"C:\Users\adria\Escritorio\.env.key", "wb") as f:
        f.write(key)

    fernet = Fernet(key)

    with open(".env", "rb") as f:
        encrypted = fernet.encrypt(f.read())

    with open(".env.encrypted", "wb") as f:
        f.write(encrypted)

    print("✅ .env encriptado! Guarda .env.key en un lugar seguro.")
    print("⚠️  Puedes borrar el .env original ahora.")

encrypt_env()