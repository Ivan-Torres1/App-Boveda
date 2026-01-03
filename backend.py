
import sqlite3
import hashlib
import base64
import shutil
import os
from datetime import datetime
from cryptography.fernet import Fernet

class PasswordManagerLogic:
    def __init__(self, db_name="mis_claves.db"):
        self.db_name = db_name
        self.key = None
        self._init_db()

    def _init_db(self):
        """Inicializa las tablas necesarias."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Tabla para validar si la contraseña maestra es correcta
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_check (
                id INTEGER PRIMARY KEY,
                check_phrase TEXT NOT NULL
            )
        ''')
        
        # Tabla de credenciales (SIN usuario, solo sitio y pass)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT NOT NULL,
                encrypted_pass TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def login(self, master_password):
        """
        Intenta loguear. 
        Retorna (True, "Mensaje") si es exitoso.
        Retorna (False, "Error") si falla.
        """
        # 1. Generar la llave candidata
        k = hashlib.sha256(master_password.encode()).digest()
        key_candidate = base64.urlsafe_b64encode(k)
        f = Fernet(key_candidate)

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # 2. Verificar si es la primera vez (Setup)
        cursor.execute("SELECT check_phrase FROM security_check WHERE id = 1")
        row = cursor.fetchone()
        
        if row is None:
            # Es una base de datos nueva. Configuramos esta contraseña como la Maestra.
            encrypted_check = f.encrypt(b"VALID").decode()
            cursor.execute("INSERT INTO security_check (id, check_phrase) VALUES (1, ?)", (encrypted_check,))
            conn.commit()
            conn.close()
            self.key = key_candidate
            return True, "Base de datos creada. ¡Bienvenido!"
        
        else:
            # Ya existe una contraseña. Verificamos si la llave actual puede abrir el cerrojo.
            try:
                encrypted_check = row[0]
                decrypted_check = f.decrypt(encrypted_check.encode()).decode()
                
                if decrypted_check == "VALID":
                    self.key = key_candidate
                    conn.close()
                    return True, "Login exitoso"
            except Exception:
                conn.close()
                return False, "Contraseña incorrecta. Acceso denegado."
            
        return False, "Error desconocido"

    def add_password(self, site, password):
        """Guarda solo sitio y contraseña."""
        if not self.key: raise Exception("Bóveda bloqueada.")
        
        f = Fernet(self.key)
        encrypted_pass = f.encrypt(password.encode()).decode()
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO credentials (site, encrypted_pass) VALUES (?, ?)",
                       (site, encrypted_pass))
        conn.commit()
        conn.close()

    def get_all_passwords(self):
        if not self.key: return []

        f = Fernet(self.key)
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, site, encrypted_pass FROM credentials")
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            try:
                decrypted = f.decrypt(row[2].encode()).decode()
                results.append({
                    'id': row[0],
                    'site': row[1],
                    'password': decrypted
                })
            except:
                results.append({'id': row[0], 'site': row[1], 'password': "Error"})
        return results

    def delete_password(self, id_entry):
        if not self.key: return # Doble seguridad
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM credentials WHERE id = ?", (id_entry,))
        conn.commit()
        conn.close()

    def create_backup(self, target_folder):
        """Crea una copia del archivo .db en la carpeta seleccionada"""
        if not os.path.exists(self.db_name):
            return False, "No hay base de datos para respaldar"
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_claves_{timestamp}.db"
        target_path = os.path.join(target_folder, backup_name)
        
        try:
            shutil.copy2(self.db_name, target_path)
            return True, f"Backup guardado en: {target_path}"
        except Exception as e:
            return False, str(e)