# App-Boveda
Necesitaba una aplicación para guardar mis contraseñas, la cree yo mismo.

🔐Gestor de Contraseñas Seguro🔐
Este proyecto es una aplicación de escritorio robusta y moderna diseñada para la gestión local de credenciales. El objetivo principal es ofrecer una alternativa privada y segura a los gestores en la nube, manteniendo el control total de los datos en el equipo del usuario.

🚀 Características Principales
Cifrado de Grado Militar: Implementación de cifrado simétrico AES a través de la librería cryptography.

Arquitectura Local-First: Uso de SQLite para persistencia de datos sin necesidad de servidores externos.

Interfaz Moderna (UI/UX): Construida con CustomTkinter, ofreciendo una experiencia de usuario fluida con soporte nativo para modo oscuro.

Seguridad Zero-Knowledge: La "Contraseña Maestra" no se almacena en ninguna parte; se utiliza dinámicamente para derivar la clave de descifrado.

Búsqueda en Tiempo Real: Filtro dinámico de credenciales para un acceso rápido.

🛡️ Arquitectura de Seguridad 🛡️ 
El corazón de la aplicación reside en su lógica de derivación de claves:

Hasing de la Llave: Cuando el usuario ingresa su Contraseña Maestra, el sistema utiliza un algoritmo SHA-256 para generar un hash único de 32 bytes.

Cifrado Fernet: Este hash se utiliza como base para inicializar el protocolo Fernet (AES).

Persistencia: Los datos se guardan en formato BLOB dentro de la base de datos SQLite, lo que significa que incluso si alguien roba el archivo .db, solo verá cadenas de texto cifradas e ilegibles.

💻 Instalación y Uso
Clona el repositorio.

Instala las dependencias: pip install customtkinter cryptography pyperclip.

Ejecuta python main.py.

Define tu Contraseña Maestra.
