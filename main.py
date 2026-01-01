import customtkinter as ctk
import tkinter.messagebox as msg
import pyperclip  # Librería para el portapapeles
from backend import PasswordManagerLogic # Importamos nuestra lógica

# Configuración inicial de apariencia
ctk.set_appearance_mode("Dark")  # Forzamos modo oscuro para que se vea más 'hacker'
ctk.set_default_color_theme("blue")

class PasswordManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Conexión con el CEREBRO (Backend)
        self.logic = PasswordManagerLogic()

        # Configuración de la ventana principal
        self.title("Bóveda de Contraseñas")
        self.geometry("700x550")
        
        # Variables de estado
        self.login_frame = None
        self.main_frame = None
        
        # Iniciamos
        self.show_login_screen()

    # ------------------------------------------------------------------
    # PANTALLA DE LOGIN
    # ------------------------------------------------------------------
    def show_login_screen(self):
        if self.main_frame:
            self.main_frame.destroy()

        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.login_frame, text="Acceso a la Bóveda", font=("Roboto Medium", 20)).pack(pady=20, padx=50)

        self.entry_password = ctk.CTkEntry(self.login_frame, placeholder_text="Contraseña Maestra", show="*", width=200)
        self.entry_password.pack(pady=10, padx=20)
        # Permitir entrar presionando Enter
        self.entry_password.bind("<Return>", lambda event: self.verify_login())

        ctk.CTkButton(self.login_frame, text="Desencriptar", command=self.verify_login).pack(pady=20, padx=20)

    def verify_login(self):
        password = self.entry_password.get()
        if not password:
            msg.showwarning("Error", "La contraseña no puede estar vacía")
            return

        # Llamamos al backend para generar la llave
        self.logic.login(password)
        
        # Pasamos a la app principal
        self.show_main_app()

    # ------------------------------------------------------------------
    # PANTALLA PRINCIPAL
    # ------------------------------------------------------------------
    def show_main_app(self):
        if self.login_frame:
            self.login_frame.destroy()

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(pady=10, padx=10, fill="both", expand=True)

        self.tab_search = self.tabview.add("Mis Contraseñas")
        self.tab_add = self.tabview.add("Agregar Nueva")

        self.setup_search_tab()
        self.setup_add_tab()

    # --- Lógica de la Pestaña 'Buscar/Ver' ---
    def setup_search_tab(self):
        # Barra de búsqueda
        search_frame = ctk.CTkFrame(self.tab_search, fg_color="transparent")
        search_frame.pack(fill="x", pady=10)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Filtrar por sitio...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        # Búsqueda en tiempo real al escribir
        self.search_entry.bind("<KeyRelease>", lambda event: self.refresh_list(filter_text=self.search_entry.get()))

        ctk.CTkButton(search_frame, text="Refrescar", width=100, command=lambda: self.refresh_list()).pack(side="right")

        # Área de resultados (Scroll)
        self.results_frame = ctk.CTkScrollableFrame(self.tab_search, label_text="Credenciales Descifradas")
        self.results_frame.pack(fill="both", expand=True, pady=10)

        # Cargar datos iniciales
        self.refresh_list()

    def refresh_list(self, filter_text=""):
        # 1. Limpiar la lista visual actual
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # 2. Obtener datos del backend
        credentials = self.logic.get_all_passwords()

        # 3. Crear las filas visuales
        for cred in credentials:
            # Filtro simple (si hay texto en el buscador)
            if filter_text.lower() in cred['site'].lower():
                self.create_row(cred)

    def create_row(self, cred):
        """Crea una fila visual para una credencial"""
        item_frame = ctk.CTkFrame(self.results_frame)
        item_frame.pack(fill="x", pady=5)

        # Icono o Texto del sitio
        ctk.CTkLabel(item_frame, text=cred['site'], font=("Arial", 14, "bold"), width=150, anchor="w").pack(side="left", padx=10)
        
        # Usuario
        ctk.CTkLabel(item_frame, text=cred['user'], text_color="gray").pack(side="left", padx=10)
        
        # Botón Eliminar
        btn_del = ctk.CTkButton(item_frame, text="X", width=30, fg_color="#FF5555", hover_color="#990000",
                                command=lambda id=cred['id']: self.delete_entry(id))
        btn_del.pack(side="right", padx=5)

        # Botón Copiar
        # Usamos lambda para capturar la contraseña específica de esta fila
        btn_copy = ctk.CTkButton(item_frame, text="Copiar Pass", width=80, 
                                 command=lambda p=cred['password']: self.copy_to_clipboard(p))
        btn_copy.pack(side="right", padx=5)

    def copy_to_clipboard(self, password):
        if "ERROR" in password:
            msg.showerror("Error", "No se puede copiar. La clave maestra era incorrecta.")
        else:
            pyperclip.copy(password)
            msg.showinfo("Copiado", "Contraseña copiada al portapapeles")

    def delete_entry(self, id_entry):
        if msg.askyesno("Confirmar", "¿Estás seguro de eliminar esta contraseña?"):
            self.logic.delete_password(id_entry)
            self.refresh_list(self.search_entry.get())

    # --- Lógica de la Pestaña 'Agregar' ---
    def setup_add_tab(self):
        self.tab_add.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.tab_add, text="Sitio Web:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_site = ctk.CTkEntry(self.tab_add, placeholder_text="ej. google.com")
        self.entry_site.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.tab_add, text="Usuario:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_user = ctk.CTkEntry(self.tab_add, placeholder_text="ej. correo@gmail.com")
        self.entry_user.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.tab_add, text="Contraseña:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.entry_new_pass = ctk.CTkEntry(self.tab_add, show="*")
        self.entry_new_pass.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        save_btn = ctk.CTkButton(self.tab_add, text="Guardar y Encriptar", command=self.save_data_logic)
        save_btn.grid(row=3, column=1, padx=10, pady=30, sticky="e")

    def save_data_logic(self):
        site = self.entry_site.get()
        user = self.entry_user.get()
        pwd = self.entry_new_pass.get()

        if site and user and pwd:
            try:
                self.logic.add_password(site, user, pwd)
                msg.showinfo("Éxito", "Contraseña encriptada y guardada.")
                
                # Limpiar campos
                self.entry_site.delete(0, 'end')
                self.entry_user.delete(0, 'end')
                self.entry_new_pass.delete(0, 'end')
                
                # Volver a la pestaña de lista y actualizar
                self.tabview.set("Mis Contraseñas")
                self.refresh_list()
                
            except Exception as e:
                msg.showerror("Error", str(e))
        else:
            msg.showwarning("Faltan datos", "Por favor llena todos los campos.")

if __name__ == "__main__":
    app = PasswordManagerApp()
    app.mainloop()