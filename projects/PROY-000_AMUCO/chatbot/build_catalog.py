"""
Genera product_catalog.json desde ChromaDB — sin llamadas a Gemini.
Ejecutar UNA VEZ: /c/Python312/python.exe build_catalog.py
"""

import json
import os
import re
import chromadb

_BASE     = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(_BASE, "chroma_db")
FICHAS_DIR = os.path.join(_BASE, "fichas_tecnicas")
OUTPUT     = os.path.join(_BASE, "product_catalog.json")

chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(name="amuco_products")

# Descripciones cortas curadas manualmente (las más comunes en la línea Coatings & Paints)
KNOWN = {
    "Melamina": {
        "description": "Resina termoplástica cristalina usada en lacas, barnices y recubrimientos de alto brillo. Aporta dureza y resistencia química al film.",
        "applications": ["Lacas termoestables", "Recubrimientos para madera", "Papel decorativo laminado"]
    },
    "Petroleum Resin": {
        "description": "Resina de hidrocarburo derivada del petróleo. Tackificante y modificador de adherencia para pinturas, adhesivos y recubrimientos.",
        "applications": ["Pinturas y recubrimientos industriales", "Adhesivos hot melt", "Tintas de impresión"]
    },
    "Nitrocellulose": {
        "description": "Polímero celulósico de secado rápido. Base de lacas de alta dureza y brillo para madera, metal y cuero.",
        "applications": ["Lacas para madera y muebles", "Recubrimientos automotrices", "Tintas para impresión flexográfica"]
    },
    "Resymas": {
        "description": "Solución de nitrocelulosa en mezcla de acetatos y alcoholes lista para formular. Ideal para lacas y barnices de secado rápido.",
        "applications": ["Lacas para madera", "Barnices industriales", "Tintas base nitrocelulosa"]
    },
    "Polyvinyl alcohol PVA": {
        "description": "Polímero sintético soluble en agua con excelente resistencia a aceites y solventes. Base para adhesivos, recubrimientos y películas.",
        "applications": ["Adhesivos para papel y cartón", "Recubrimientos de papel", "Emulsiones para pinturas"]
    },
    "Polyvinyl Acetate PVAC": {
        "description": "Polímero termoplástico en emulsión acuosa con alta adhesión. Usado en pinturas de emulsión, adhesivos y selladores.",
        "applications": ["Pinturas de emulsión", "Adhesivos vinílicos", "Imprimaciones y selladores"]
    },
    "Stearic Acid": {
        "description": "Ácido graso saturado de origen vegetal o animal. Agente dispersante y lubricante en pinturas, recubrimientos y cosméticos.",
        "applications": ["Dispersante de pigmentos", "Lubricante en formulaciones", "Estabilizador de emulsiones"]
    },
    "Redispersible Polymer Powder": {
        "description": "Polvo polimérico redispersable en agua. Mejora adhesión, flexibilidad y resistencia al agua en morteros y recubrimientos.",
        "applications": ["Morteros y pastas cementosas", "Recubrimientos de fachada", "Adhesivos para baldosas"]
    },
    "AMUTROL": {
        "description": "Línea de resinas tackificantes de hidrocarburo (C5 hidrogenadas y monómero puro). Modifican adhesión y pegajosidad en formulaciones poliméricas.",
        "applications": ["Adhesivos hot melt (HMA)", "Adhesivos sensibles a la presión (PSA)", "Modificación de polímeros en recubrimientos"]
    },
    "Aromatic Hydrocarbon Resin": {
        "description": "Resina de hidrocarburo aromático con alta compatibilidad con cauchos y polímeros. Tackificante en adhesivos y recubrimientos.",
        "applications": ["Adhesivos de contacto", "Recubrimientos de caucho", "Selladores industriales"]
    },
    "Cyclohexanone": {
        "description": "Solvente orgánico cetónico con alto poder disolvente. Usado en lacas de nitrocelulosa, resinas vinílicas y recubrimientos especiales.",
        "applications": ["Solvente para lacas y barnices", "Diluyente en recubrimientos industriales", "Síntesis química"]
    },
    "Adipic Acid": {
        "description": "Ácido dicarboxílico alifático. Monómero para poliésteres y poliuretanos usados en recubrimientos flexibles y adhesivos.",
        "applications": ["Síntesis de poliésteres para recubrimientos", "Plastificantes para PVC", "Poliuretanos flexibles"]
    },
    "Aluminium Hydroxide - Hydrate - Trihydrate": {
        "description": "Carga mineral ignífuga y dispersante. Retardante de llama en pinturas y recubrimientos intumescentes.",
        "applications": ["Pinturas intumescentes ignífugas", "Relleno mineral en recubrimientos", "Aislantes eléctricos"]
    },
    "Bismuth Hydroxide": {
        "description": "Compuesto inorgánico de bismuto usado como catalizador de curado en pinturas de poliuretano libres de estaño.",
        "applications": ["Catalizador para pinturas PU sin estaño", "Recubrimientos de bajo VOC", "Barnices industriales"]
    },
    "Bismuth Oxide": {
        "description": "Óxido de bismuto con propiedades catalíticas y pigmentantes. Alternativa no tóxica a catalizadores de estaño en recubrimientos.",
        "applications": ["Catalizador en recubrimientos de poliuretano", "Pigmento amarillo en esmaltes", "Recubrimientos de alta temperatura"]
    },
    "Diethanolamine DEA": {
        "description": "Amina alifática con doble función alcohol-amina. Neutralizante y emulsificante en pinturas de emulsión acuosa.",
        "applications": ["Neutralizante en pinturas acuosas", "Emulsificante industrial", "Inhibidor de corrosión"]
    },
    "Monoethanolamine": {
        "description": "Amina alcohólica de bajo peso molecular. Agente neutralizante y dispersante en pinturas base agua y recubrimientos acuosos.",
        "applications": ["Neutralizante pH en pinturas acuosas", "Dispersante de pigmentos", "Fluidos de corte industriales"]
    },
    "Dioctyl Maleate": {
        "description": "Éster plastificante derivado del ácido maleico. Aporta flexibilidad y resistencia a polímeros en recubrimientos y PVC.",
        "applications": ["Plastificante para PVC y vinilo", "Modificador de flexibilidad en recubrimientos", "Copolimerización reactiva"]
    },
    "Phenol": {
        "description": "Compuesto aromático monohidroxilado. Materia prima para resinas fenólicas, epóxicas y recubrimientos de alta resistencia química.",
        "applications": ["Síntesis de resinas fenólicas", "Recubrimientos anticorrosivos", "Adhesivos estructurales"]
    },
    "Phenol -Hydroxybenzene - Monohydroxybenzene - Carbolic acid": {
        "description": "Fenol puro de alta pureza. Base para resinas fenólicas usadas en barnices, recubrimientos resistentes al calor y adhesivos.",
        "applications": ["Resinas fenólicas para barnices", "Recubrimientos resistentes a temperatura", "Laminados y aglomerados"]
    },
    "Phenolic Resin": {
        "description": "Resina termoendurecible de alta resistencia química y térmica. Base de barnices, imprimaciones anticorrosivas y recubrimientos industriales.",
        "applications": ["Barnices y lacas industriales", "Imprimaciones anticorrosivas", "Recubrimientos para tanques y tuberías"]
    },
    "Acrylamide": {
        "description": "Monómero vinílico hidrofílico. Precursor de poliacrilamidas usadas como espesantes y agentes de retención en recubrimientos de papel.",
        "applications": ["Espesantes para recubrimientos de papel", "Floculantes en tratamiento de aguas", "Geles de poliacrilamida"]
    },
    "2-Hydroxy Ethyl Methacrylate 2HEMA": {
        "description": "Monómero acrílico funcional hidroxilo. Comonómero reactivo en recubrimientos de poliuretano y epoxi de curado UV.",
        "applications": ["Recubrimientos UV de curado rápido", "Resinas acrílicas para pinturas 2K", "Lentes de contacto y biomateriales"]
    },
    "Triethylene Glycol Dimethylacrylate": {
        "description": "Monómero difuncional acrílico de curado UV/EB. Agente de entrecruzamiento en recubrimientos de alta dureza.",
        "applications": ["Recubrimientos UV de alta dureza", "Agente de crosslinking en resinas acrílicas", "Tintas UV de impresión"]
    },
    "VINYL ACETATE- VAE": {
        "description": "Copolímero de acetato de vinilo y etileno en emulsión. Alta flexibilidad y adhesión en pinturas, adhesivos y recubrimientos.",
        "applications": ["Pinturas de emulsión interior/exterior", "Adhesivos para construcción", "Recubrimientos flexibles de papel"]
    },
    "Vinyl Chloride-Vinyl Acetates Terpolymer (UMCH)": {
        "description": "Terpolímero vinílico con grupos hidroxilo. Alta adhesión a metales y resistencia química en recubrimientos de latas y envases.",
        "applications": ["Recubrimientos para envases metálicos", "Lacas para latas de alimentos y bebidas", "Tintas y barnices de impresión"]
    },
    "Hitex, Esterquat o Methyl Triethanolammonium": {
        "description": "Surfactante catiónico (esterquat). Agente acondicionador y emulsificante usado en formulaciones de recubrimientos y cuidado del cabello.",
        "applications": ["Emulsificante en recubrimientos", "Acondicionador de superficies", "Suavizantes y formulaciones cosméticas"]
    },
}


def get_best_file(product: str) -> str:
    results = collection.get(where={"product": product}, limit=1, include=["metadatas"])
    metas = results.get("metadatas", [])
    return metas[0].get("filename", "") if metas else ""


def build_catalog():
    folders = sorted([
        f for f in os.listdir(FICHAS_DIR)
        if os.path.isdir(os.path.join(FICHAS_DIR, f)) and not f.startswith("_")
    ])

    catalog = {"products": []}

    for folder in folders:
        info = KNOWN.get(folder, {})
        best_file = get_best_file(folder)

        catalog["products"].append({
            "name": folder,
            "folder": folder,
            "description": info.get("description", f"Especialidad química de la línea Coatings & Paints de AMUCO."),
            "applications": info.get("applications", ["Recubrimientos industriales"]),
            "key_properties": info.get("key_properties", []),
            "best_file": best_file
        })
        print(f"  [OK] {folder}")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print(f"\nCatalogo guardado: {OUTPUT}")
    print(f"Total productos: {len(catalog['products'])}")


if __name__ == "__main__":
    build_catalog()
