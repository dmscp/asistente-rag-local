"""Paso 1-3: carga los PDF, los trocea, calcula los embeddings y los guarda en ChromaDB.
Uso:  python indexar.py            (indexa con 300 y con 1000 caracteres)
      python indexar.py --tam 1000 (solo un tamaño)"""
import argparse
import time

import config
import rag

parser = argparse.ArgumentParser()
parser.add_argument("--tam", type=int, choices=list(config.TAMANOS), help="tamaño de fragmento")
args = parser.parse_args()

rag.cabecera("INDEXACIÓN DE LOS APUNTES")
paginas = rag.cargar_pdfs()
docs = sorted({p["doc"] for p in paginas})
print(f"\nDocumentos cargados: {len(docs)} · Páginas con texto: {len(paginas)}")
for d in docs:
    print(f"  - {d}: {sum(1 for p in paginas if p['doc'] == d)} páginas")

for tam in ([args.tam] if args.tam else config.TAMANOS):
    solape = config.TAMANOS[tam]
    fragmentos = rag.trocear_paginas(paginas, tam, solape)
    print(f"\n--- Troceado: {tam} caracteres, solapamiento {solape} ---")
    print(f"Fragmentos generados: {len(fragmentos)}")
    for d in docs:
        print(f"  - {d}: {sum(1 for f in fragmentos if f['doc'] == d)} fragmentos")
    ej = fragmentos[len(fragmentos) // 3]
    print(f"\nEjemplo de fragmento ({ej['id']}, {len(ej['texto'])} caracteres):")
    print("  " + ej["texto"].replace("\n", " ")[:400] + ("..." if len(ej["texto"]) > 400 else ""))

    print(f"\nCalculando embeddings con {config.MODELO_EMB}...")
    t0 = time.time()
    col = rag.crear_coleccion(tam)
    LOTE = 32
    for i in range(0, len(fragmentos), LOTE):
        lote = fragmentos[i:i + LOTE]
        col.add(ids=[f["id"] for f in lote],
                documents=[f["texto"] for f in lote],
                embeddings=rag.embeddings_documentos([f["texto"] for f in lote]),
                metadatas=[{"doc": f["doc"], "pagina": f["pagina"]} for f in lote])
    print(f"Colección '{col.name}' creada en '{config.CARPETA_BD}' con {col.count()} fragmentos "
          f"({time.time() - t0:.1f} s)")
print("\nIndexación terminada.")
