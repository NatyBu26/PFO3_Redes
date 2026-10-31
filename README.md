# PFO3 – Rediseño como Sistema Distribuido (Cliente-Servidor)

**Materia:** Programación sobre Redes – IFTS N.º 29  
**Propuesta Formativa Obligatoria 3**

## 1. Objetivo

Diseñar una arquitectura distribuida de tipo cliente-servidor y desarrollar en Python un prototipo funcional que reciba tareas mediante **sockets TCP**, las distribuya entre **workers** de un pool de hilos y devuelva los resultados al cliente.

La entrega diferencia dos alcances:

- **Diseño de arquitectura distribuida:** diagrama con los componentes indicados por la consigna.
- **Implementación local:** servidor TCP, cliente de consola y cuatro workers en Python, ejecutados y probados en una computadora.

## 2. Relación con el PFO2

En el PFO2 se desarrolló un servidor con API HTTP mediante Flask, SQLite y un cliente de consola. El PFO3 retoma el modelo cliente-servidor, pero utiliza **sockets TCP** para transmitir tareas y un **pool de hilos** para procesarlas concurrentemente.

No se reutilizan la autenticación, la API Flask ni la base de datos SQLite del PFO2 en esta implementación, porque el foco de la nueva consigna es la recepción y distribución de tareas por sockets.

