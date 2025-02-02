import os
import base64
import jwt
import datetime

SECRET_KEY = os.environ['HASH_KEY']

def hash_base64(input_string: str) -> str:
    """Mã hóa chuỗi bằng Base64"""
    encoded_bytes = base64.b64encode(input_string.encode("utf-8"))
    return encoded_bytes.decode("utf-8")

def create_password(input: str) -> str:
    return (hash_base64(input) + hash_base64(SECRET_KEY)) * 2