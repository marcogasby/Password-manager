import os
import json
import base64
import uuid
from datetime import datetime
from security.crypto_engine import CryptoEngine

class DBManager:
    def __init__(self, filename="vault.json"):
        self.filename = filename
        self.crypto = CryptoEngine()
        self.active_data = None

    def vault_exists(self) -> bool:
        return os.path.exists(self.filename)

    def create_vault(self, master_password: str) -> bool:
        try:
            initial_structure = self.crypto.initialize_new_vault(master_password)
            with open(self.filename, 'w') as f:
                json.dump(initial_structure, f, indent=4)
            self.active_data = {"categories": ["Generale", "Lavoro", "Social", "Finanze"], "items": []}
            return True
        except Exception:
            return False

    def open_vault(self, master_password: str) -> bool:
        try:
            with open(self.filename, 'r') as f:
                vault_data = json.load(f)
            self.active_data = self.crypto.unlock_vault(master_password, vault_data)
            return True
        except Exception:
            return False

    def save_changes(self):
        if self.active_data is None:
            return
        ciphertext, nonce = self.crypto.encrypt_data(self.active_data)
        with open(self.filename, 'r') as f:
            file_structure = json.load(f)
        file_structure["nonce"] = base64.b64encode(nonce).decode('utf-8')
        file_structure["payload"] = base64.b64encode(ciphertext).decode('utf-8')
        with open(self.filename, 'w') as f:
            json.dump(file_structure, f, indent=4)

    def add_item(self, title, username, password, url, notes, category) -> str:
        item_id = str(uuid.uuid4())
        new_item = {
            "id": item_id,
            "title": title if title else "Senza titolo",
            "username": username,
            "password": password,
            "url": url,
            "notes": notes,
            "category": category,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.active_data["items"].append(new_item)
        self.save_changes()
        return item_id

    def update_item(self, item_id, title, username, password, url, notes, category):
        for item in self.active_data["items"]:
            if item["id"] == item_id:
                item.update({
                    "title": title,
                    "username": username,
                    "password": password,
                    "url": url,
                    "notes": notes,
                    "category": category,
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                break
        self.save_changes()

    def delete_item(self, item_id):
        self.active_data["items"] = [i for i in self.active_data["items"] if i["id"] != item_id]
        self.save_changes()

    def get_items(self):
        return self.active_data["items"] if self.active_data else []

    def get_categories(self):
        return self.active_data["categories"] if self.active_data else []
        
    def add_category(self, name):
        if name and name not in self.active_data["categories"]:
            self.active_data["categories"].append(name)
            self.save_changes()

            