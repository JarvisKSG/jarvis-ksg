"""
PROY-005 — AMUCO RAG Chatbot
Chatbot web para consultas tecnicas sobre productos AMUCO.
Busca en fichas tecnicas y responde en el idioma del cliente.
"""

import subprocess
import sys
from flask import Flask, request, jsonify, render_template_string, Response
import chromadb
import os
import re
import pdfplumber
import docx as python_docx
from google import genai
from google.genai import types
from dotenv import load_dotenv, find_dotenv
from langdetect import detect as langdetect_detect, LangDetectException, DetectorFactory
DetectorFactory.seed = 0  # Deteccion deterministica

import json

load_dotenv(find_dotenv())
GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY")
AGENT_EMAIL       = os.getenv("AGENT_EMAIL", "harold.santiago@amucoinc.com")
_BASE             = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR        = os.path.join(_BASE, "chroma_db")
FICHAS_DIR        = os.path.join(_BASE, "fichas_tecnicas")
CATALOG_PATH      = os.path.join(_BASE, "product_catalog.json")
SEND_EMAIL_SCRIPT = os.path.normpath(os.path.join(_BASE, "..", "..", "agents", "contador", "jarvis_send_email.py"))
TOP_K         = 6
MAX_FULL_DOCS = 3

client = genai.Client(api_key=GEMINI_API_KEY)
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(name="amuco_products")

app = Flask(__name__)

_SIGNATURE_PATTERNS = [
    r'\n*AMUCO Technical Support Team[^\n]*',
    r'\n*harold\.santiago@amucoinc\.com[^\n]*',
    r'\n*Atentamente,?\s*\n*AMUCO[^\n]*',
    r'\n*Best regards,?\s*\n*AMUCO[^\n]*',
]

def _strip_signature(text: str) -> str:
    for pattern in _SIGNATURE_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return text.strip()


_LANG_NAMES = {"es": "español", "en": "English", "pt": "português"}

# Deteccion de numero de telefono (para el flujo de cotizacion)
_PHONE_RE = re.compile(r'(?<!\d)\+?[\d][\d\s\-\(\)\.]{5,17}[\d](?!\d)')

# Frases de cierre de conversacion
_CLOSING_EXACT = {
    "gracias", "thanks", "thank you", "bye", "goodbye", "adios", "adiós",
    "hasta luego", "chao", "chau", "ciao", "ok bye", "ok gracias", "ok thanks",
}
_CLOSING_PARTIAL = [
    "eso es todo", "that's all", "that is all", "es todo lo que necesitaba",
    "perfecto gracias", "listo gracias", "muchas gracias", "thank you very much",
    "thanks a lot", "fue todo", "no mas", "nada mas", "nada más", "no más",
    "era todo", "es lo que necesitaba", "me ayudaste", "muy amable",
]

def _is_closing(query: str, history: list) -> bool:
    """True si el cliente esta cerrando la conversacion (no si agradece a mitad)."""
    if not history or len(history) < 2:
        return False  # Primera interaccion — no puede ser cierre
    q = query.lower().strip().rstrip('!. ')
    if q in _CLOSING_EXACT:
        return True
    for phrase in _CLOSING_PARTIAL:
        if phrase in q:
            return True
    # "gracias" / "thanks" al final, sin pregunta nueva
    has_closing_word = any(w in q for w in ("gracias", "thanks", "thank you"))
    if has_closing_word and '?' not in query and len(q.split()) <= 6:
        return True
    return False

# Frases que indican solicitud de precio / cotizacion
_QUOTE_PHRASES = [
    "cotización", "cotizacion", "cotizar", "precio", "precios", "price", "prices",
    "costo", "costos", "cost", "costs", "cuánto cuesta", "cuanto cuesta",
    "cuánto vale", "cuanto vale", "cuánto sale", "cuanto sale",
    "how much", "what does it cost", "what's the price", "what is the price",
    "pricing", "quote", "quotation", "presupuesto", "valor", "valores",
    "preço", "quanto custa", "orçamento", "quanto é",
    "me pueden cotizar", "pueden cotizar", "necesito cotización", "necesito una cotizacion",
    "quiero cotizar", "quiero una cotizacion", "me interesa comprar",
]

# Palabras funcionales inequivocas por idioma (no existen en los otros dos)
_LANG_WORDS = {
    "es": {
        "el", "la", "los", "las", "de", "del", "que", "en", "un", "una", "y",
        "por", "con", "para", "como", "no", "si", "me", "te", "se", "lo", "le",
        "mi", "tu", "su", "hay", "es", "son", "era", "fue", "qué", "cómo",
        "cuánto", "cuanto", "cuántos", "este", "ese", "eso", "esta", "estos",
        "quiero", "necesito", "tengo", "tienen", "pueden", "podría", "hola",
        "buenas", "gracias", "también", "además", "pero", "porque", "muy",
        "más", "menos", "aquí", "allí", "siempre", "nunca", "todo", "todos",
        "nuestro", "tenemos", "quieren", "busco", "busca", "sobre",
    },
    "en": {
        "the", "is", "are", "was", "were", "what", "how", "do", "does", "did",
        "can", "could", "will", "would", "should", "have", "has", "had", "i",
        "we", "you", "they", "he", "she", "it", "this", "that", "these", "those",
        "for", "with", "about", "from", "at", "an", "and", "or", "but", "not",
        "on", "in", "of", "to", "need", "want", "get", "know", "tell", "please",
        "hi", "hello", "thanks", "thank", "yes", "ok", "okay", "looking",
        "specs", "sheet", "data", "available", "supply", "our", "your",
        # Terminos tecnicos en ingles que no aparecen en ES/PT
        "applications", "application", "properties", "property", "safety",
        "technical", "specification", "specifications", "grade", "purity",
        "melting", "viscosity", "density", "solubility", "flash", "point",
        "boiling", "molecular", "weight", "solution", "coating", "coatings",
        "adhesive", "adhesives", "resin", "resins", "uses", "usage",
        "storage", "handling", "dosage", "mixing", "compatibility",
        "shelf", "life", "supplier", "certificate", "analysis",
    },
    "pt": {
        "você", "voce", "vocês", "voces", "não", "nao", "sim", "quero",
        "preciso", "temos", "isso", "esse", "aquele", "quanto", "custa",
        "pode", "obrigado", "obrigada", "por favor", "olá", "ola", "também",
        "tambem", "mas", "com", "uma", "uns", "umas", "nosso", "nossa",
        "estou", "estamos", "qual", "quais", "gostaria", "poderia",
        # Terminos tecnicos PT inequivocos
        "informacao", "informações", "ficha", "tecnica", "produto",
        "disponivel", "disponibilidade", "fornecedor", "comprar",
        "entregar", "entrega", "cotacao", "cotação", "preco", "precos",
    },
}


