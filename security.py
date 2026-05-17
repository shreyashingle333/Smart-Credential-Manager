import os
import hashlib
import binascii
import string

def hash_password(password: str) -> tuple[str, str]:
    salt = os.urandom(16)

    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000
    )

    return (
        binascii.hexlify(dk).decode(),
        binascii.hexlify(salt).decode()
    )

def verify_password(
    stored_password: str,
    stored_salt: str,
    provided_password: str
) -> bool:

    salt = binascii.unhexlify(stored_salt.encode())

    dk = hashlib.pbkdf2_hmac(
        "sha256",
        provided_password.encode(),
        salt,
        100000
    )

    return binascii.hexlify(dk).decode() == stored_password

def check_strength(password: str) -> str:

    strength = 0

    if any(c.islower() for c in password):
        strength += 1

    if any(c.isupper() for c in password):
        strength += 1

    if any(c.isdigit() for c in password):
        strength += 1

    if any(c in string.punctuation for c in password):
        strength += 1

    if len(password) >= 8:
        strength += 1

    if strength <= 2:
        return "Weak"

    elif strength == 3:
        return "Medium"

    return "Strong"