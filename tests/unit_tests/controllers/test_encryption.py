import unittest
from unittest.mock import patch
from cryptography.fernet import Fernet
from superagi.helper.encyption_helper import encrypt_data
from superagi.helper.encyption_helper import decrypt_data

class TestEncryptionAndDecryption(unittest.TestCase):
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)

    def test_encrypt_data(self):
        test_data = "Hello, this is a secret message."
        encrypted_data = encrypt_data(test_data)
        # Ensure that the encrypted data is not the same as the original data
        self.assertNotEqual(test_data, encrypted_data)

    def test_decrypt_data(self):
        test_data = "Hello, this is a secret message."
        encrypted_data = encrypt_data(test_data)
        decrypted_data = decrypt_data(encrypted_data)
        # Ensure that the decrypted data matches the original data
        self.assertEqual(test_data, decrypted_data)

if __name__ == '__main__':
    unittest.main()