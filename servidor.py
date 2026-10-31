"""PFO3: servidor TCP que recibe solicitudes JSON y las asigna a workers.

Implementación local de la parte funcional. El diagrama presenta la arquitectura
objetivo con balanceador, RabbitMQ y almacenamiento distribuido, que aquí no se
instalan ni se simulan como servicios reales.
"""

import json
import logging
import socketserver
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

HOST = "127.0.0.1"  # Solo conexiones locales durante las pruebas.
PUERTO = 12345
CANTIDAD_WORKERS = 4
MAX_BYTES = 8192

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(threadName)s | %(message)s",
    datefmt="%H:%M:%S",
)


def procesar_tarea(solicitud):
    """Esta función se ejecuta dentro de un worker del pool."""
    if not isinstance(solicitud, dict):
        raise ValueError("La solicitud debe ser un objeto JSON.")

    operacion = solicitud.get("operacion")
    dato = solicitud.get("dato")
    worker = threading.current_thread().name
    logging.info("Worker procesa operación: %s", operacion)

    if operacion == "sumar":
        if not isinstance(dato, list) or not dato:
            raise ValueError("Para sumar, 'dato' debe ser una lista no vacía.")
        if any(type(numero) not in (int, float) for numero in dato):
            raise ValueError("La lista debe contener solamente números.")
        resultado = sum(dato)    
    elif operacion == "mayusculas":
        if not isinstance(dato, str):
            raise ValueError("Para mayúsculas, 'dato' debe ser texto.")
        resultado = dato.upper()    
    elif operacion == "contar_palabras":
        if not isinstance(dato, str):
            raise ValueError("Para contar palabras, 'dato' debe ser texto.")
        resultado = sum(
            1 for elemento in dato.split()
            if any(caracter.isalpha() for caracter in elemento)
        )       
    elif operacion == "invertir":
        if not isinstance(dato, str):
            raise ValueError("Para invertir, 'dato' debe ser texto.")
        resultado = dato[::-1]    
    elif operacion == "simular":
        # Solo para verificar concurrencia durante las pruebas.
        if type(dato) not in (int, float) or not 0 <= dato <= 3:
            raise ValueError("Para simular, 'dato' debe estar entre 0 y 3 segundos.")
        time.sleep(dato)
        resultado = f"Tarea completada después de {dato} segundos"
    else:
        raise ValueError("Operación desconocida.")

    return {"ok": True, "resultado": resultado, "worker": worker}


class ManejadorCliente(socketserver.StreamRequestHandler):
    """Cada conexión recibe una solicitud y devuelve una respuesta JSON."""

    def handle(self):
        self.request.settimeout(10)
        respuesta = None
        try:
            linea = self.rfile.readline(MAX_BYTES + 1)
            if not linea or len(linea) > MAX_BYTES or not linea.endswith(b"\n"):
                raise ValueError("Solicitud vacía, demasiado larga o sin terminador de línea.")
            solicitud = json.loads(linea.decode("utf-8"))
            futuro = self.server.pool.submit(procesar_tarea, solicitud)
            respuesta = futuro.result(timeout=8)
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
            respuesta = {"ok": False, "error": str(error)}
        except (TimeoutError, FutureTimeout):
            respuesta = {"ok": False, "error": "Tiempo de espera agotado."}
        except Exception:
            logging.exception("Error inesperado procesando solicitud")
            respuesta = {"ok": False, "error": "Error interno del servidor."}

        try:
            mensaje = (json.dumps(respuesta, ensure_ascii=False) + "\n").encode("utf-8")
            self.wfile.write(mensaje)
            self.wfile.flush()
        except (OSError, TimeoutError):
            logging.warning("No se pudo enviar la respuesta al cliente.")


class ServidorTCP(socketserver.ThreadingTCPServer):
    """Atiende varias conexiones y comparte el pool de workers."""
    allow_reuse_address = True
    daemon_threads = True


def main():
    with ThreadPoolExecutor(max_workers=CANTIDAD_WORKERS, thread_name_prefix="Worker") as pool:
        with ServidorTCP((HOST, PUERTO), ManejadorCliente) as servidor:
            servidor.pool = pool
            logging.info("Servidor TCP escuchando en %s:%s", HOST, PUERTO)
            logging.info("Pool preparado con %s workers.", CANTIDAD_WORKERS)
            logging.info("Detener con Ctrl+C.")
            try:
                servidor.serve_forever(poll_interval=0.2)
            except KeyboardInterrupt:
                logging.info("Servidor detenido por el usuario.")


if __name__ == "__main__":
    main()
