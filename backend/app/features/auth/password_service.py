import bcrypt

def hash_password(plaintext: str) -> str:
    """
    🔒 Hash password using bcrypt
    Cost factor 12 makes it slow to resist brute force
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plaintext.encode('utf-8'), salt).decode('utf-8')


def verify_password(plaintext: str, hash_value: str) -> bool:
    """
    🔒 Verify plaintext password against bcrypt hash
    """
    return bcrypt.checkpw(plaintext.encode('utf-8'), hash_value.encode('utf-8'))