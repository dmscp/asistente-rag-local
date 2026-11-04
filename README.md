# Asistente RAG sobre apuntes de Ciberseguridad
Samuel Correia Pinto · 2º DAM · Programación asistida por IA (T04)

Sistema RAG 100 % local: Python + Ollama (llama3.2:3b y nomic-embed-text) + ChromaDB.

## Instalación (macOS)
1. Instalar Ollama desde https://ollama.com/download y abrirlo (queda en la barra de menús).
2. Descargar los modelos:
   ```bash
   ollama pull llama3.2:3b
   ollama pull nomic-embed-text
   ```
3. Crear el entorno de Python e instalar las librerías:
   ```bash
   cd rag_samuel_correia
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Copiar los PDF de apuntes en la carpeta `documentos/`.

## Uso
| Paso | Comando | Qué hace |
|---|---|---|
| Indexar | `python indexar.py` | Carga, trocea (300 y 1000 caracteres), calcula embeddings y crea las colecciones |
| Buscar | `python buscar.py "pregunta" --tam 1000` | Muestra los fragmentos recuperados y su similitud |
| Preguntar | `python preguntar.py "pregunta"` | Respuesta con RAG (`--sin-rag` para el modelo solo, `--ver-prompt` para ver el prompt) |
| Chat | `python chat.py` | Asistente en consola (`/sinrag`, `/rag`, `/tam 300`, `/salir`) |
| Evaluar | `python evaluar.py` | Lanza las 12 preguntas de `preguntas.json` y genera `resultados.csv` |

## Ficheros
- `config.py`: modelos, carpetas, top-k y tamaños de fragmento.
- `rag.py`: funciones de carga, troceado, embeddings, búsqueda y generación, y la plantilla de prompt.
- `preguntas.json`: las 12 preguntas de evaluación con su respuesta correcta y la página donde está.
