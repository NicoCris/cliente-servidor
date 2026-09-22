# ============================================================
# server.py - Socket servidor TCP con SQLite y Multithreading
# Permite múltiples clientes conectados en paralelo
# ============================================================

import socket
import threading
from datetime import datetime
from database import init_db, guardar_mensaje
from config import HOST, PORT, BUFFER_SIZE, ENCODING


# Lista para mantener registro de clientes activos (thread-safe con Lock)
clientes_activos = []
clientes_lock = threading.Lock()

# Flag para indicar que el servidor se está deteniendo
servidor_deteniendo = False


def cerrar_todos_los_clientes():
    """
    Cierra todas las conexiones activas de clientes de forma ordenada.
    Recorre la lista de clientes activos y cierra cada conexión.
    """
    global clientes_activos

    print("\n[APAGADO] Cerrando conexiones de clientes activos...")

    # Obtener una copia de la lista para iterar de forma segura
    with clientes_lock:
        clientes_copia = clientes_activos.copy()

    if not clientes_copia:
        print("[APAGADO] No hay clientes activos para cerrar.")
        return

    # Cerrar cada conexión de cliente
    for cliente in clientes_copia:
        try:
            conn = cliente['conexion']
            ip = cliente['ip']
            puerto = cliente.get('puerto', 'N/A')

            # Enviar mensaje de cierre al cliente antes de cerrar
            try:
                mensaje_cierre = "[SERVIDOR]: El servidor se está apagando. Desconectado."
                conn.sendall(mensaje_cierre.encode(ENCODING))
            except (ConnectionResetError, BrokenPipeError, OSError):
                pass  # La conexión ya puede estar cerrada

            # Cerrar la conexión del socket
            conn.close()
            print(f"[APAGADO] Conexión con {ip}:{puerto} cerrada.")

        except Exception as e:
            print(f"[APAGADO] Error cerrando cliente: {e}")

    # Limpiar la lista de clientes activos
    with clientes_lock:
        clientes_activos.clear()

    print(f"[APAGADO] Todas las conexiones de clientes cerradas.")


def inicializar_socket():
    """
    Inicializa y configura el socket TCP del servidor.

    Returns:
        socket: El socket configurado y listo para escuchar conexiones.
    """
    try:
        # Crear socket TCP/IP (IPv4, SOCK_STREAM = TCP)
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Permitir reutilizar el puerto inmediatamente tras un reinicio
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Asociar el socket a la dirección y puerto
        servidor.bind((HOST, PORT))

        # Escuchar conexiones entrantes (máximo 5 en la cola)
        servidor.listen(5)

        print(f"[SERVIDOR] Escuchando en {HOST}:{PORT}...")
        print("[SERVIDOR] Esperando conexiones de clientes...")
        print("[SERVIDOR] Presiona Ctrl+C para detener el servidor.\n")

        return servidor

    except OSError as e:
        print(f"[ERROR] No se pudo iniciar el servidor en {HOST}:{PORT}")
        print(f"[ERROR] Detalle: {e}")
        raise


def aceptar_conexiones(servidor):
    """
    Acepta conexiones de clientes y crea un hilo independiente para cada uno.
    Permite ejecutar funciones concurrentemente en múltiples hilos.

    Args:
        servidor: El socket del servidor ya inicializado.
    """
    global servidor_deteniendo

    try:
        while not servidor_deteniendo:
            # Aceptar una nueva conexión de cliente
            conn, addr = servidor.accept()
            ip_cliente = addr[0]
            puerto_cliente = addr[1]

            print(f"[CONEXIÓN] Cliente conectado desde {ip_cliente}:{puerto_cliente}")

            # Crear un hilo nuevo para manejar este cliente
            hilo = threading.Thread(
                target=manejar_cliente,
                args=(conn, ip_cliente, puerto_cliente),
                daemon=True  # Hilo daemon: se cierra automáticamente si el programa principal termina
            )
            hilo.start()

            # Registrar el cliente activo (thread-safe)
            with clientes_lock:
                clientes_activos.append({
                    'thread': hilo,
                    'ip': ip_cliente,
                    'puerto': puerto_cliente,
                    'conexion': conn
                })
                print(f"[HILOS] Clientes activos: {len(clientes_activos)}")

    except KeyboardInterrupt:
        print("\n[SERVIDOR] Señal de interrupción recibida (Ctrl+C)...")
        servidor_deteniendo = True

    finally:
        # Cerrar todas las conexiones de clientes antes de cerrar el servidor
        cerrar_todos_los_clientes()

        # Cerrar el socket del servidor
        servidor.close()
        print("[SERVIDOR] Socket del servidor cerrado.")
        print("[SERVIDOR] Servidor detenido correctamente.")


