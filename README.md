# Aplicación Flask con tareas I/O-bound concurrentes

## Requisitos
- Python 3.10 o superior  
- Librerías necesarias:
  ```bash
  pip install flask requests
  ```

---

## Ejecución

1. Asegúrate de tener un archivo llamado `data2.txt` en el mismo directorio.
2. Ejecuta el programa:
   ```bash
   python app.py
   ```
3. Abre tu navegador en:
   - `http://127.0.0.1:5000/` → Ejecuta las peticiones HTTP concurrentes.  
   - `http://127.0.0.1:5000/zen` → Devuelve un mensaje del API de GitHub.

---

## Estructura del código

| Sección | Descripción |
|----------|--------------|
| **Lectura de archivo** | Lee `data2.txt`, muestra cantidad de caracteres y líneas (operación I/O-bound). |
| **Peticiones HTTP** | Se definen varias URLs que se consultan con `requests`. |
| **Backoff exponencial** | Si una petición falla, se reintenta hasta 3 veces con tiempos crecientes: 0.5s, 1s, 2s. |
| **ThreadPoolExecutor** | Ejecuta peticiones simultáneamente (`max_workers=3`, razonable para tareas I/O-bound). |
| **as_completed()** | Procesa resultados conforme se completan, sin esperar a que terminen todas. |
| **Flask endpoints** | `/` ejecuta las peticiones concurrentes; `/zen` consulta la API de GitHub. |

---

