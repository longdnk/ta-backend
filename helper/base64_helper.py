import base64


def string_to_base64(input_string: str) -> str:
    """
    Chuyển đổi chuỗi sang base64.

    Args:
        input_string (str): Chuỗi văn bản cần chuyển đổi.

    Returns:
        str: Chuỗi được mã hóa base64.
    """
    # Mã hóa chuỗi thành byte và sau đó chuyển thành base64
    base64_bytes = base64.b64encode(input_string.encode("utf-8"))
    return base64_bytes.decode("utf-8")


def base64_to_string(base64_string: str) -> str:
    """
    Chuyển đổi base64 thành chuỗi văn bản gốc.

    Args:
        base64_string (str): Chuỗi base64 cần chuyển đổi.

    Returns:
        str: Chuỗi văn bản gốc.
    """
    # Giải mã base64 thành byte và chuyển thành chuỗi
    decoded_bytes = base64.b64decode(base64_string)
    return decoded_bytes.decode("utf-8")

# Chuỗi gốc
# original_string = ""

# # Chuyển chuỗi sang base64
# encoded_string = string_to_base64(original_string)
# print("Encoded Base64:", encoded_string)

# # Chuyển base64 về chuỗi gốc
# decoded_string = base64_to_string(encoded_string)
# print("Decoded String:", decoded_string)