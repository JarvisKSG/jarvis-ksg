import urllib.request, json, urllib.parse, os

# TOKEN: Bearer token de Azure Entra ID de Harold (expira ~1h).
# Extraer desde DevTools del browser en kiwi.amucoinc.com → Network → Authorization header.
# NO hardcodear aquí. Pasar como variable de entorno o argumento al correr el script.
import os
TOKEN = os.environ.get('SHAREPOINT_TOKEN', '')

BASE_URL = 'https://reciend.sharepoint.com'
SAVE_DIR = r'C:\Users\thoma\Desktop\Claude\PROY-005_Agente_IA_AMUCO\fichas_tecnicas'
HEADERS = {'Authorization': 'Bearer ' + TOKEN, 'Accept': 'application/json;odata=verbose'}

subfolders = [
    'Triethylene Glycol Dimethylacrylate', 'Lithium Hydroxi', 'AMUTROL',
    'Aluminium Hydroxide - Hydrate - Trihydrate', '2-Hydroxy Ethyl Methacrylate 2HEMA',
    'Aromatic Hydrocarbon Resin', 'Melamina', 'Glycerol-Glyceryl Monostearate- GMS',
    'VINYL ACETATE- VAE', 'Silica', 'Polyvinyl alcohol PVA',
    'Trisopropanolamine TIPA 85%', 'Acrylamide', 'Dioctyl Maleate', 'Resymas',
    'Redispersible Polymer Powder', 'Monoethanolamine', 'Petroleum Resin',
    'Phenol -Hydroxybenzene - Monohydroxybenzene - Carbolic acid',
    'Polyvinyl Acetate PVAC', 'Bismuth Hydroxide', 'Diethanolamine DEA',
    'Nitrocellulose', 'Hitex, Esterquat o Methyl Triethanolammonium', 'Adipic Acid',
    'Cyclohexanone', 'Vinyl Chloride-Vinyl Acetates Terpolymer (UMCH)', 'Formalin 37%',
    'Stearic Acid', 'Phenol', 'Bismuth Oxide', 'Pentaerythritol', 'Phenolic Resin'
]

BASE_FOLDER = '/sites/Amuco/Shared Documents/Sales/AMUCO Archivos Comerciales/02 COMERCIAL/07 DOCUMENTOS PRODUCTOS/04 LINEA COATINGS & PAINTS'
ALLOWED_EXT = {'.pdf', '.docx', '.doc', '.xlsx', '.pptx'}

downloaded = 0
errors = 0
manifest = []

os.makedirs(SAVE_DIR, exist_ok=True)

def api_get(path):
    url = BASE_URL + '/sites/Amuco/_api/web/GetFolderByServerRelativeUrl(@p)/' + path + "?@p='" + urllib.parse.quote(folder_path, safe='') + "'"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())

def get_files(fp):
    url = BASE_URL + '/sites/Amuco/_api/web/GetFolderByServerRelativeUrl(@p)/Files?@p=' + urllib.parse.quote("'" + fp + "'")
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read()).get('d', {}).get('results', [])

def get_subfolders(fp):
    url = BASE_URL + '/sites/Amuco/_api/web/GetFolderByServerRelativeUrl(@p)/Folders?@p=' + urllib.parse.quote("'" + fp + "'")
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read()).get('d', {}).get('results', [])

for prod in subfolders:
    folder_path = BASE_FOLDER + '/' + prod
    try:
        files = get_files(folder_path)

        if not files:
            subs = get_subfolders(folder_path)
            for sf in subs:
                files.extend(get_files(sf['ServerRelativeUrl']))

        prod_downloaded = 0
        for f in files:
            fname = f['Name']
            ext = os.path.splitext(fname)[1].lower()
            if ext not in ALLOWED_EXT:
                continue

            # safe filename: replace problematic chars
            safe_prod = prod[:50]
            for ch in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
                safe_prod = safe_prod.replace(ch, '-')
            safe_name = safe_prod + '__' + fname
            save_path = os.path.join(SAVE_DIR, safe_name)

            if os.path.exists(save_path):
                manifest.append({'product': prod, 'file': fname, 'local': safe_name, 'status': 'exists'})
                continue

            dl_url = BASE_URL + '/sites/Amuco/_api/web/GetFileByServerRelativeUrl(@p)/$value?@p=' + urllib.parse.quote("'" + f['ServerRelativeUrl'] + "'")
            dl_req = urllib.request.Request(dl_url, headers=HEADERS)

            with urllib.request.urlopen(dl_req, timeout=30) as dl_resp:
                content = dl_resp.read()
            with open(save_path, 'wb') as out:
                out.write(content)

            size_kb = len(content) // 1024
            print(f'  [OK] {prod[:35]:<35} | {fname} ({size_kb} KB)')
            downloaded += 1
            prod_downloaded += 1
            manifest.append({'product': prod, 'file': fname, 'local': safe_name, 'status': 'downloaded', 'size_kb': size_kb})

        if prod_downloaded == 0 and not any(m['product'] == prod for m in manifest):
            print(f'  [EMPTY] {prod[:50]}')

    except Exception as e:
        print(f'  [ERR] {prod[:40]}: {e}')
        errors += 1

with open(os.path.join(SAVE_DIR, '_manifest.json'), 'w', encoding='utf-8') as mf:
    json.dump(manifest, mf, indent=2, ensure_ascii=False)

print()
print('=== RESUMEN ===')
print(f'Descargados: {downloaded}')
print(f'Errores: {errors}')
print(f'Total en manifest: {len(manifest)}')
