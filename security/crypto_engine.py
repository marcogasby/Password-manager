import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

class CryptoEngine:
    def __init__(self):
        self.key = None

    def derive_key(self, master_password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        return kdf.derive(master_password.encode())

    def initialize_new_vault(self, master_password: str) -> dict:
        salt = os.urandom(16)
        self.key = self.derive_key(master_password, salt)
        empty_data = {"categories": ["Generale", "Lavoro", "Social", "Finanze"], "items": []}
        ciphertext, nonce = self.encrypt_data(empty_data)
        return {
            "salt": base64.b64encode(salt).decode('utf-8'),
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "payload": base64.b64encode(ciphertext).decode('utf-8')
        }

    def unlock_vault(self, master_password: str, vault_data: dict) -> dict:
        salt = base64.b64decode(vault_data["salt"].encode('utf-8'))
        nonce = base64.b64decode(vault_data["nonce"].encode('utf-8'))
        payload = base64.b64decode(vault_data["payload"].encode('utf-8'))
        self.key = self.derive_key(master_password, salt)
        return self.decrypt_data(payload, nonce)

    def encrypt_data(self, data: dict) -> tuple[bytes, bytes]:
        if not self.key:
            raise ValueError("Chiave non inizializzata.")
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)
        raw_bytes = json.dumps(data).encode('utf-8')
        ciphertext = aesgcm.encrypt(nonce, raw_bytes, None)
        return ciphertext, nonce

    def decrypt_data(self, ciphertext: bytes, nonce: bytes) -> dict:
        aesgcm = AESGCM(self.key)
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        return json.loads(decrypted_bytes.decode('utf-8'))
    
    