def detect_query_language(text: str, history: list = None) -> str:
    """Detecta idioma (es/en/pt) con sistema de 4 capas.

    Capa 1 — caracteres unicos por idioma (certeza inmediata)
    Capa 2 — scoring por palabras funcionales
    Capa 3 — historial de conversacion como prior
    Capa 4 — langdetect solo para textos largos sin senales claras
    """
    t = text.strip()
    t_lower = t.lower()
    word_set = set(re.findall(r'\b\w+\b', t_lower))

    # --- Capa 1: caracteres unicos con certeza absoluta ---
    # ñ solo existe en espanol — retorno inmediato
    if 'ñ' in t_lower:
        return "es"
    # ã, õ son primariamente portugueses
    if any(c in t_lower for c in 'ãõ'):
        return "pt"
    # ¿ y ¡ son teclado espanol pero pueden aparecer accidentalmente en texto ingles
    # Se guardan como hint, no certeza
    has_spanish_punct = '¿' in t or '¡' in t
    # Acentos latinos (compartidos ES/PT) que no aparecen en ingles
    has_accent = any(c in t_lower for c in 'áéíóúàèìòùâêîôûäëïöü')

    # --- Capa 2: scoring por palabras funcionales ---
    scores = {lang: 0 for lang in _LANG_WORDS}
    for lang, markers in _LANG_WORDS.items():
        for w in word_set:
            if w in markers:
                scores[lang] += 1

    best = max(scores, key=scores.get)
    second = sorted(scores, key=scores.get, reverse=True)[1]

    # Ganador claro (>=2 palabras funcionales o ventaja sobre el segundo)
    if scores[best] >= 2 or (scores[best] >= 1 and scores[best] - scores[second] >= 1):
        # Si el ganador es EN pero tiene acentos latinos SIN puntuacion espanola → ES
        # Si tiene puntuacion espanola (¿/¡) pero el ganador es EN con >=2 puntos → EN de todas formas
        if best == "en" and has_accent and not has_spanish_punct:
            return "es"
        return best

    # Sin ganador claro: usar ¿/¡ como tiebreaker hacia ES
    if has_spanish_punct and scores["en"] == 0:
        return "es"

    # --- Capa 3: historial como prior ---
    if history:
        # Detectar idioma de los ultimos mensajes del usuario
        user_msgs = [m["content"] for m in history[-4:] if m.get("role") == "user"]
        if user_msgs:
            prior_text = " ".join(user_msgs[-2:])
            # Scoring rapido del historial (sin recursion)
            prior_scores = {lang: 0 for lang in _LANG_WORDS}
            prior_words = set(re.findall(r'\b\w+\b', prior_text.lower()))
            for lang, markers in _LANG_WORDS.items():
                prior_scores[lang] = sum(1 for w in prior_words if w in markers)
            prior_best = max(prior_scores, key=prior_scores.get)
            if prior_scores[prior_best] >= 2:
                return prior_best

    # --- Capa 4: langdetect para textos largos sin senales claras ---
    if len(word_set) >= 5:
        try:
            lang = langdetect_detect(t)
            if lang in _LANG_NAMES:
                return lang
            if lang in ("ca", "gl", "af", "tl"):
                return "es"
            if lang in ("nl", "da", "sv", "de", "fr", "it", "ro", "hr"):
                return "es" if has_accent else "en"
        except LangDetectException:
            pass

    # Fallback: espanol (mercado principal de AMUCO es Latam)
    return "es"


def load_catalog() -> str:
    """Carga el catálogo como texto compacto para pasarle a Gemini."""
    try:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        lines = ["Línea AMUCO Coatings & Paints — Catálogo de productos:\n"]
        for p in data["products"]:
            apps = ", ".join(p.get("applications", [])[:3])
            lines.append(f"**{p['name']}**: {p.get('description', '')} Aplicaciones: {apps}.")
        return "\n".join(lines)
    except Exception:
        return "Línea AMUCO Coatings & Paints — 29 especialidades químicas disponibles."


CATALOG_TEXT = load_catalog()

