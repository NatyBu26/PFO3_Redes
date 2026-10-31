"""PFO3: cliente de consola que envía tareas por sockets TCP."""

import json
import socket

HOST = "127.0.0.1"
PUERTO = 12345


def enviar_tarea(operacion, dato):
    """Envía una solicitud JSON (una línea) y espera su respuesta."""
    solicitud = {"operacion": operacion, "dato": dato}
    with socket.create_connection((HOST, PUERTO), timeout=10) as conexion:
        conexion.settimeout(10)
        mensaje = json.dumps(solicitud, ensure_ascii=False) + "\n"
        conexion.sendall(mensaje.encode("utf-8"))
        with conexion.makefile("r", encoding="utf-8") as entrada:
            respuesta = entrada.readline(8193)
            if not respuesta or not respuesta.endswith("\n"):
                raise ConnectionError("El servidor no envió una respuesta completa.")
            return json.loads(respuesta)


def main():
    while True:
        print("\n=== PFO3 - CLIENTE TCP ===")
        print("1. Sumar números")
        print("2. Convertir texto a mayúsculas")
        print("3. Contar palabras")
        print("4. Invertir orden de caracteres")
        print("5. Salir")
        opcion = input("Elegí una opción: ").strip()

        if opcion == "5":
            print("Cliente finalizado.")
            break

        if opcion == "1":
            entrada = input("Ingresá números separados por espacios: ")
            try:
                valores = [float(n) for n in entrada.replace(",", ".").split()]
                if not valores:
                    raise ValueError
            except ValueError:
                print("Ingresá al menos un número válido, separado por espacios.")
                continue
            operacion, dato = "sumar", valores
        elif opcion in ("2", "3", "4"):
            dato = input("Ingresá un texto: ")
            operacion = {"2": "mayusculas", "3": "contar_palabras", "4": "invertir"}[opcion]
        else:
            print("Opción no válida.")
            continue

        try:
            respuesta = enviar_tarea(operacion, dato)
            if respuesta.get("ok"):
                print("Resultado:", respuesta["resultado"])
                print("Procesado por:", respuesta["worker"])
            else:
                print("Error informado por el servidor:", respuesta.get("error"))
        except (OSError, ConnectionError, ValueError, json.JSONDecodeError) as error:
            print("No se pudo completar la solicitud:", error)
            print("Comprobá que el servidor esté ejecutándose en otra terminal.")


if __name__ == "__main__":
    main()
