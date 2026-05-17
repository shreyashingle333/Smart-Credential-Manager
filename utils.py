import random
import string

def generate_random_password(length: int) -> str:

    all_chars = (
        string.ascii_letters +
        string.digits +
        string.punctuation
    )

    return "".join(
        random.choices(all_chars, k=length)
    )