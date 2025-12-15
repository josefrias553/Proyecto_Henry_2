import os
import re

MAPPING = {
    "load_usuarios.py": "usuarios.csv",
    "load_categorias.py": "categorias.csv",
    "load_metodos_pago.py": "metodos_pago.csv",
    "load_productos.py": "productos.csv",
    "load_direcciones_envio.py": "direcciones_envio.csv",
    "load_carrito.py": "carrito.csv",
    "load_ordenes.py": "ordenes.csv",
    "load_detalle_ordenes.py": "detalle_ordenes.csv",
    "load_ordenes_metodos_pago.py": "ordenes_metodos_pago.csv",
    "load_resenas_productos.py": "resenas_productos.csv",
    "load_historial_pagos.py": "historial_pagos.csv"
}

LOADERS_DIR = "loaders"

def update_loaders():
    for filename, csv_name in MAPPING.items():
        filepath = os.path.join(LOADERS_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Skipping {filename}, not found.")
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            

        new_content = re.sub(
            r'CSV_PATH = get_csv_path\(".*?"\)',
            f'CSV_PATH = get_csv_path("{csv_name}")',
            content
        )
        
        if content != new_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated {filename}")
        else:
            print(f"No changes for {filename}")

if __name__ == "__main__":
    update_loaders()
