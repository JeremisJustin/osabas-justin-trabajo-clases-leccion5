import sys
import time
import requests
import logging
import csv
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

# Lectura de archivo

with open("data2.txt", "w", encoding="utf-8") as archivo:
    archivo.write("texto de prueba\nsegunda línea\notra más")

p = sys.argv[1] if len(sys.argv) > 1 else "data2.txt"
with open(p, "r", encoding="utf-8") as f:
    contenido = f.read()
num_str = len(contenido)
num_lines = sum(1 for _ in contenido.splitlines())
print(f"Caracteres: {num_str}\nLíneas: {num_lines}")

#Configuración de logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("registro.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

URLS = [
    "https://httpbin.org/delay/3",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/2",
    "https://api.github.com"
]

#Petición HTTP con timeout, reintentos y backoff exponencial

def fetch(url, reintento=0.5, max_intentos=3):
    for i in range(max_intentos):
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            return url, r.status_code, r.elapsed.total_seconds()
        except Exception as e:
            if i == max_intentos - 1:
                logging.warning(f"Fallo final {url}: {e}")
                return url, f"ERROR: {e.__class__.__name__}", 0
            time.sleep(reintento * (2 ** i))  # Espera 0.5, 1, 2 segundos
            logging.info(f"Reintentando {url} (intento {i+2})...")

#Ejecución concurrente con ThreadPoolExecutor y as_completed

def ejecutar_peticiones():
    resultados = []
    # Los max_workers=3 son de esa capacidad por la tarea que realizan
    with ThreadPoolExecutor(max_workers=3) as ex:
        futuros = [ex.submit(fetch, u) for u in URLS]
        for futuro in as_completed(futuros):
            url, status, tiempo = futuro.result()
            logging.info(f"{url} → {status} ({tiempo:.2f}s)")
            resultados.append({"url": url, "status": status, "tiempo": tiempo})

    # Guarda resultados en CSV (reporte)
    with open("reporte.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["url", "status", "tiempo"])
        w.writeheader()
        w.writerows(resultados)
    logging.info("Reporte generado: reporte.csv")
    return resultados

#Endpoints Flask
@app.get("/")
def inicio():
    datos = ejecutar_peticiones()
    return jsonify(resultados=datos)

@app.get("/zen")
def peticion_inicio():
    try:
        r = requests.get("https://api.github.com/zen", timeout=5)
        r.raise_for_status()
        return jsonify(zen=r.text)
    except requests.exceptions.RequestException as e:
        return jsonify(error=str(e)), 500


if __name__ == "__main__":
    app.run(debug=True)
