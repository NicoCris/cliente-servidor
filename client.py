# ============================================================
# client.py - Socket cliente TCP
# ============================================================

import socket
from config import HOST, PORT, BUFFER_SIZE, ENCODING


def inicializar_cliente():
    """
    Inicializa y conecta el socket del cliente al servidor.

    Returns:
        socket: El socket conectado al servidor.
    """
    try:
        # Crear socket TCP/IP (IPv4, SOCK_STREAM = TCP)
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Conectar al servidor
        cliente.connect((HOST, PORT))

        print(f"[CLIENTE] Conectado al servidor {HOST}:{PORT}")
        print("[CLIENTE] Escribí tu mensaje y presioná Enter para enviar.")
        print("[CLIENTE] Escribí '/salir' o 'éxito' para desconectarte.\n")

        return cliente

    except ConnectionRefusedError:
        print(f"[ERROR] No se pudo conectar al servidor {HOST}:{PORT}")
        print("[ERROR] Verificá que el servidor esté ejecutándose.")
        raise
    except OSError as e:
        print(f"[ERROR] Error de conexión: {e}")
        raise


def enviar_mensajes(cliente):
    """
    Envía múltiples mensajes al servidor hasta que el usuario decida salir.

    Args:
        cliente: El socket conectado al servidor.
    """
    try:
        while True:
            # Solicitar mensaje al usuario
            mensaje = input("Tu mensaje: ").strip()

            # Verificar si el usuario quiere salir
            if mensaje.lower() in ["/salir", "éxito", "exito"]:
                print("\n[CLIENTE] Desconectando del servidor...")
                break

            # Ignorar mensajes vacíos
            if not mensaje:
                print("[CLIENTE] El mensaje no puede estar vacío.")
                continue

            try:
                # Enviar el mensaje al servidor
                cliente.sendall(mensaje.encode(ENCODING))

                # Recibir la respuesta del servidor
                respuesta = cliente.recv(BUFFER_SIZE)

                if respuesta:
                    print(f"{respuesta.decode(ENCODING)}\n")
                else:
                    print("[CLIENTE] El servidor cerró la conexión.")
                    break

            except ConnectionResetError:
                print("[ERROR] Conexión perdida con el servidor.")
                break
            except ConnectionAbortedError:
                print("[ERROR] Conexión abortada.")
                break

    except KeyboardInterrupt:
        print("\n[CLIENTE] Interrupción por teclado.")
    finally:
        cliente.close()
        print("[CLIENTE] Conexión cerrada.")


def main():
    """
    Función principal del cliente.
    """
    print("=" * 50)
    print("   CLIENTE DE CHAT - SOCKETS TCP")
    print("=" * 50)
    print()

    # Inicializar y conectar el cliente
    cliente = inicializar_cliente()

    # Iniciar envío de mensajes
    enviar_mensajes(cliente)


if __name__ == "__main__":
    main()
