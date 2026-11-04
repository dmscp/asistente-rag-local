# Configuración del proyecto RAG · Samuel Correia Pinto · 2º DAM
MODELO_LLM = "llama3.2:3b"          # modelo que genera las respuestas
MODELO_EMB = "nomic-embed-text"     # modelo que crea los embeddings
CARPETA_DOCS = "documentos"         # aquí van los PDF de apuntes
CARPETA_BD = "bd_chroma"            # aquí ChromaDB guarda la base de datos
TOP_K = 4                           # nº de fragmentos que se recuperan por pregunta

# Tamaños de fragmento para el experimento (caracteres) y su solapamiento (10 %)
TAMANOS = {300: 30, 1000: 100}
TAM_POR_DEFECTO = 1000
