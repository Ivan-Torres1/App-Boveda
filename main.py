import customtkinter as ctk
import tkinter.messagebox as msg
import pyperclip  
from backend import PasswordManagerLogic 

# Configuración inicial de apariencia
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")

class PasswordManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.logic = PasswordManagerLogic()
        self.title("Bóveda Segura v2")
        self.geometry("700x550")
        
        self.login_frame = None
        self.main_frame = None
        
       
        self.show_login_screen()

   
    def show_login_screen(self):
        if self.main_frame: self.main_frame.destroy()
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.login_frame, text="Acceso a la Bóveda", font=("Roboto Medium", 20)).pack(pady=20, padx=50)

        self.entry_password = ctk.CTkEntry(self.login_frame, placeholder_text="Contraseña Maestra", show="*", width=200)
        self.entry_password.pack(pady=10, padx=20)
        self.entry_password.bind("<Return>", lambda event: self.verify_login())
        
        # Etiqueta para mensajes de error
        self.lbl_error = ctk.CTkLabel(self.login_frame, text="", text_color="red")
        self.lbl_error.pack(pady=5)

        ctk.CTkButton(self.login_frame, text="Desencriptar", command=self.verify_login).pack(pady=20, padx=20)

    def verify_login(self):
        password = self.entry_password.get()
        if not password:
            self.lbl_error.configure(text="Ingresa una contraseña")
            return

        # Intentamos loguear con validación
        success, message = self.logic.login(password)
        
        if success:
            self.show_main_app()
        else:
            # Si falla, mostramos error y NO entramos
            self.lbl_error.configure(text=message)
            self.entry_password.delete(0, 'end') # Limpiamos campo


    def show_main_app(self):
        if self.login_frame: self.login_frame.destroy()
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(pady=10, padx=10, fill="both", expand=True)

        self.tab_search = self.tabview.add("Mis Contraseñas")
        self.tab_add = self.tabview.add("Agregar Nueva")

        self.setup_search_tab()
        self.setup_add_tab()

    def setup_search_tab(self):
        # Header con Buscador y Backup
        top_frame = ctk.CTkFrame(self.tab_search, fg_color="transparent")
        top_frame.pack(fill="x", pady=10)

        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="Filtrar por sitio...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda event: self.refresh_list(self.search_entry.get()))

        # Botón de Backup
        ctk.CTkButton(top_frame, text="Crear Backup", width=100, fg_color="green", 
                      command=self.create_backup_ui).pack(side="right")

        self.results_frame = ctk.CTkScrollableFrame(self.tab_search, label_text="Credenciales")
        self.results_frame.pack(fill="both", expand=True, pady=10)
        self.refresh_list()

    def create_backup_ui(self):
        # Abre ventana para elegir carpeta
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            success, msg_text = self.logic.create_backup(folder_selected)
            if success:
                msg.showinfo("Backup Exitoso", msg_text)
            else:
                msg.showerror("Error", msg_text)

    def refresh_list(self, filter_text=""):
        for widget in self.results_frame.winfo_children(): widget.destroy()
        
        credentials = self.logic.get_all_passwords()
        for cred in credentials:
            if filter_text.lower() in cred['site'].lower():
                self.create_row(cred)

    def create_row(self, cred):
        item_frame = ctk.CTkFrame(self.results_frame)
        item_frame.pack(fill="x", pady=5)

        # Solo mostramos el Sitio (eliminamos usuario)
        ctk.CTkLabel(item_frame, text=cred['site'], font=("Arial", 14, "bold"), width=200, anchor="w").pack(side="left", padx=10)
        
        # Botones
        ctk.CTkButton(item_frame, text="X", width=30, fg_color="#FF5555", hover_color="#990000",
                                command=lambda id=cred['id']: self.delete_entry(id)).pack(side="right", padx=5)
        
        ctk.CTkButton(item_frame, text="Copiar", width=80, 
                                 command=lambda p=cred['password']: self.copy_to_clipboard(p)).pack(side="right", padx=5)

    def copy_to_clipboard(self, password):
        pyperclip.copy(password)
        msg.showinfo("Copiado", "Contraseña copiada al portapapeles")

    def delete_entry(self, id_entry):
        if msg.askyesno("Confirmar", "¿Eliminar esta contraseña?"):
            self.logic.delete_password(id_entry)
            self.refresh_list(self.search_entry.get())

    # --- PESTAÑA AGREGAR (Sin Usuario) ---
    def setup_add_tab(self):
        self.tab_add.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.tab_add, text="Sitio Web:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_site = ctk.CTkEntry(self.tab_add, placeholder_text="ej. Netflix")
        self.entry_site.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.tab_add, text="Contraseña:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_new_pass = ctk.CTkEntry(self.tab_add, show="*")
        self.entry_new_pass.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkButton(self.tab_add, text="Guardar", command=self.save_data_logic).grid(row=2, column=1, padx=10, pady=30, sticky="e")

    def save_data_logic(self):
        site = self.entry_site.get()
        pwd = self.entry_new_pass.get()

        if site and pwd:
            try:
                self.logic.add_password(site, pwd) # Solo 2 argumentos ahora
                msg.showinfo("Éxito", "Guardado.")
                self.entry_site.delete(0, 'end')
                self.entry_new_pass.delete(0, 'end')
                self.tabview.set("Mis Contraseñas")
                self.refresh_list()
            except Exception as e:
                msg.showerror("Error", str(e))
        else:
            msg.showwarning("Faltan datos", "Llena ambos campos.")

if __name__ == "__main__":
    app = PasswordManagerApp()
    app.mainloop()