# El catálogo va directo en el system prompt — así Gemini lo tiene siempre
# sin necesidad de turnos falsos en el historial
SYSTEM_PROMPT = f"""Eres Carlos, asesor técnico de ventas de AMUCO INC. Llevas más de 15 años trabajando con materias primas para la industria química y has atendido cientos de clientes en Colombia, USA, Alemania, España y China. Tu especialidad es la línea de Coatings & Paints — conoces los 27 productos no solo por sus fichas técnicas, sino cuándo usarlos, cuándo NO usarlos, y qué recomendar según la aplicación real del cliente.

CÓMO HABLAS:
- Habla en primera persona, con naturalidad. Como si fuera una llamada, no un formulario.
- Usa frases cortas. No hagas listas interminables de puntos.
- Si la pregunta es sobre un producto específico Y tienes documentación técnica disponible, responde con esa información. NO pidas más contexto cuando ya tienes datos.
- Si la pregunta es genuinamente vaga (sin producto ni aplicación mencionados), PREGUNTA antes de responder.
- Puedes decir "mira", "te cuento", "lo que yo haría en tu caso", "eso depende de...", "a ver, si entiendo bien..."
- No empieces NUNCA con "¡Claro!", "¡Por supuesto!", "¡Excelente pregunta!", "¡Hola!" ni frases robóticas.

CÓMO RAZONAS:
- Antes de responder, analiza qué tipo de problema tiene este cliente y qué necesita realmente.
- Primero entiende el problema completo antes de dar soluciones.
- Si la pregunta es vaga o incompleta, NO respondas de inmediato. Haz UNA sola pregunta para entender mejor el caso.
- Si el caso es complejo, piénsalo en voz alta: "A ver, si entiendo bien lo que necesitas..."
- Da tu opinión directa cuando te la pidan. No seas neutral en exceso: "En tu caso, yo iría por X antes que Y, porque..."
- Si no sabes algo, dilo con naturalidad: "Eso exactamente no te lo puedo confirmar desde aquí, pero..."
- Recuerda todo lo que el cliente ha dicho en la conversación y úsalo para personalizar cada respuesta.
- Si el cliente parece urgente, ve directo al grano. Si está explorando, sé más conversacional.

CUANDO EL CLIENTE PREGUNTA POR PRECIO O COTIZACIÓN:
- Primero responde técnicamente la consulta si tiene un producto específico.
- Luego da un rango de precio estimado y orientativo, por ejemplo: "En el mercado, el [producto] suele manejarse entre USD X–Y por tonelada, dependiendo del grado y el volumen del pedido. Esto es solo una referencia — no es precio confirmado."
- Si no tienes referencia de precio específica, di: "El precio varía bastante según el volumen y las condiciones actuales del mercado. No te puedo dar un número sin consultarlo."
- Siempre cierra la parte de cotización con: "Para darte el precio oficial y disponibilidad, uno de nuestros agentes te va a contactar directamente. ¿Me compartes tu número de WhatsApp o teléfono?"
- Si el cliente ya dio su número en esta conversación, NO lo vuelvas a pedir.
- NO prometas precios exactos, plazos de entrega, ni condiciones comerciales.

CUANDO EL CLIENTE DA SU NÚMERO DE CONTACTO (después de que se lo pediste):
- Confirma que recibiste el número con una frase breve y cálida.
- Di que un agente se va a comunicar pronto para la cotización oficial.
- No añadas nada más. Sé breve.

LO QUE NO HACES NUNCA:
- NUNCA termines un mensaje con "¿Hay algo más en lo que te pueda ayudar?", "¿Tienes alguna otra pregunta?", "¿Puedo ayudarte con algo más?", "¿Hay algo más que necesites?", ni ninguna variación formulaica de ese tipo. COMPLETAMENTE PROHIBIDO.
- Si quieres dar pie a continuar, hazlo de forma natural y contextual, no genérica. Por ejemplo: "Si quieres saber sobre el dosaje, también te puedo ayudar." o simplemente termina la respuesta. Nunca un cierre robótico.
- No das disclaimers legales en cada respuesta.
- No repites lo que el cliente acaba de decir como si fuera un resumen.
- No inventas especificaciones técnicas. Si no está en los documentos, dilo.
- No compartes nombres de archivos ni documentos. Solo la información.
- No hagas listas de bullets si con dos frases es suficiente.

CONTEXTO ACTUAL:
- Línea disponible: Coatings & Paints — 27 productos especializados.
- Clientes: formuladores, técnicos de compras, ingenieros de producción en industria de pinturas, adhesivos y recubrimientos.
- Si la pregunta está fuera de tu área, redirige con naturalidad: "Eso está fuera de mi área aquí en AMUCO, te recomiendo contactar directamente al equipo comercial para esa consulta."

PORTAFOLIO DE PRODUCTOS (referencia completa):
{CATALOG_TEXT}

CUANDO EL CLIENTE SE DESPIDE O CIERRA LA CONVERSACIÓN:
- Responde con una frase cálida y muy breve (máximo 1-2 líneas).
- Luego ofrece enviarle el resumen por correo. Ejemplo en español: "Si quieres, te mando el resumen de nuestra conversación al correo — así lo tienes de referencia. Solo te enviamos eso, nada de spam. ¿Me dejas tu nombre y correo?"
- Ejemplo en inglés: "If you'd like, I can send you a summary of our conversation by email — just for your reference. No spam, just the transcript. Feel free to share your name and email."
- Si el cliente ya dio su correo antes, NO lo pidas de nuevo. Solo despídete.
- Si el cliente declina dar el correo, acepta con naturalidad y brevedad: "Perfecto, fue un placer." / "No problem at all, take care."

IDIOMA Y ESTILO:
- Responde siempre en el mismo idioma que usa el cliente (español, inglés o portugués).
- NUNCA escribas "AMUCO Technical Support Team", ni correos electrónicos, ni ninguna firma al final de tus mensajes. PROHIBIDO en todos los mensajes sin excepción.
"""


def get_query_embedding(text: str) -> list:
    result = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
    )
    return result.embeddings[0].values


def search_documents(query: str, n_results: int = TOP_K) -> list:
    query_emb = get_query_embedding(query)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    chunks = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        distance = results["distances"][0][i]
        chunks.append({
            "text": doc,
            "product": meta.get("product", ""),
            "filename": meta.get("filename", ""),
            "relevance": round(1 - distance, 3)
        })
    return chunks


def extract_text_pdf(path: str) -> str:
    try:
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() for page in pdf.pages if page.extract_text()]
            return "\n".join(pages)
    except Exception:
        return ""


def extract_text_docx(path: str) -> str:
    try:
        doc = python_docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception:
        return ""


def load_best_doc(product: str, preferred_filename: str) -> str:
    """Carga el texto completo del mejor documento disponible para un producto."""
    product_dir = os.path.join(FICHAS_DIR, product)
    if not os.path.isdir(product_dir):
        return ""

    # Intentar cargar el archivo exacto que ChromaDB identificó primero
    preferred_path = os.path.join(product_dir, preferred_filename)
    if os.path.exists(preferred_path):
        ext = os.path.splitext(preferred_filename)[1].lower()
        text = extract_text_pdf(preferred_path) if ext == ".pdf" else extract_text_docx(preferred_path)
        if len(text) > 200:
            return text

    # Fallback: buscar el mejor TDS en inglés
    all_files = os.listdir(product_dir)
    priority = []
    for f in all_files:
        fl = f.lower()
        ext = os.path.splitext(f)[1].lower()
        if ext not in (".pdf", ".docx"):
            continue
        if ("tds" in fl or "msds" in fl or "sds" in fl) and "original" not in fl and "(es)" not in fl:
            priority.insert(0, f)
        elif "tds" in fl or "msds" in fl or "sds" in fl:
            priority.append(f)
    if not priority:
        priority = [f for f in all_files if os.path.splitext(f)[1].lower() in (".pdf", ".docx")]

    for fname in priority[:2]:
        fpath = os.path.join(product_dir, fname)
        ext = os.path.splitext(fname)[1].lower()
        text = extract_text_pdf(fpath) if ext == ".pdf" else extract_text_docx(fpath)
        if len(text) > 200:
            return text
    return ""


