from cryptography.fernet import Fernet, InvalidToken, InvalidSignature

# Generate a key
# key = Fernet.generate_key()
key = b'e3mp0E0Jr3jnVb96A31_lKzGZlSTPIp4-rPaVseyn58='

cipher_suite = Fernet(key)


def encrypt_data(data):
    """
    Encrypts the given data using the Fernet cipher suite.

    Args:
        data (str): The data to be encrypted.

    Returns:
        str: The encrypted data, decoded as a string.
    """
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data.decode()


def decrypt_data(encrypted_data):
    """
    Decrypts the given encrypted data using the Fernet cipher suite.

    Args:
        encrypted_data (str): The encrypted data to be decrypted.

    Returns:
        str: The decrypted data, decoded as a string.
    """
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
    return decrypted_data.decode()


def is_encrypted(value):
    key = b'e3mp0E0Jr3jnVb96A31_lKzGZlSTPIp4-rPaVseyn58='
    try:
        f = Fernet(key)
        f.decrypt(value)
        return True
    except (InvalidToken, InvalidSignature):
        return False
    except (ValueError, TypeError):
        return False
