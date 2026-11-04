"""Paso 5: responde a una pregunta con RAG o sin RAG.
Uso:  python preguntar.py "pregunta"            (con RAG)
      python preguntar.py "pregunta" --sin-rag  (solo el modelo)
      python preguntar.py "pregunta" --ver-prompt"""
import argparse
import time

import config
import rag

parser = argparse.ArgumentParser()
parser.add_argument("pregunta")
parser.add_argument("--sin-rag", action="store_true")
parser.add_argument("--tam", type=int, default=config.TAM_POR_DEFECTO, choices=list(config.TAMANOS))
parser.add_argument("--ver-prompt", action="store_true", help="muestra el prompt completo enviado al modelo")
args = parser.parse_args()

modo = "SIN RAG" if args.sin_rag else f"CON RAG ({args.tam} caracteres)"
rag.cabecera(f"PREGUNTA {modo} · modelo {config.MODELO_LLM}")
print(f"\nPregunta: {args.pregunta}\n")
t0 = time.time()
if args.sin_rag:
    respuesta = rag.responder_sin_rag(args.pregunta)
else:
    fragmentos = rag.buscar(args.pregunta, args.tam)
    prompt = rag.construir_prompt(args.pregunta, fragmentos)
    if args.ver_prompt:
        print("----- PROMPT ENVIADO -----\n" + prompt + "\n--------------------------\n")
    respuesta = rag.generar(prompt)
    print("Fuentes recuperadas: " + ", ".join(f"{f['doc']} p.{f['pagina']} ({f['similitud']:.2f})" for f in fragmentos))
print(f"\nRespuesta:\n{respuesta}\n\n(tiempo: {time.time() - t0:.1f} s)")
