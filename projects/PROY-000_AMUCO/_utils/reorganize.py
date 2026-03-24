import os, json, shutil

SAVE_DIR = r'C:\Users\thoma\Desktop\Claude\PROY-005_Agente_IA_AMUCO\fichas_tecnicas'

with open(os.path.join(SAVE_DIR, '_manifest.json'), 'r', encoding='utf-8') as f:
    manifest = json.load(f)

INVALID_CHARS = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']

moved = 0
for entry in manifest:
    if entry['status'] not in ('downloaded', 'exists'):
        continue
    prod = entry['product']
    local_name = entry['local']
    src = os.path.join(SAVE_DIR, local_name)
    if not os.path.exists(src):
        continue

    safe_prod = prod
    for ch in INVALID_CHARS:
        safe_prod = safe_prod.replace(ch, '-')

    dest_dir = os.path.join(SAVE_DIR, safe_prod)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, entry['file'])
    shutil.move(src, dest)
    moved += 1

print(f'Reorganizados: {moved} archivos en subcarpetas por producto')
