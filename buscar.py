"""Paso 4: muestra qué fragmentos recupera la búsqueda y su similitud.
Uso:  python buscar.py "¿Qué es un RPO?" [--tam 300]"""
import argparse

import config
import rag

parser = argparse.ArgumentParser()
parser.add_argument("pregunta")
parser.add_argument("--tam", type=int, default=config.TAM_POR_DEFECTO, choices=list(config.TAMANOS))
args = parser.parse_args()

rag.cabecera(f"RECUPERACIÓN (fragmentos de {args.tam} caracteres, top-{config.TOP_K})")
print(f"\nPregunta: {args.pregunta}\n")
for i, f in enumerate(rag.buscar(args.pregunta, args.tam), start=1):
    print(f"#{i}  similitud {f['similitud']:.3f}  ·  {f['doc']}, pág. {f['pagina']}")
    print("    " + f["texto"].replace("\n", " ")[:300] + "...\n")
