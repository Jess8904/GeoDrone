"""Conexion con NodeODM: enviar fotos, consultar avance, descargar resultados."""
import glob
import os
from pyodm import Node
from . import config


def get_node() -> Node:
    return Node(config.NODEODM_HOST, config.NODEODM_PORT)


def submit(photos_dir: str, options: dict | None = None) -> str:
    """Crea la tarea en NodeODM y regresa su uuid (el backend lo guarda)."""
    files = sorted(
        glob.glob(os.path.join(photos_dir, "*.jpg"))
        + glob.glob(os.path.join(photos_dir, "*.JPG"))
        + glob.glob(os.path.join(photos_dir, "*.jpeg"))
    )
    if len(files) < 5:
        raise ValueError(f"Se necesitan mas fotos (encontre {len(files)}) en {photos_dir}")
    task = get_node().create_task(files, {**config.ODM_OPTIONS, **(options or {})})
    return task.uuid


def status(uuid: str) -> dict:
    """Estado para la pantalla de procesamiento de la app."""
    info = get_node().get_task(uuid).info()
    # status.code: 10 en cola, 20 corriendo, 30 fallo, 40 completo, 50 cancelado
    return {
        "uuid": uuid,
        "code": info.status.value,
        "progress": info.progress,
        "processing_time_ms": info.processing_time,
        "last_error": info.last_error or None,
    }


def wait(uuid: str, on_progress=None):
    task = get_node().get_task(uuid)
    task.wait_for_completion(status_callback=on_progress)
    return task


def download(uuid: str, dest: str) -> str:
    """Descarga todos los resultados a `dest` y regresa la carpeta."""
    os.makedirs(dest, exist_ok=True)
    get_node().get_task(uuid).download_assets(dest)
    return dest


def cancel(uuid: str):
    get_node().get_task(uuid).cancel()
