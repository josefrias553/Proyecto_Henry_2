from db import create_tables
from loaders.load_usuarios import load_usuarios
from loaders.load_categorias import load_categorias
from loaders.load_metodos_pago import load_metodos_pago
from loaders.load_productos import load_productos
from loaders.load_direcciones_envio import load_direcciones_envio
from loaders.load_carrito import load_carrito
from loaders.load_ordenes import load_ordenes
from loaders.load_detalle_ordenes import load_detalle_ordenes
from loaders.load_ordenes_metodos_pago import load_ordenes_metodos_pago
from loaders.load_resenas_productos import load_resenas_productos
from loaders.load_historial_pagos import load_historial_pagos



def main():
    create_tables()

    load_usuarios()
    load_categorias()
    load_metodos_pago()
    load_productos()
    load_direcciones_envio()
    load_carrito()
    load_ordenes()
    load_detalle_ordenes()
    load_ordenes_metodos_pago()
    load_resenas_productos()
    load_historial_pagos()

if __name__ == "__main__":
    main()
