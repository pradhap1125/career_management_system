import hashlib
import hmac
import base64

def hash_password(password: str, secret_key: str) -> str:

    hashed = hmac.new(secret_key.encode(), password.encode(), hashlib.sha256).digest()
    return base64.b64encode(hashed).decode()


# password = "password"
# secret_key = "acs57501"
# hashed_password = hash_password(password, secret_key)
# print("Hashed Password:", hashed_password)