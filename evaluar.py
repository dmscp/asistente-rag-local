"""Pasos 5.1 y 5.2: lanza las 12 preguntas sin RAG y con RAG (300 y 1000 caracteres)
y guarda todo en resultados.csv para clasificar cada respuesta a mano.
Uso:  python evaluar.py"""
import csv
import json
import time

import config
import rag

rag.cabecera("EVALUACIÓN: 12 PREGUNTAS SIN RAG Y CON RAG")
with open("preguntas.json", encoding="utf-8") as f:
    preguntas = json.load(f)

filas = []
for q in preguntas:
    print(f"\n[{q['n']}/12] {q['pregunta']}")
    fila = {"n": q["n"], "pregunta": q["pregunta"], "respuesta_correcta": q["correcta"]}

    t0 = time.time()
    fila["sin_rag"] = rag.responder_sin_rag(q["pregunta"])
    fila["sin_rag_seg"] = round(time.time() - t0, 1)
    fila["sin_rag_clasificacion"] = ""          # rellenar a mano: correcta/incompleta/incorrecta/inventada

    for tam in config.TAMANOS:
        t0 = time.time()
        respuesta, frags = rag.responder_con_rag(q["pregunta"], tam)
        fila[f"rag{tam}"] = respuesta
        fila[f"rag{tam}_seg"] = round(time.time() - t0, 1)
        fila[f"rag{tam}_fuentes"] = "; ".join(f"{x['doc'][:5]} p.{x['pagina']} ({x['similitud']:.2f})" for x in frags)
        if q["paginas"]:
            ok = any(x["doc"] == q["doc"] and x["pagina"] in q["paginas"] for x in frags)
            fila[f"rag{tam}_recupero_pagina"] = "sí" if ok else "no"
        else:
            fila[f"rag{tam}_recupero_pagina"] = "no aplica"
        fila[f"rag{tam}_clasificacion"] = ""
        print(f"   RAG {tam}: página correcta recuperada -> {fila[f'rag{tam}_recupero_pagina']}")
    filas.append(fila)

with open("resultados.csv", "w", newline="", encoding="utf-8-sig") as f:   # utf-8-sig: se abre bien en Excel
    w = csv.DictWriter(f, fieldnames=list(filas[0]), delimiter=";")
    w.writeheader()
    w.writerows(filas)
print("\nResultados guardados en resultados.csv")
