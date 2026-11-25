import os

NODEODM_HOST = os.getenv("NODEODM_HOST", "localhost")
NODEODM_PORT = int(os.getenv("NODEODM_PORT", "3000"))

# Opciones de OpenDroneMap. dsm=True es obligatorio: de ahi salen las alturas
# (Parte 4) y las curvas de nivel.
ODM_OPTIONS = {
    "dsm": True,              # modelo digital de superficie (alturas)
    "gltf": True,             # modelo 3D en .glb (lo lee Three.js directo)
    "orthophoto-resolution": 5,   # cm/pixel; mas bajo = mas detalle y mas lento
    "pc-quality": "medium",
    "feature-quality": "medium",
    "resize-to": 2048,
    "fast-orthophoto": False,     # True solo para pruebas rapidas (sin 3D)
}

# Niveles de zoom para los mosaicos del mapa
TILE_ZOOM = os.getenv("TILE_ZOOM", "14-21")
CONTOUR_INTERVAL_M = float(os.getenv("CONTOUR_INTERVAL_M", "2"))
CONTOUR_SMOOTH_M = float(os.getenv("CONTOUR_SMOOTH_M", "1"))  # tamaño de pixel al suavizar el DSM
