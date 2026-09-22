# ============================================================
# database.py - Inicialización y funciones CRUD de SQLite
# Soporte para multithreading con Lock para acceso seguro
# ============================================================

import sqlite3
import threading
from config import DB_NAME

# Lock para sincronizar acceso a la base de datos entre hilos
# Según documentación de Python: threading.Lock protege secciones críticas
db_lock = threading.Lock()


def init_db():
    """
    Inicializa la base de datos y crea la tabla 'mensajes' si no existe.
    Usa un gestor de contexto para manejar la conexión de forma segura.
    """
    try:
        # Conexión a la base de datos SQLite (se crea si no existe)
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()

            # Crear tabla 'mensajes' con los campos requeridos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mensajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contenido TEXT NOT NULL,
                    fecha_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ip_cliente TEXT NOT NULL
                )
            ''')

            # Confirmar los cambios
            conn.commit()
            print("[DATABASE] Tabla 'mensajes' inicializada correctamente.")

    except sqlite3.Error as e:
        print(f"[DATABASE] Error al inicializar la base de datos: {e}")
        raise


def guardar_mensaje(contenido: str, ip_cliente: str) -> int:
    """
    Guarda un mensaje en la base de datos de forma thread-safe.
    Usa un Lock para sincronizar el acceso concurrente desde múltiples hilos.

    Args:
        contenido (str): El contenido del mensaje.
        ip_cliente (str): La dirección IP del cliente.

    Returns:
        int: El ID del mensaje guardado.
    """
    try:
        # Adquirir el lock antes de acceder a la base de datos
        # Esto asegura que solo un hilo a la vez pueda escribir
        with db_lock:
            # Cada función crea su propia conexión (recomendado para multithreading)
            # según documentación de Context7: check_same_thread=True por defecto
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()

                # Insertar el mensaje con timestamp automático
                cursor.execute(
                    "INSERT INTO mensajes (contenido, ip_cliente) VALUES (?, ?)",
                    (contenido, ip_cliente)
                )

                # Obtener el ID generado
                mensaje_id = cursor.lastrowid
                conn.commit()

                print(f"[DATABASE] Mensaje #{mensaje_id} guardado correctamente.")
                return mensaje_id

    except sqlite3.Error as e:
        print(f"[DATABASE] Error al guardar el mensaje: {e}")
        raise


def obtener_mensajes():
    """
    Obtiene todos los mensajes almacenados en la base de datos de forma thread-safe.

    Returns:
        list: Lista de tuplas con todos los mensajes.
    """
    try:
        # Adquirir el lock para lectura segura
        with db_lock:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM mensajes ORDER BY fecha_envio DESC")
                mensajes = cursor.fetchall()

                return mensajes

    except sqlite3.Error as e:
        print(f"[DATABASE] Error al obtener mensajes: {e}")
        return []


# Inicializar la base de datos al importar el módulo
if __name__ == "__main__":
    init_db()
    print("[DATABASE] Base de datos lista para usar.")
