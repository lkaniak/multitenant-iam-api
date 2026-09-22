import base64


def ensure_base32(value: str) -> str:
    encoded_value = base64.b32encode(value.encode("utf-8"))
    return encoded_value.decode("utf-8")
