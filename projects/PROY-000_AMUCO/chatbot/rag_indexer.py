"""
PROY-005 — RAG Indexer
Extrae texto de PDFs y DOCX, genera embeddings con Gemini, guarda en ChromaDB.
Ejecutar UNA VEZ antes de arrancar el chatbot.
"""

import os
import json
import time
import pdfplumber
import docx
import chromadb
from google import genai
from google.genai import types

# Rate limiting: free tier = 100 req/min → 1 req cada 0.65s = ~92/min (margen seguro)
EMBED_DELAY = 0.65

GEMINI_API_KEY = "AIzaSyAw2y5QfsB1-039Fa70dY5zQThP67DRASQ"
_BASE = os.path.dirname(os.path.abspath(__file__))
FICHAS_DIR = os.path.join(_BASE, "fichas_tecnicas")
CHROMA_DIR = os.path.join(_BASE, "chroma_db")
CHUNK_SIZE = 1200     # caracteres por chunk (mas grande = menos chunks = menos requests)
CHUNK_OVERLAP = 100

client = genai.Client(api_key=GEMINI_API_KEY)
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(
    name="amuco_products",
    metadata={"hnsw:space": "cosine"}
)


def extract_text_pdf(path: str) -> str:
    try:
        with pdfplumber.open(path) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            return "\n".join(pages)
    except Exception as e:
        print(f"    [WARN] PDF error {os.path.basename(path)}: {e}")
        return ""


def extract_text_docx(path: str) -> str:
    try:
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        print(f"    [WARN] DOCX error {os.path.basename(path)}: {e}")
        return ""


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if len(chunk) > 100:  # ignorar chunks muy pequenos
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def get_embedding(text: str) -> list:
    time.sleep(EMBED_DELAY)  # rate limiting: ~92 req/min (free tier max: 100)
    result = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
    )
    return result.embeddings[0].values


def index_all():
    print("=" * 60)
    print("AMUCO RAG Indexer")
    print("=" * 60)

    # Contar lo que ya esta indexado
    existing = collection.count()
    print(f"Chunks ya indexados: {existing}")

    total_files = 0
    total_chunks = 0
    skipped = 0
    errors = 0

    for product_folder in sorted(os.listdir(FICHAS_DIR)):
        product_path = os.path.join(FICHAS_DIR, product_folder)
        if not os.path.isdir(product_path):
            continue

        # Priorizar TDS Amuco en ingles, luego MSDS, luego resto
        # Saltar: COA (certificates of analysis), ISO certs, originales si hay version Amuco
        all_files = os.listdir(product_path)
        priority_files = []
        for f in all_files:
            fl = f.lower()
            ext = os.path.splitext(f)[1].lower()
            if ext not in ('.pdf', '.docx'):
                continue
            # Prioridad alta: TDS y MSDS en ingles (version Amuco preferida)
            if ('tds' in fl or 'msds' in fl or 'sds' in fl) and 'original' not in fl and '(es)' not in fl:
                priority_files.insert(0, f)
            elif 'tds' in fl or 'msds' in fl or 'sds' in fl:
                priority_files.append(f)
        # Si no hay TDS/MSDS, tomar cualquier PDF/DOCX
        if not priority_files:
            priority_files = [f for f in all_files if os.path.splitext(f)[1].lower() in ('.pdf', '.docx')]

        # Limitar a max 3 archivos por producto para no exceder cuota
        selected_files = priority_files[:3]

        for filename in selected_files:
            filepath = os.path.join(product_path, filename)
            ext = os.path.splitext(filename)[1].lower()

            if ext not in ('.pdf', '.docx', '.doc'):
                continue

            # ID unico para este archivo
            doc_id = f"{product_folder}__{filename}"

            # Verificar si ya esta indexado
            existing_ids = collection.get(where={"doc_id": doc_id})
            if existing_ids and existing_ids['ids']:
                skipped += 1
                continue

            # Extraer texto
            if ext == '.pdf':
                text = extract_text_pdf(filepath)
            else:
                text = extract_text_docx(filepath)

            if not text or len(text) < 50:
                continue

            # Chunking
            chunks = chunk_text(text)
            if not chunks:
                continue

            # Embeddings y guardado en ChromaDB
            try:
                ids = []
                embeddings = []
                documents = []
                metadatas = []

                for i, chunk in enumerate(chunks):
                    chunk_id = f"{doc_id}__chunk{i}"
                    emb = get_embedding(chunk)
                    ids.append(chunk_id)
                    embeddings.append(emb)
                    documents.append(chunk)
                    metadatas.append({
                        "product": product_folder,
                        "filename": filename,
                        "doc_id": doc_id,
                        "chunk_index": i
                    })

                collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )

                total_files += 1
                total_chunks += len(chunks)
                print(f"  [OK] {product_folder[:30]:<30} | {filename[:40]:<40} | {len(chunks)} chunks")

            except Exception as e:
                print(f"  [ERR] {filename}: {e}")
                errors += 1

    print()
    print("=" * 60)
    print("RESUMEN")
    print(f"  Archivos indexados: {total_files}")
    print(f"  Chunks totales: {total_chunks}")
    print(f"  Ya existian (skip): {skipped}")
    print(f"  Errores: {errors}")
    print(f"  Total en DB: {collection.count()}")
    print("=" * 60)


if __name__ == "__main__":
    index_all()
