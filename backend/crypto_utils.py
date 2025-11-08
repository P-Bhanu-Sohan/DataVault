import json
import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

def encrypt_json(data, key):
    """
    Encrypts a JSON object using AES-256-CBC.
    :param data: JSON-style object to encrypt
    :param key: 32-byte key for AES-256
    :return: Base64-encoded encrypted string
    """
    if len(key) != 32:
        raise ValueError('Key must be 32 bytes for AES-256')

    json_string = json.dumps(data)
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(json_string.encode('utf-8')) + padder.finalize()

    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return base64.b64encode(iv + encrypted_data).decode('utf-8')

def decrypt_json(encrypted_data_b64, key):
    """
    Decrypts an AES-256-CBC encrypted string
    :param encrypted_data_b64: Base64-encoded encrypted string
    :param key: Same 32-byte key used for encryption
    :return: Original JSON object
    """
    if len(key) != 32:
        raise ValueError('Key must be 32 bytes for AES-256')

    decoded_data = base64.b64decode(encrypted_data_b64)
    iv = decoded_data[:16]
    encrypted_data = decoded_data[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_json_bytes = unpadder.update(padded_data) + unpadder.finalize()

    return json.loads(decrypted_json_bytes.decode('utf-8'))

if __name__ == '__main__':
    # Example usage
    secret_key = os.urandom(32) # Generate a random 32-byte key
    data = {'name': 'Bhanu', 'age': 25, 'email': 'bhanu@example.com'}

    encrypted = encrypt_json(data, secret_key)
    print('Encrypted:', encrypted)

    decrypted = decrypt_json(encrypted, secret_key)
    print('Decrypted:', decrypted)
