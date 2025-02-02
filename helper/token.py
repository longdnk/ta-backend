import os
import jwt

SECRET_KEY = os.environ["HASH_KEY"]

def create_jwt_token(payload: dict) -> str:
    """
    Tạo JWT token không có thời gian hết hạn
    """
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS512")
    return token