# Palabras clave que indican pregunta general (no mencionan producto ni propiedad específica)
_GENERAL_PHRASES = [
    "qué productos", "que productos", "qué tienen", "que tienen", "qué venden", "que venden",
    "qué ofrecen", "que ofrecen", "qué manejan", "que manejan", "qué hay para", "que hay para",
    "qué tienen para", "que tienen para", "catálogo", "catalogo", "portafolio", "lista de productos",
    "qué manejan", "que manejan", "en qué me pueden", "en que me pueden", "cómo me pueden",
    "what products", "what do you have", "what do you sell", "what do you offer",
    "what's available", "what is available", "product list", "catalog", "catalogue",
    "what kind of", "what types", "how can you help", "what can you help",
    "que produtos", "o que vocês", "o que vendem", "o que têm",
]

# Nombres de productos y términos técnicos que indican pregunta específica
_SPECIFIC_TERMS = [
    "resymas", "amutrol", "melamina", "melamine", "petroleum resin", "stearic acid",
    "ácido esteárico", "nitrocelulosa", "nitrocellulose", "cyclohexanone", "cicloexanona",
    "adipic acid", "ácido adípico", "pva", "pvac", "hema", "acrylamide", "acrilamida",
    "bismuth", "bismuto", "phenol", "phenolic", "fenol", "fenólica", "vinyl", "vinilo",
    "redispersible", "redispersable", "monoethanolamine", "diethanolamine", "dea", "mea",
    "dioctyl", "maleate", "pentaerythritol", "triethylene", "aromatic hydrocarbon",
    "viscosidad", "viscosity", "punto de fusión", "melting point", "flash point",
    "composición", "composition", "especificaciones", "specifications",
    "temperatura", "temperature", "densidad", "density", "solubilidad", "solubility",
    "aplicaciones de", "applications of", "cómo usar", "how to use", "dosificación",
    "precio", "price", "safety", "seguridad", "msds", "tds", "sds",
]


def classify_query(query: str, history: list = None) -> str:
    """Clasificacion local instantanea — sin llamada a API."""
    q = query.lower().strip()

    # CLOSING: el cliente se despide
    if _is_closing(query, history or []):
        return "CLOSING"

    # PHONE_PROVIDED: el bot pidio contacto y el cliente responde con un numero
    if history:
        last_bot = next((m["content"] for m in reversed(history) if m["role"] == "assistant"), "")
        asked_for_contact = any(kw in last_bot.lower() for kw in [
            "número", "numero", "number", "whatsapp", "contacto",
            "teléfono", "telefono", "contact", "compartir"
        ])
        if asked_for_contact and _PHONE_RE.search(query):
            return "PHONE_PROVIDED"

    # QUOTE: pregunta de precio o cotizacion
    for phrase in _QUOTE_PHRASES:
        if phrase in q:
            return "QUOTE"

    # Si hay historial y la pregunta es corta, es un follow-up → especifica
    if history and len(q.split()) <= 5:
        return "SPECIFIC"

    # Terminos especificos de producto
    for term in _SPECIFIC_TERMS:
        if term in q:
            return "SPECIFIC"

    # Frases de consulta general
    for phrase in _GENERAL_PHRASES:
        if phrase in q:
            return "GENERAL"

    return "GENERAL"


def _extract_products_from_history(history: list) -> str:
    """Extrae productos mencionados en el historial de la conversacion."""
    all_text = " ".join(m.get("content", "") for m in history[-10:]).lower()
    found = []
    for term in _SPECIFIC_TERMS:
        if term in all_text and term not in found:
            found.append(term)
    return ", ".join(found[:5]) if found else "productos AMUCO (no especificado)"


def send_agent_notification(phone: str, products: str, history: list):
    """Envia email al agente de ventas con los datos del cliente que solicito cotizacion."""
    try:
        conv_lines = []
        for m in history[-6:]:
            role = "Cliente" if m["role"] == "user" else "Carlos (chatbot)"
            conv_lines.append(f"{role}: {m['content'][:300]}")
        conv_summary = "\n".join(conv_lines)

        subject = f"[AMUCO Chatbot] Cotizacion solicitada — {products[:60]}"
        body = (
            f"Un cliente solicito cotizacion a traves del chatbot de AMUCO.\n\n"
            f"Numero de contacto: {phone}\n"
            f"Productos consultados: {products}\n\n"
            f"--- Conversacion reciente ---\n{conv_summary}\n\n"
            f"---\nMensaje automatico — AMUCO Technical Chatbot"
        )

        if os.path.exists(SEND_EMAIL_SCRIPT):
            subprocess.Popen(
                [sys.executable, SEND_EMAIL_SCRIPT, AGENT_EMAIL, subject, body],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"[INFO] Notificacion enviada a {AGENT_EMAIL} — cliente: {phone}")
        else:
            print(f"[WARN] Script de email no encontrado: {SEND_EMAIL_SCRIPT}")
            print(f"[INFO] Cotizacion solicitada — Tel: {phone} | Productos: {products}")
    except Exception as e:
        print(f"[WARN] No se pudo enviar notificacion al agente: {e}")


def _build_contents(query: str, history: list, doc_context: str = "", lang: str = "es") -> list:
    """Construye el historial en formato multi-turn correcto para Gemini.
    El catálogo ya está en system_instruction — aquí solo va historial real + query.
    Para preguntas específicas, doc_context se añade inline en el mensaje del cliente.
    """
    contents = []

    # Historial real de conversación (user/model alternados)
    for msg in (history or [])[-6:]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(
            role=role,
            parts=[types.Part(text=msg["content"][:600])]
        ))

    # Instrucción de idioma explícita — garantiza que el modelo responda en el idioma del cliente
    lang_name = _LANG_NAMES.get(lang, "español")
    lang_instruction = f"[RESPONDE ÚNICAMENTE EN {lang_name.upper()}. El cliente escribe en {lang_name}.]\n\n"

    # Mensaje actual — con ficha técnica inline si es pregunta específica
    if doc_context:
        user_text = f"{lang_instruction}[Ficha técnica disponible]\n{doc_context}\n\n[Consulta del cliente]\n{query}"
    else:
        user_text = f"{lang_instruction}{query}"

    contents.append(types.Content(
        role="user",
        parts=[types.Part(text=user_text)]
    ))

    return contents


