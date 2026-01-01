# Guardar como backend.py
import sqlite3
import hashlib
import base64
from cryptography.fernet import Fernet
import os

class PasswordManagerLogic:
    def __init__(self, db_name="mis_claves.db"):
        self.db_name = db_name
        self.key = None # Aquí se guardará la llave temporalmente
        self._init_db()

    def _init_db(self):
        """Inicializa la base de datos si no existe."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT NOT NULL,
                username TEXT NOT NULL,
                encrypted_pass TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def login(self, master_password):
        """
        Genera la llave de encriptación basada en la contraseña maestra.
        Retorna True si el proceso fue exitoso.
        """
        # Convertimos la contraseña maestra en una llave de 32 bytes segura
        # Usamos SHA256 para asegurar longitud correcta para Fernet
        k = hashlib.sha256(master_password.encode()).digest()
        self.key = base64.urlsafe_b64encode(k)
        return True

    def add_password(self, site, username, password):
        """Encripta y guarda una nueva contraseña."""
        if not self.key:
            raise Exception("La bóveda está bloqueada. Haz login primero.")
        
        f = Fernet(self.key)
        encrypted_pass = f.encrypt(password.encode()).decode()
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO credentials (site, username, encrypted_pass) VALUES (?, ?, ?)",
                       (site, username, encrypted_pass))
        conn.commit()
        conn.close()

    def get_all_passwords(self):
        """
        Devuelve una lista de diccionarios con las contraseñas DESENCRIPTADAS.
        Formato: [{'id': 1, 'site': 'Google', 'user': 'ivan', 'pass': '1234'}, ...]
        """
        if not self.key:
            return []

        f = Fernet(self.key)
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, site, username, encrypted_pass FROM credentials")
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            try:
                decrypted = f.decrypt(row[3].encode()).decode()
                results.append({
                    'id': row[0],
                    'site': row[1],
                    'user': row[2],
                    'password': decrypted
                })
            except Exception:
                # Si falla desencriptar (ej: llave incorrecta), mostramos error
                results.append({
                    'id': row[0],
                    'site': row[1],
                    'user': row[2],
                    'password': "[ERROR: CLAVE MAESTRA INCORRECTA]"
                })
        return results

    def delete_password(self, id_entry):
        """Elimina una entrada por su ID."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM credentials WHERE id = ?", (id_entry,))
        conn.commit()
        conn.close()