def manejar_cliente(conn, ip_cliente, puerto_cliente):
    """
    Maneja la comunicación con un cliente conectado en su propio hilo.
    Cada cliente tiene su propia conexión y hilo de ejecución.

    Args:
        conn: Socket de conexión con el cliente.
        ip_cliente: Dirección IP del cliente.
        puerto_cliente: Puerto del cliente.
    """
    hilo_actual = threading.current_thread()
    print(f"[HILO] Hilo {hilo_actual.name} iniciado para cliente {ip_cliente}:{puerto_cliente}")

    try:
        while not servidor_deteniendo:
            # Recibir datos del cliente
            data = conn.recv(BUFFER_SIZE)

            # Si no hay datos, el cliente se desconectó
            if not data:
                print(f"[DESCONEXIÓN] Cliente {ip_cliente}:{puerto_cliente} se desconectó.")
                break

            # Decodificar el mensaje recibido
            mensaje = data.decode(ENCODING).strip()

            # Ignorar mensajes vacíos
            if not mensaje:
                continue

            # Guardar el mensaje en la base de datos (thread-safe con Lock)
            mensaje_id = guardar_mensaje(mensaje, ip_cliente)

            # Generar timestamp para la respuesta
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Preparar y enviar respuesta al cliente
            respuesta = f"[SERVIDOR]: Mensaje recibido: {timestamp}"
            conn.sendall(respuesta.encode(ENCODING))

            print(f"[MENSAJE #{mensaje_id}] De {ip_cliente}:{puerto_cliente} : {mensaje}")

    except ConnectionResetError:
        print(f"[ERROR] Conexión reseteada por el cliente {ip_cliente}:{puerto_cliente}.")
    except ConnectionAbortedError:
        print(f"[ERROR] Conexión abortada por el cliente {ip_cliente}:{puerto_cliente}.")
        # Socket cerrado durante operación (servidor apagándose)
    except Exception as e:
        if not servidor_deteniendo:
            print(f"[ERROR] Error inesperado con el cliente {ip_cliente}:{puerto_cliente}: {e}")
    finally:
        # Remover cliente de la lista de activos (thread-safe)
        with clientes_lock:
            clientes_activos[:] = [c for c in clientes_activos if c['ip'] != ip_cliente or c.get('puerto') != puerto_cliente]

        # Cerrar la conexión si aún está abierta
        try:
            conn.close()
        except OSError:
            pass

        print(f"[HILO] Hilo {hilo_actual.name} finalizado. Conexión con {ip_cliente}:{puerto_cliente} cerrada.")
        print(f"[HILOS] Clientes activos restantes: {len(clientes_activos)}")


def main():
    """
    Función principal del servidor.
    """
    global servidor_deteniendo

    print("=" * 60)
    print("   SERVIDOR DE CHAT - SOCKETS TCP CON SQLITE Y MULTITHREADING")
    print("=" * 60)

    # Inicializar la base de datos
    print("\n[INICIO] Inicializando base de datos...")
    init_db()

    # Inicializar el socket del servidor
    print("[INICIO] Inicializando socket del servidor...\n")
    servidor = inicializar_socket()

    # Iniciar el loop de aceptar conexiones
    aceptar_conexiones(servidor)


if __name__ == "__main__":
    main()