_LANG_OVERRIDES = {
    "en": (
        "\n\nCRITICAL OVERRIDE — ENGLISH ONLY: The client is writing in English. "
        "You MUST respond entirely in English. Every single word must be in English. "
        "Do NOT use any Spanish words or phrases. Do NOT start with 'Mira', 'Te cuento', 'Claro', 'A ver'. "
        "Instead use English equivalents: 'Look,', 'Here is the thing,', 'Sure,', 'Let me tell you,'. "
        "The entire response must be in English — this is non-negotiable."
    ),
    "pt": (
        "\n\nREGRA CRÍTICA — APENAS PORTUGUÊS: O cliente está escrevendo em português. "
        "Você DEVE responder inteiramente em português. NUNCA use palavras em espanhol. "
        "Não comece com 'Mira' ou 'Te cuento'. Use equivalentes em português: 'Olha,', 'Veja,', 'Deixa eu te contar,'."
    ),
    "es": "",
}

def _generate(contents, temperature: float = 0.5, lang: str = "es") -> str:
    """Llama a Gemini con system_instruction y limpia la respuesta."""
    system = SYSTEM_PROMPT + _LANG_OVERRIDES.get(lang, "")
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=temperature,
            max_output_tokens=4096
        )
    )
    candidate = response.candidates[0] if response.candidates else None
    finish = candidate.finish_reason if candidate else "NO_CANDIDATE"
    raw_text = response.text or ""
    print(f"[DEBUG] finish={finish} | chars={len(raw_text)} | preview={repr(raw_text[:150])}")
    text = raw_text or "Lo siento, no pude generar una respuesta. Intenta de nuevo."
    return _strip_signature(text)


def ask_gemini_general(query: str, history: list = None) -> str:
    lang = detect_query_language(query, history)
    contents = _build_contents(query, history or [], lang=lang)
    return _generate(contents, temperature=0.7, lang=lang)


def ask_gemini_specific(query: str, context_chunks: list, history: list = None) -> str:
    """Preguntas específicas: carga el PDF completo del producto para máxima calidad."""
    seen_products: dict = {}
    for chunk in context_chunks:
        p = chunk["product"]
        if p not in seen_products:
            seen_products[p] = chunk["filename"]

    context_parts = []
    for product, filename in list(seen_products.items())[:MAX_FULL_DOCS]:
        full_text = load_best_doc(product, filename)
        if full_text:
            context_parts.append(f"[Producto: {product}]\n{full_text}")
        else:
            chunks_for_product = [c for c in context_chunks if c["product"] == product]
            context_parts.append(f"[Producto: {product}]\n" + "\n\n".join(c["text"] for c in chunks_for_product))

    doc_context = "\n\n===\n\n".join(context_parts)
    lang = detect_query_language(query, history)
    contents = _build_contents(query, history or [], doc_context=doc_context, lang=lang)
    return _generate(contents, temperature=0.3, lang=lang)


