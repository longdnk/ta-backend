import secrets
import jwt

# Khóa bí mật dùng để ký JWT
SECRET_KEY = secrets.token_hex(32) # Thay bằng một chuỗi bảo mật thực sự
ALGORITHM = "HS256"  # Thuật toán ký, thường sử dụng HS256


# Hàm tạo JWT không hết hạn
def create_jwt_token(user_id: str, user_name: str, user_email):
    to_encode = {"sub": f"{user_id}-{user_name}-{user_email}"}  # Không có trường "exp" nên token không hết hạn
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
