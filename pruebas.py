"""Pruebas automatizadas sin paquetes externos para el PFO3."""

from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
from cliente import enviar_tarea


def comprobar(nombre, operacion, dato, esperado):
    respuesta = enviar_tarea(operacion, dato)
    assert respuesta["ok"], respuesta
    assert respuesta["resultado"] == esperado, (nombre, respuesta)
    print(f"OK | {nombre}: {respuesta['resultado']} | {respuesta['worker']}")


def main():
    comprobar("Suma", "sumar", [2, 3, 5], 10)
    comprobar("Mayúsculas", "mayusculas", "hola red", "HOLA RED")
    comprobar("Contar palabras", "contar_palabras", "hola desde el cliente", 4)
    comprobar("Invertir texto", "invertir", "red", "der")

    respuesta_error = enviar_tarea("operacion_inexistente", "x")
    assert not respuesta_error["ok"]
    print("OK | Solicitud inválida rechazada:", respuesta_error["error"])

    # Se envían 8 tareas en paralelo: con 4 workers el tiempo esperado
    # ronda 2 segundos (más un pequeño margen), no 8 segundos.
    inicio = perf_counter()
    with ThreadPoolExecutor(max_workers=8) as clientes:
        respuestas = list(clientes.map(lambda _: enviar_tarea("simular", 1), range(8)))
    tiempo = perf_counter() - inicio
    assert len(respuestas) == 8
    assert all(respuesta["ok"] for respuesta in respuestas), respuestas
    workers = {respuesta["worker"] for respuesta in respuestas}
    assert len(workers) >= 2, workers
    assert tiempo < 7, f"Las tareas tardaron demasiado: {tiempo:.2f} s"
    print(f"OK | 8 solicitudes concurrentes atendidas en {tiempo:.2f} s")
    print("Workers utilizados:", ", ".join(sorted(workers)))
    print("\nTODAS LAS PRUEBAS PASARON.")


if __name__ == "__main__":
    main()