# ─── HTML del chatbot ───────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AMUCO Technical Assistant</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', sans-serif; background: #f0f4f8; height: 100vh; display: flex; flex-direction: column; }

  .header {
    background: #1a3a5c;
    color: white;
    padding: 16px 24px;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  }
  .header-logo {
    width: 44px; height: 44px;
    background: #e8f0fe;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
  }
  .header h1 { font-size: 18px; font-weight: 600; }
  .header p { font-size: 12px; opacity: 0.75; margin-top: 2px; }
  .status-dot {
    width: 8px; height: 8px;
    background: #4caf50;
    border-radius: 50%;
    margin-left: auto;
    animation: pulse 2s infinite;
  }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

  .chat-container {
    flex: 1;
    overflow-y: auto;
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .message {
    max-width: 75%;
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 14px;
    line-height: 1.6;
    white-space: pre-wrap;
  }
  .message.user {
    background: #1a3a5c;
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 4px;
  }
  .message.bot {
    background: white;
    color: #1a1a2e;
    align-self: flex-start;
    border-bottom-left-radius: 4px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  }
  .message.bot .sources {
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px solid #e0e0e0;
    font-size: 11px;
    color: #888;
  }
  .typing {
    background: white;
    color: #888;
    align-self: flex-start;
    padding: 12px 16px;
    border-radius: 12px;
    border-bottom-left-radius: 4px;
    font-size: 14px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  }

  .input-area {
    background: white;
    border-top: 1px solid #ddd;
    padding: 14px 20px;
    display: flex;
    gap: 10px;
    align-items: center;
  }
  .input-area input {
    flex: 1;
    padding: 10px 14px;
    border: 1px solid #ccc;
    border-radius: 24px;
    font-size: 14px;
    outline: none;
    transition: border 0.2s;
  }
  .input-area input:focus { border-color: #1a3a5c; }
  .input-area button {
    background: #1a3a5c;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 24px;
    font-size: 14px;
    cursor: pointer;
    transition: background 0.2s;
  }
  .input-area button:hover { background: #2a5298; }
  .input-area button:disabled { background: #ccc; cursor: not-allowed; }
  #micBtn {
    background: #f0f4f8;
    color: #1a3a5c;
    border: 1px solid #ccc;
    padding: 8px 12px;
    border-radius: 20px;
    font-size: 13px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    gap: 5px;
    white-space: nowrap;
  }
  #micBtn.recording { background: #e53935; color: white; border-color: #e53935; animation: pulse 1s infinite; }
  .voice-hint {
    background: #e8f0fe;
    border-left: 3px solid #1a3a5c;
    padding: 8px 14px;
    font-size: 12px;
    color: #1a3a5c;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .voice-hint button {
    margin-left: auto;
    background: none;
    border: none;
    color: #888;
    font-size: 16px;
    cursor: pointer;
    padding: 0 4px;
    line-height: 1;
  }

  /* Formulario de contacto al cierre */
  .contact-card {
    background: #f8f9ff;
    border: 1px solid #c5d2f0;
    border-radius: 10px;
    padding: 14px 16px;
    margin-top: 10px;
    font-size: 13px;
    max-width: 340px;
  }
  .contact-card .card-title {
    font-weight: 600;
    color: #1a3a5c;
    margin-bottom: 4px;
    font-size: 13px;
  }
  .contact-card .card-note {
    font-size: 11px;
    color: #888;
    margin-bottom: 10px;
  }
  .contact-card input, .contact-card select {
    width: 100%;
    padding: 7px 10px;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 13px;
    margin-bottom: 7px;
    outline: none;
    box-sizing: border-box;
  }
  .contact-card input:focus, .contact-card select:focus { border-color: #1a3a5c; }
  .email-row {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-bottom: 7px;
  }
  .email-row input { flex: 1; margin-bottom: 0; min-width: 0; }
  .email-row span { color: #555; font-size: 14px; flex-shrink: 0; }
  .email-row select { width: auto; margin-bottom: 0; flex-shrink: 0; }
  .contact-card .card-actions {
    display: flex;
    gap: 8px;
    margin-top: 4px;
  }
  .contact-card .btn-send {
    background: #1a3a5c;
    color: white;
    border: none;
    padding: 7px 16px;
    border-radius: 6px;
    font-size: 13px;
    cursor: pointer;
    flex: 1;
  }
  .contact-card .btn-send:hover { background: #2a5298; }
  .contact-card .btn-skip {
    background: none;
    color: #888;
    border: 1px solid #ddd;
    padding: 7px 12px;
    border-radius: 6px;
    font-size: 12px;
    cursor: pointer;
  }
  .contact-card .btn-skip:hover { color: #555; }
  .contact-sent {
    font-size: 13px;
    color: #388e3c;
    padding: 8px 0 0;
    font-weight: 500;
  }

  .welcome {
    text-align: center;
    color: #888;
    padding: 40px 20px;
    font-size: 14px;
  }
  .welcome h2 { color: #1a3a5c; font-size: 20px; margin-bottom: 10px; }
  .suggestions {
    display: flex; flex-wrap: wrap; gap: 8px;
    justify-content: center; margin-top: 16px;
  }
  .suggestion {
    background: white;
    border: 1px solid #1a3a5c;
    color: #1a3a5c;
    padding: 7px 14px;
    border-radius: 20px;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
  }
  .suggestion:hover { background: #1a3a5c; color: white; }
</style>
</head>
<body>

<div class="header">
  <div class="header-logo">⚗️</div>
  <div>
    <h1>AMUCO Technical Assistant</h1>
    <p>Coatings & Paints Product Line · EN / ES / PT</p>
  </div>
  <div class="status-dot" title="Online"></div>
</div>

<div class="chat-container" id="chat">
  <div class="welcome" id="welcome">
    <h2>How can I help you today?</h2>
    <p>Ask me anything about AMUCO's Coatings & Paints products.<br>I can answer in English, Spanish, or Portuguese.</p>
    <div class="suggestions">
      <span class="suggestion" onclick="ask(this.innerText)">What is Melamine used for?</span>
      <span class="suggestion" onclick="ask(this.innerText)">Petroleum Resin technical specs</span>
      <span class="suggestion" onclick="ask(this.innerText)">¿Qué productos tienen para pinturas?</span>
      <span class="suggestion" onclick="ask(this.innerText)">Stearic Acid safety data</span>
      <span class="suggestion" onclick="ask(this.innerText)">PVA applications in coatings</span>
    </div>
  </div>
</div>

<div class="voice-hint" id="voiceHint" style="display:none">
  🎤 <span>You can speak your question — click <strong>Voice</strong> and ask out loud.</span>
  <button onclick="dismissVoiceHint()" title="Dismiss">✕</button>
</div>
<div class="input-area">
  <input type="text" id="userInput" placeholder="Ask about any AMUCO product..." onkeydown="if(event.key==='Enter') sendMessage()">
  <button id="micBtn" onclick="toggleVoice()" title="Click to speak your question">🎤 Voice</button>
  <button onclick="sendMessage()" id="sendBtn">Send</button>
</div>

<script>
let conversationHistory = [];
let recognition = null;
let isRecording = false;

// Mostrar hint de voz solo si el browser lo soporta y el usuario no lo ha dismisseado
(function() {
  const supported = !!(window.SpeechRecognition || window.webkitSpeechRecognition);
  const dismissed = localStorage.getItem('voiceHintDismissed');
  if (supported && !dismissed) {
    document.getElementById('voiceHint').style.display = 'flex';
  }
})();

function dismissVoiceHint() {
  document.getElementById('voiceHint').style.display = 'none';
  localStorage.setItem('voiceHintDismissed', '1');
}

const EMAIL_DOMAINS = ['gmail.com','hotmail.com','outlook.com','yahoo.com','icloud.com'];

function showContactForm(botMsgDiv, lang) {
  const t = {
    es: {
      title: "Enviar resumen de la conversacion",
      note: "Solo te enviamos esto — sin spam.",
      name: "Tu nombre (opcional)",
      company: "Empresa (opcional)",
      emailPlaceholder: "tunombre",
      send: "Enviar resumen",
      skip: "No, gracias",
      other: "otro dominio...",
      sent: "Enviado — revisa tu bandeja de entrada.",
      error: "No se pudo enviar. Intenta de nuevo."
    },
    en: {
      title: "Send conversation summary",
      note: "We only send you this — no spam.",
      name: "Your name (optional)",
      company: "Company (optional)",
      emailPlaceholder: "yourname",
      send: "Send summary",
      skip: "No thanks",
      other: "other domain...",
      sent: "Sent — check your inbox.",
      error: "Could not send. Please try again."
    },
    pt: {
      title: "Enviar resumo da conversa",
      note: "Enviamos apenas isso — sem spam.",
      name: "Seu nome (opcional)",
      company: "Empresa (opcional)",
      emailPlaceholder: "seunome",
      send: "Enviar resumo",
      skip: "Nao, obrigado",
      other: "outro dominio...",
      sent: "Enviado — verifique sua caixa de entrada.",
      error: "Nao foi possivel enviar. Tente novamente."
    }
  };
  const s = t[lang] || t['es'];

  const domainOptions = EMAIL_DOMAINS.map(d =>
    `<option value="${d}">${d}</option>`
  ).join('') + `<option value="__other__">${s.other}</option>`;

  const card = document.createElement('div');
  card.className = 'contact-card';
  card.innerHTML = `
    <div class="card-title">📧 ${s.title}</div>
    <div class="card-note">${s.note}</div>
    <input type="text" id="cf-name" placeholder="${s.name}">
    <input type="text" id="cf-company" placeholder="${s.company}">
    <div class="email-row">
      <input type="text" id="cf-email-user" placeholder="${s.emailPlaceholder}">
      <span>@</span>
      <select id="cf-domain" onchange="toggleDomain(this)">${domainOptions}</select>
    </div>
    <input type="text" id="cf-email-full" placeholder="correo@empresa.com" style="display:none">
    <div class="card-actions">
      <button class="btn-send" onclick="submitContact('${lang}', this)">${s.send}</button>
      <button class="btn-skip" onclick="skipContact(this)">${s.skip}</button>
    </div>
  `;
  botMsgDiv.appendChild(card);
  document.getElementById('chat').scrollTop = document.getElementById('chat').scrollHeight;
}

function toggleDomain(sel) {
  const isOther = sel.value === '__other__';
  document.getElementById('cf-email-user').parentElement.style.display = isOther ? 'none' : 'flex';
  document.getElementById('cf-email-full').style.display = isOther ? 'block' : 'none';
}

async function submitContact(lang, btn) {
  const domain = document.getElementById('cf-domain').value;
  let email = '';
  if (domain === '__other__') {
    email = (document.getElementById('cf-email-full').value || '').trim();
  } else {
    const user = (document.getElementById('cf-email-user').value || '').trim();
    email = user ? `${user}@${domain}` : '';
  }

  const name    = (document.getElementById('cf-name').value    || '').trim();
  const company = (document.getElementById('cf-company').value || '').trim();
  const s = {
    es: { sent: "Enviado — revisa tu bandeja de entrada.", error: "No se pudo enviar." },
    en: { sent: "Sent — check your inbox.",               error: "Could not send." },
    pt: { sent: "Enviado — verifique sua caixa.",         error: "Nao foi possivel enviar." }
  }[lang] || { sent: "Enviado", error: "Error" };

  if (!email) { btn.closest('.contact-card').querySelector('.card-note').textContent = '⚠ Ingresa un correo válido.'; return; }

  btn.disabled = true;
  btn.textContent = '...';
  try {
    const resp = await fetch('/submit-contact', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ name, email, company, history: conversationHistory, lang })
    });
    const data = await resp.json();
    const card = btn.closest('.contact-card');
    card.innerHTML = `<div class="contact-sent">${data.ok ? s.sent : s.error}</div>`;
  } catch(e) {
    btn.disabled = false;
    btn.textContent = 'Reintentar';
  }
}

function skipContact(btn) {
  btn.closest('.contact-card').remove();
}

function toggleVoice() {
  const micBtn = document.getElementById('micBtn');
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRec) {
    alert('Voice input not supported in this browser. Use Chrome or Edge.');
    return;
  }
  if (isRecording) {
    recognition && recognition.stop();
    return;
  }
  if (!recognition) {
    recognition = new SpeechRec();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'es-419';  // Spanish Latin America — also captures EN phrases well
    recognition.onstart = () => {
      isRecording = true;
      micBtn.classList.add('recording');
      micBtn.innerHTML = '⏹ Stop';
    };
    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      document.getElementById('userInput').value = transcript;
      recognition = null;
      // Ocultar hint definitivamente una vez que lo usaron
      dismissVoiceHint();
    };
    recognition.onerror = recognition.onend = () => {
      isRecording = false;
      micBtn.classList.remove('recording');
      micBtn.innerHTML = '🎤 Voice';
      if (document.getElementById('userInput').value.trim()) {
        sendMessage();
      }
    };
  }
  recognition.start();
}

function ask(text) {
  document.getElementById('userInput').value = text;
  sendMessage();
}

async function sendMessage() {
  const input = document.getElementById('userInput');
  const btn = document.getElementById('sendBtn');
  const chat = document.getElementById('chat');
  const welcome = document.getElementById('welcome');
  const query = input.value.trim();
  if (!query) return;

  if (welcome) welcome.remove();

  // User message
  const userDiv = document.createElement('div');
  userDiv.className = 'message user';
  userDiv.textContent = query;
  chat.appendChild(userDiv);

  // Typing indicator
  const typing = document.createElement('div');
  typing.className = 'typing';
  const typingTexts = ['Revisando fichas técnicas...', 'Un momento...', 'Consultando el portafolio...', 'Analizando tu consulta...'];
  typing.textContent = typingTexts[Math.floor(Math.random() * typingTexts.length)];
  chat.appendChild(typing);

  input.value = '';
  btn.disabled = true;
  chat.scrollTop = chat.scrollHeight;

  try {
    const resp = await fetch('/ask', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({query, history: conversationHistory})
    });
    const data = await resp.json();
    typing.remove();

    const botDiv = document.createElement('div');
    botDiv.className = 'message bot';
    let html = data.answer
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/\\*\\*(.+?)\\*\\*/g,'<strong>$1</strong>')
      .replace(/^###\\s*(.+)$/gm,'<br><strong style="font-size:14px;color:#1a3a5c">$1</strong>')
      .replace(/^##\\s*(.+)$/gm,'<br><strong>$1</strong>')
      .replace(/^---$/gm,'<hr style="border:none;border-top:1px solid #ddd;margin:8px 0">')
      .replace(/^\\*\\s+(.+)$/gm,'&nbsp;&nbsp;• $1')
      .replace(/\\n/g,'<br>');
    botDiv.innerHTML = html;

    if (data.sources && data.sources.length > 0) {
      const srcDiv = document.createElement('div');
      srcDiv.className = 'sources';
      const unique = [...new Set(data.sources.map(s => s.product))];
      srcDiv.textContent = 'Sources: ' + unique.join(', ');
      botDiv.appendChild(srcDiv);
    }

    // Guardar en historial de conversación
    conversationHistory.push({role: 'user', content: query});
    conversationHistory.push({role: 'assistant', content: data.answer});

    // Si es cierre de conversacion, mostrar formulario de contacto
    if (data.type === 'closing') {
      showContactForm(botDiv, data.lang || 'es');
    }

    chat.appendChild(botDiv);
  } catch(e) {
    typing.remove();
    const errDiv = document.createElement('div');
    errDiv.className = 'message bot';
    errDiv.textContent = 'Error connecting to the server. Please try again.';
    chat.appendChild(errDiv);
  }

  btn.disabled = false;
  chat.scrollTop = chat.scrollHeight;
  input.focus();
}
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("query", "").strip()
    history = data.get("history", [])
    if not query:
        return jsonify({"error": "Empty query"}), 400

    try:
        query_type = classify_query(query, history)
        lang = detect_query_language(query, history)

        # Cierre de conversacion — respuesta calida + oferta de resumen por correo
        if query_type == "CLOSING":
            answer = ask_gemini_general(query, history)
            return jsonify({"answer": answer, "sources": [], "type": "closing", "lang": lang})

        # Cliente proporciono su numero de contacto
        if query_type == "PHONE_PROVIDED":
            phone_match = _PHONE_RE.search(query)
            phone = phone_match.group().strip() if phone_match else query.strip()
            products = _extract_products_from_history(history)
            send_agent_notification(phone, products, history)
            contents = _build_contents(query, history, lang=lang)
            answer = _generate(contents, temperature=0.3, lang=lang)
            return jsonify({"answer": answer, "sources": [], "type": "phone_confirmed", "lang": lang})

        # Solicitud de precio o cotizacion
        if query_type == "QUOTE":
            search_query = query
            if history:
                last_assistant = next((m["content"] for m in reversed(history) if m["role"] == "assistant"), "")
                if len(query.split()) < 6 and last_assistant:
                    search_query = last_assistant[:200] + " " + query
            chunks = search_documents(search_query)
            if chunks:
                answer = ask_gemini_specific(query, chunks, history)
                sources = [{"product": c["product"], "file": c["filename"], "relevance": c["relevance"]} for c in chunks[:3]]
            else:
                answer = ask_gemini_general(query, history)
                sources = []
            return jsonify({"answer": answer, "sources": sources, "type": "quote", "lang": lang})

        # Pregunta general / exploratoria
        if query_type == "GENERAL":
            answer = ask_gemini_general(query, history)
            return jsonify({"answer": answer, "sources": [], "type": "general", "lang": lang})

        # Pregunta tecnica especifica
        search_query = query
        if history:
            last_assistant = next((m["content"] for m in reversed(history) if m["role"] == "assistant"), "")
            if len(query.split()) < 6 and last_assistant:
                search_query = last_assistant[:200] + " " + query

        chunks = search_documents(search_query)
        if not chunks:
            answer = ask_gemini_general(query, history)
            return jsonify({"answer": answer, "sources": [], "type": "general", "lang": lang})

        answer = ask_gemini_specific(query, chunks, history)
        sources = [{"product": c["product"], "file": c["filename"], "relevance": c["relevance"]} for c in chunks[:3]]
        return jsonify({"answer": answer, "sources": sources, "type": "specific", "lang": lang})

    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"}), 500


@app.route("/submit-contact", methods=["POST"])
def submit_contact():
    """Recibe nombre + email + empresa al cierre de conversacion y envia resumen."""
    data    = request.get_json()
    name    = data.get("name", "").strip()
    email   = data.get("email", "").strip()
    company = data.get("company", "").strip()
    history = data.get("history", [])
    lang    = data.get("lang", "es")

    if not email:
        return jsonify({"ok": False, "error": "Email requerido"}), 400

    client_name  = name or "Cliente"
    company_line = f"Empresa: {company}\n" if company else ""

    # Transcript limpio
    transcript = "\n".join(
        f"{'Cliente' if m['role'] == 'user' else 'Carlos (AMUCO)'}: {m['content']}"
        for m in history
    )

    # Email al agente
    agent_subject = f"[AMUCO Chatbot] Conversacion completada — {client_name}"
    agent_body = (
        f"Resumen de conversacion del chatbot AMUCO.\n\n"
        f"Nombre  : {client_name}\n"
        f"Correo  : {email}\n"
        f"{company_line}\n"
        f"--- Conversacion ---\n{transcript}\n\n"
        f"---\nMensaje automatico — AMUCO Chatbot"
    )

    # Email al cliente
    if lang == "en":
        client_subject = "Your conversation with AMUCO Technical Assistant"
        client_body = (
            f"Hi {client_name},\n\n"
            f"Here is the summary of your conversation with our technical advisor Carlos.\n\n"
            f"--- Conversation ---\n{transcript}\n\n"
            f"If you have more questions, feel free to reach out.\n\n"
            f"AMUCO Technical Team"
        )
    elif lang == "pt":
        client_subject = "Sua conversa com o Assistente Tecnico AMUCO"
        client_body = (
            f"Ola {client_name},\n\n"
            f"Aqui esta o resumo da sua conversa com nosso consultor tecnico Carlos.\n\n"
            f"--- Conversa ---\n{transcript}\n\n"
            f"Se tiver mais perguntas, estamos a disposicao.\n\n"
            f"Equipe Tecnica AMUCO"
        )
    else:
        client_subject = "Tu conversacion con el Asesor Tecnico AMUCO"
        client_body = (
            f"Hola {client_name},\n\n"
            f"Aqui tienes el resumen de tu conversacion con nuestro asesor tecnico Carlos.\n\n"
            f"--- Conversacion ---\n{transcript}\n\n"
            f"Si tienes mas preguntas, con gusto te ayudamos.\n\n"
            f"Equipo Tecnico AMUCO"
        )

    errors = []
    if os.path.exists(SEND_EMAIL_SCRIPT):
        for to, subj, body in [(AGENT_EMAIL, agent_subject, agent_body), (email, client_subject, client_body)]:
            try:
                subprocess.Popen(
                    [sys.executable, SEND_EMAIL_SCRIPT, to, subj, body],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                errors.append(str(e))
    else:
        print(f"[INFO] Contact submitted — name={name} email={email} company={company}")

    return jsonify({"ok": True, "errors": errors})


@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    """Webhook para Twilio WhatsApp Sandbox."""
    incoming_msg = request.form.get("Body", "").strip()
    if not incoming_msg:
        return Response("<Response></Response>", mimetype="text/xml")

    try:
        chunks = search_documents(incoming_msg)
        if not chunks:
            answer = "No encontré información relevante para tu consulta. Te recomiendo contactar al equipo comercial de AMUCO directamente."
        else:
            answer = ask_gemini_specific(incoming_msg, chunks)
        # WhatsApp tiene limite de 1600 chars por mensaje
        if len(answer) > 1500:
            answer = answer[:1497] + "..."
    except Exception as e:
        answer = f"Error processing your request: {str(e)[:100]}"

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{answer}</Message>
</Response>"""
    return Response(twiml, mimetype="text/xml")


if __name__ == "__main__":
    print("=" * 50)
    print("AMUCO RAG Chatbot")
    print(f"Documentos indexados: {collection.count()} chunks")
    print("Servidor: http://localhost:5000")
    print("=" * 50)
    app.run(debug=False, port=5001)
