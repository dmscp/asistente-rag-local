"""Funciones comunes del sistema RAG · Samuel Correia Pinto · 2º DAM"""
import getpass
import os
import re
import platform

import chromadb
import ollama
from pypdf import PdfReader

import config

PROMPT_RAG = """Eres un asistente que responde preguntas sobre los apuntes de Ciberseguridad de 2º DAM.
Responde ÚNICAMENTE con la información del CONTEXTO. No uses tus conocimientos propios.
Si la respuesta no aparece en el contexto, responde exactamente: "No lo sé, esa información no está en los apuntes."
Responde en español, de forma breve, y termina indicando entre paréntesis el documento y la página de donde sale.

CONTEXTO:
{contexto}

PREGUNTA: {pregunta}

RESPUESTA:"""


def cabecera(titulo):
    """Muestra quién ejecuta el programa (para que las capturas queden identificadas)."""
    print("=" * 70)
    print(f"  {titulo}")
    print(f"  Autor: Samuel Correia Pinto · Usuario del sistema: {getpass.getuser()}")
    print(f"  Equipo: {platform.system()} {platform.machine()} · Carpeta: {os.path.basename(os.getcwd())}")
    print("=" * 70)


# ---------- 1. CARGA ----------
def limpiar(texto):
    texto = texto.replace("\u00ad", "")          # guiones invisibles de los PDF
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{2,}", "\n", texto)
    return texto.strip()


def cargar_pdfs(carpeta=config.CARPETA_DOCS):
    """Devuelve una lista de páginas: {'doc', 'pagina', 'texto'}."""
    paginas = []
    for nombre in sorted(os.listdir(carpeta)):
        if not nombre.lower().endswith(".pdf"):
            continue
        lector = PdfReader(os.path.join(carpeta, nombre))
        for num, pagina in enumerate(lector.pages, start=1):
            texto = limpiar(pagina.extract_text() or "")
            if texto:
                paginas.append({"doc": nombre, "pagina": num, "texto": texto})
    return paginas


# ---------- 2. TROCEADO ----------
def trocear(texto, tam, solape):
    """Divide un texto en fragmentos de 'tam' caracteres que se solapan 'solape' caracteres.
    Intenta cortar en un espacio para no partir palabras."""
    fragmentos, inicio = [], 0
    while inicio < len(texto):
        fin = min(inicio + tam, len(texto))
        if fin < len(texto):
            espacio = texto.rfind(" ", inicio + tam // 2, fin)
            if espacio != -1:
                fin = espacio
        fragmentos.append(texto[inicio:fin].strip())
        if fin >= len(texto):
            break
        nuevo = fin - solape
        espacio = texto.find(" ", nuevo, fin)      # empezar el siguiente trozo en una palabra entera
        if espacio != -1:
            nuevo = espacio + 1
        inicio = max(nuevo, inicio + 1)
    return [f for f in fragmentos if f]


def trocear_paginas(paginas, tam, solape):
    fragmentos = []
    for p in paginas:
        for i, trozo in enumerate(trocear(p["texto"], tam, solape)):
            fragmentos.append({
                "id": f"{p['doc']}-p{p['pagina']}-{i}",
                "texto": trozo,
                "doc": p["doc"],
                "pagina": p["pagina"],
            })
    return fragmentos


# ---------- 3. EMBEDDINGS Y BASE DE DATOS ----------
# nomic-embed-text funciona mejor con estos prefijos (lo indica su documentación)
def embeddings_documentos(textos):
    return ollama.embed(model=config.MODELO_EMB,
                        input=["search_document: " + t for t in textos])["embeddings"]


def embedding_pregunta(pregunta):
    return ollama.embed(model=config.MODELO_EMB,
                        input=["search_query: " + pregunta])["embeddings"][0]


def nombre_coleccion(tam):
    return f"apuntes_{tam}"


def cliente():
    return chromadb.PersistentClient(path=config.CARPETA_BD)


def crear_coleccion(tam):
    c = cliente()
    nombre = nombre_coleccion(tam)
    if nombre in [col.name for col in c.list_collections()]:
        c.delete_collection(nombre)              # se rehace desde cero
    # distancia coseno: similitud = 1 - distancia
    return c.create_collection(name=nombre, metadata={"hnsw:space": "cosine"})


def obtener_coleccion(tam):
    return cliente().get_collection(nombre_coleccion(tam))


# ---------- 4. RECUPERACIÓN ----------
def buscar(pregunta, tam=config.TAM_POR_DEFECTO, k=config.TOP_K):
    col = obtener_coleccion(tam)
    res = col.query(query_embeddings=[embedding_pregunta(pregunta)], n_results=k)
    resultados = []
    for texto, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        resultados.append({"texto": texto, "doc": meta["doc"], "pagina": meta["pagina"],
                           "similitud": round(1 - dist, 3)})
    return resultados


# ---------- 5. GENERACIÓN ----------
def generar(prompt):
    r = ollama.chat(model=config.MODELO_LLM,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0})   # temperatura 0: respuestas repetibles
    return r["message"]["content"].strip()


def construir_prompt(pregunta, fragmentos):
    contexto = "\n\n".join(f"[{f['doc']}, pág. {f['pagina']}]\n{f['texto']}" for f in fragmentos)
    return PROMPT_RAG.format(contexto=contexto, pregunta=pregunta)


def responder_con_rag(pregunta, tam=config.TAM_POR_DEFECTO):
    fragmentos = buscar(pregunta, tam)
    return generar(construir_prompt(pregunta, fragmentos)), fragmentos


def responder_sin_rag(pregunta):
    return generar(f"Responde en español, de forma breve, a esta pregunta sobre ciberseguridad:\n{pregunta}")
