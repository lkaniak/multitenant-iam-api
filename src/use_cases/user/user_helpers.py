import hashlib
import hmac
import re
import secrets
import string
from random import choice

from entities.enum.user_type_enum import UserTypeEnum
from entities.user_entity import UserEntity

PASSWORD_HASH_ALGORITHM = "sha512"
PASSWORD_HASH_ITERATIONS = 120000
PASSWORD_HASH_SALT_BYTES = 16


def is_valid_email(email: str) -> bool:
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


def is_valid_organization_owner_name(name: str) -> bool:
    return not re.match(r"[\s\W]", name)


def generate_password() -> str:
    special_chars = "".join(choice(string.punctuation) for _ in range(2))
    digits = "".join(choice(string.digits) for _ in range(2))
    letters = "".join(choice(string.ascii_letters) for _ in range(10))
    return letters + special_chars + digits


def is_sys_admin_user(user: UserEntity) -> bool:
    return UserTypeEnum.from_str(user.user_type) == UserTypeEnum.SYSTEM_ADMIN


def encrypt_password(password: str) -> str:
    salt = secrets.token_bytes(PASSWORD_HASH_SALT_BYTES)
    derived = hashlib.pbkdf2_hmac(
        PASSWORD_HASH_ALGORITHM,
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    return f"{PASSWORD_HASH_ITERATIONS}${salt.hex()}${derived.hex()}"


def verify_password(challenge: str, hashed_password: str) -> bool:
    try:
        iterations, salt_hex, digest_hex = hashed_password.split("$")
        derived = hashlib.pbkdf2_hmac(
            PASSWORD_HASH_ALGORITHM,
            challenge.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(derived, bytes.fromhex(digest_hex))
    except (ValueError, TypeError):
        return False