[Repositorio del PFO2](https://github.com/NatyBu26/PFO2_Redes)

## 3. Archivos del proyecto

```text
PFO3_Redes/
├── servidor.py
├── cliente.py
├── pruebas.py
├── README.md
├── requirements.txt
├── .gitignore
└── docs/
    ├── diagrama_arquitectura.png
    ├── diagrama_arquitectura.mmd  (si se guarda el código de Mermaid)
    ├── PFO3_Documentacion_de_pruebas.pdf
    └── capturas/
        ├── 01_servidor_iniciado.png
        ├── 02_cliente_iniciado.png
        ├── ...
        └── 11_nombre_operacion_corregido.png
```

- **`servidor.py`:** servidor TCP que recibe solicitudes JSON, valida datos, distribuye tareas mediante `ThreadPoolExecutor` y registra la actividad.
- **`cliente.py`:** menú de consola para enviar tareas y presentar los resultados recibidos.
- **`pruebas.py`:** comprobaciones automáticas de operaciones, rechazo de una operación desconocida y procesamiento concurrente.
- **`requirements.txt`:** indica que solo se usa la biblioteca estándar de Python.
- **`docs/`:** contiene el diagrama y la documentación de las pruebas.

## 4. Diseño de la arquitectura distribuida

El diagrama fue elaborado en **Mermaid** y representa una **arquitectura propuesta**, con los elementos solicitados en la consigna:

1. **Clientes web y móviles:** origen de las solicitudes.
2. **Balanceador de carga (Nginx o HAProxy):** distribuye las conexiones entre servidores receptores.
3. **Servidores receptores:** reciben las tareas y las publican en la cola.
4. **RabbitMQ – Cola de tareas:** desacopla la recepción de solicitudes del procesamiento.
5. **Servidores workers con pool de hilos:** consumen y procesan las tareas.
6. **PostgreSQL y S3:** representan el almacenamiento de datos estructurados y archivos.
7. **RabbitMQ – Cola de resultados:** representa el retorno de resultados hacia el receptor, que responde al cliente correspondiente.

**[Ver diagrama de arquitectura](docs/diagrama_arquitectura.png)**

> **Alcance:** el diagrama muestra el diseño completo. En el prototipo local **no están implementados** Nginx/HAProxy, RabbitMQ, PostgreSQL ni S3, ni existen clientes web o móviles reales. El prototipo implementa un servidor TCP en Python con un pool local de cuatro workers y un cliente de consola.

## 5. Requisitos y ejecución

- Windows, Linux o macOS con **Python 3.10 o superior**.
- No requiere paquetes externos de `pip`.
- Para las pruebas locales se utiliza `127.0.0.1:12345`.

Abrir la carpeta del proyecto en Visual Studio Code o en una terminal.

**Primera terminal: iniciar el servidor**

```powershell
python servidor.py
```

El servidor informa que está escuchando en `127.0.0.1:12345` y que tiene preparado un pool de **4 workers**. Dejar esta terminal abierta.

**Segunda terminal: iniciar el cliente**

```powershell
python cliente.py
```

El menú permite:

1. Sumar números.
2. Convertir texto a mayúsculas.
3. Contar palabras.
4. Invertir orden de caracteres.
5. Salir.

Para cerrar el cliente, elegir **5**. Para detener el servidor, utilizar **Ctrl + C**. Si el comando `python` no funciona en Windows, probar `py`.

## 6. Protocolo de comunicación

El cliente envía una solicitud en formato **JSON**, codificada en UTF-8 y terminada con un salto de línea (`\n`). Por ejemplo:

```json
{"operacion":"sumar","dato":[4,7,3,8]}
```

El servidor responde con otra línea JSON:

```json
{"ok":true,"resultado":22,"worker":"Worker_0"}
```

El identificador del worker puede variar según la ejecución. Las solicitudes inválidas reciben una respuesta con `"ok":false` y un mensaje de error.

El servidor de práctica escucha únicamente en la interfaz local. **No debe exponerse directamente a internet** sin controles adicionales de autenticación, cifrado y seguridad.

## 7. Pruebas realizadas

Se ejecutaron pruebas manuales en el cliente y se verificaron los registros del servidor:

- **Suma:** `4 + 7 + 3 + 8` → `22.0`.
- **Mayúsculas:** transformación de una frase de Blaise Pascal.
- **Conteo de palabras:** frase sobre Charles Babbage y Ada Lovelace.
- **Inversión del orden de caracteres:** frase sobre Grace Hopper.

Para ejecutar las pruebas automáticas, **con el servidor iniciado**, abrir otra terminal:

```powershell
python pruebas.py
```

El script verifica las operaciones básicas, el rechazo de una operación desconocida y el envío de **8 solicitudes concurrentes**. En la ejecución documentada, se registraron **2,01 segundos** y participaron `Worker_0`, `Worker_1`, `Worker_2` y `Worker_3`. El tiempo puede variar de una computadora a otra.

La salida final registrada fue: **`TODAS LAS PRUEBAS PASARON.`**

## 8. Mejoras identificadas durante las pruebas

Las pruebas manuales permitieron identificar dos oportunidades de mejora que se incorporaron y verificaron nuevamente:

**8.1. Conteo de palabras**

- **Antes:** el conteo por separación de espacios devolvía **19** al incluir el año `1843` como un elemento.
- **Cambio:** se ajustó el criterio de conteo para considerar elementos que contienen letras y excluir valores compuestos únicamente por números.
- **Después:** la misma frase devolvió **18**.
- **Alcance de la mejora:** es un criterio sencillo y útil para esta prueba; no pretende resolver todos los casos lingüísticos de tokenización.

**8.2. Nombre de la operación de inversión**

- **Antes:** el menú mostraba `Invertir texto`.
- **Cambio:** se reemplazó el texto visible por **`Invertir orden de caracteres`** para describir mejor la operación.
- **Después:** se verificó que el programa continuara devolviendo la secuencia de caracteres en orden inverso.
- **Importante:** se mantuvo el identificador interno `"invertir"`, utilizado por el cliente y el servidor.

Luego de los cambios se ejecutaron nuevamente las pruebas automáticas, con resultado satisfactorio. La corrección del caso `1843` también se comprobó manualmente.

## 9. Evidencias y documentación

La documentación incluye **11 capturas**, con las pruebas iniciales, la concurrencia y la comparación antes/después de las mejoras.

**[Documentación de pruebas en PDF](docs/PFO3_Documentacion_de_pruebas.pdf)**

Las imágenes originales se encuentran en `docs/capturas/`.

## 10. Entregables

La consigna solicita:

- **Diagrama** del sistema distribuido.
- **Código del servidor y cliente** en un repositorio de GitHub.

El archivo `pruebas.py`, las capturas y el PDF de documentación se adjuntan como **evidencias complementarias** del funcionamiento; no se presentan como requisitos obligatorios de la consigna.
