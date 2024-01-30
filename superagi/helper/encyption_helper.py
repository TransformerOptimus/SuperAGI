import base64

from cryptography.fernet import Fernet, InvalidToken, InvalidSignature
from superagi.config.config import get_config
from superagi.lib.logger import logger
# Generate a key
# key = Fernet.generate_key()

key = get_config("ENCRYPTION_KEY")
if key is None:
    raise Exception("Encryption key not found in config file.")

if len(key) != 32:
    raise ValueError("Encryption key must be 32 bytes long.")

# Encode the key to UTF-8
key = key.encode(
    "utf-8"
)

# base64 encode the key
key = base64.urlsafe_b64encode(key)

# Create a cipher suite
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
    #key = get_config("ENCRYPTION_KEY")
    try:
        f = Fernet(key)
        f.decrypt(value)
        return True
    except (InvalidToken, InvalidSignature):
        return False
    except (ValueError, TypeError):
        return False
