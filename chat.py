"""Paso 6: asistente en consola.  Comandos: /sinrag, /rag, /tam 300, /tam 1000, /salir"""
import config
import rag

rag.cabecera("ASISTENTE DE APUNTES DE CIBERSEGURIDAD (RAG)")
print("Escribe tu pregunta. Comandos: /rag  /sinrag  /tam 300  /tam 1000  /salir\n")
usar_rag, tam = True, config.TAM_POR_DEFECTO
while True:
    try:
        entrada = input(f"[{'RAG ' + str(tam) if usar_rag else 'SIN RAG'}] Tú > ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if not entrada:
        continue
    if entrada == "/salir":
        break
    if entrada in ("/rag", "/sinrag"):
        usar_rag = entrada == "/rag"
        continue
    if entrada.startswith("/tam"):
        try:
            nuevo = int(entrada.split()[1])
            if nuevo in config.TAMANOS:
                tam = nuevo
            else:
                print(f"Tamaños disponibles: {list(config.TAMANOS)}")
        except (IndexError, ValueError):
            print("Uso: /tam 300")
        continue
    if usar_rag:
        respuesta, fragmentos = rag.responder_con_rag(entrada, tam)
        print(f"Asistente > {respuesta}")
        print("   fuentes: " + ", ".join(f"{f['doc']} p.{f['pagina']}" for f in fragmentos) + "\n")
    else:
        print(f"Asistente > {rag.responder_sin_rag(entrada)}\n")
print("¡Hasta luego!")
