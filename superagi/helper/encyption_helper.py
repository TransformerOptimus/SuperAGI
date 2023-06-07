from cryptography.fernet import Fernet

# Generate a key
# key = Fernet.generate_key()
key = b'e3mp0E0Jr3jnVb96A31_lKzGZlSTPIp4-rPaVseyn58='

cipher_suite = Fernet(key)


def encrypt_data(data):
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data.decode()


def decrypt_data(encrypted_data):
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
    return decrypted_data.decode()
