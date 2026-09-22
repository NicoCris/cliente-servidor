# 💬 Chat Cliente-Servidor (TCP + SQLite + Multithreading)

Sistema de chat por consola en arquitectura cliente-servidor desarrollado en Python. Implementa comunicación mediante sockets TCP/IP, persistencia de mensajes en SQLite y soporte para múltiples clientes simultáneos utilizando hilos (`threading`).

No requiere librerías externas: utiliza exclusivamente los módulos de la librería estándar de Python.

---

## 🚀 Características

- **Comunicación TCP/IP:** Conexión punto a punto mediante sockets IPv4 (puerto `5000` por defecto).
- **Soporte Multicliente:** Manejo de múltiples clientes en paralelo asignando un hilo independiente (`threading.Thread`) con modo *daemon* a cada conexión.
- **Persistencia en SQLite:** Almacenamiento de cada mensaje recibido con su contenido, fecha/hora y dirección IP del remitente.
- **Sincronización Thread-Safe:** Uso de `threading.Lock` para garantizar la consistencia en lecturas/escrituras concurrentes en la base de datos y en el registro de clientes activos.
- **Respuestas con confirmación:** El servidor acusa recibo del mensaje indicando fecha y hora de recepción.
- **Gestión robusta de errores:** Control de desconexiones abruptas (`ConnectionResetError`), servidor no disponible, puertos ocupados e interrupciones por teclado (`Ctrl+C`).

---

## 🏗️ Arquitectura y Funcionamiento

┌─────────────┐         TCP/IP          ┌─────────────────────────┐
│   Cliente 1 │ ◄──────────────────────►│                         │
└─────────────┘                         │        Servidor         │
│       (server.py)       │
┌─────────────┐         TCP/IP          │                         │
│   Cliente 2 │ ◄──────────────────────►│  + Hilos (threading)   │
└─────────────┘                         │                         │
└────────────┬────────────┘
┌─────────────┐         TCP/IP                       │
│   Cliente N │ ◄──────────────────────►             ▼
└─────────────┘                         ┌─────────────────────────┐
                                        │  Base de Datos (chat.db)│
                                        │  SQLite + db_lock       │
                                        └─────────────────────────┘
1. **Servidor:** Configura el socket TCP, inicializa la tabla en la base de datos y queda a la escucha de nuevas conexiones.
2. **Cliente:** Se conecta a la dirección y puerto del servidor.
3. **Flujo de mensajes:** Por cada cliente conectado, el servidor despacha un hilo (`manejar_cliente`). Cuando el cliente envía un texto (UTF-8), el hilo adquiere el lock, guarda el registro en SQLite y devuelve una confirmación.
4. **Desconexión:** Al recibir `/salir` o `éxito`, el cliente y el servidor cierran la conexión de forma ordenada y liberan los recursos
---

## 📁 Estructura del Proyecto

```text

cliente_servidor/
├── config.py       # Configuración central (HOST, PORT, BUFFER_SIZE, ENCODING, DB_NAME)
├── database.py     # Inicialización y operaciones CRUD en SQLite con Lock
├── server.py       # Servidor TCP multihilo y despacho de clientes
├── client.py       # Cliente interactivo de terminal
├── chat.db         # Archivo SQLite (creado automáticamente al iniciar)


📋 Requisitos PreviosPython 3.6 o superior instalado.   No se necesitan dependencias externas (usa socket, threading, sqlite3, etc.).

🛠️ Instalación y Uso.

# 1. Clonar el repositorio

git clone [https://github.com/tu-usuario/tu-repositorio.git](https://github.com/tu-usuario/tu-repositorio.git)

cd tu-repositorio

2. Iniciar el ServidorEn una terminal:

python server.py

El servidor comenzará a escuchar en 127.0.0.1:5000 y creará la base de datos si no existe.

3. Iniciar uno o varios ClientesEn una o más terminales adicionales:

python client.py


4. Enviar Mensajes y Comandos
Acción                Comando / Entrada
Enviar mensaje        Escribe cualquier texto y presiona Enter
Desconectarse         Escribe /salir o éxito
Salida forzada        Presiona Ctrl + C

🗄️ Esquema de Base de DatosEl archivo chat.db almacena los registros bajo la tabla mensajes:

SQLCREATE TABLE IF NOT EXISTS mensajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contenido TEXT NOT NULL,
    fecha_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_cliente TEXT NOT NULL
);

Consultar los mensajes almacenados
Podes verificar el contenido de la base de datos directamente desde la terminal:

python -c "import sqlite3; conn = sqlite3.connect('chat.db'); c = conn.cursor(); c.execute('SELECT * FROM mensajes'); [print(r) for r in c.fetchall()]; conn.close()"

⚙️ ConfiguraciónPuedes modificar las opciones de red y almacenamiento en config.py:

PythonHOST = "127.0.0.1"    # Dirección de escucha
PORT = 5000           # Puerto TCP
BUFFER_SIZE = 1024    # Tamaño máximo de buffer de lectura
ENCODING = "utf-8"    # Codificación de caracteres
DB_NAME = "chat.db"   # Nombre del archivo SQLite
