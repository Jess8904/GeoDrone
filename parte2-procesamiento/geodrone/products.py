"""Post-proceso: mosaicos del mapa, modelo 3D y curvas de nivel."""
import glob
import os
import shutil
import subprocess
from . import config


def _run(cmd: list[str]):
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True)


def _find(root: str, pattern: str) -> str | None:
    hits = glob.glob(os.path.join(root, "**", pattern), recursive=True)
    return hits[0] if hits else None


def make_tiles(ortho_tif: str, out_dir: str, zoom: str | None = None) -> str:
    """Parte el ortomosaico en mosaicos XYZ ({z}/{x}/{y}.png) para el mapa."""
    os.makedirs(out_dir, exist_ok=True)
    _run([
        "gdal2tiles.py", "--xyz", "--processes=4",
        "-z", zoom or config.TILE_ZOOM,
        ortho_tif, out_dir,
    ])
    return out_dir


def make_contours(dsm_tif: str, out_geojson: str,
                  interval: float | None = None) -> str:
    """Curvas de nivel ligeras del DSM, en WGS84 (lat/lon) para el mapa."""
    smooth = out_geojson + ".dsm.tif"
    tmp = out_geojson + ".utm.geojson"
    # El DSM trae ~5 cm/pixel y mucho ruido: se promedia a CONTOUR_SMOOTH_M metros
    _run(["gdalwarp", "-overwrite", "-tr", str(config.CONTOUR_SMOOTH_M),
          str(config.CONTOUR_SMOOTH_M), "-r", "average", dsm_tif, smooth])
    _run(["gdal_contour", "-a", "elev", "-i",
          str(interval or config.CONTOUR_INTERVAL_M),
          "-f", "GeoJSON", smooth, tmp])
    if os.path.exists(out_geojson):
        os.remove(out_geojson)
    _run(["ogr2ogr", "-f", "GeoJSON", "-t_srs", "EPSG:4326",
          "-lco", "COORDINATE_PRECISION=6", out_geojson, tmp])
    os.remove(tmp)
    os.remove(smooth)
    return out_geojson


def export_model(results_dir: str, out_dir: str) -> str | None:
    """Copia el modelo 3D .glb (lo genera ODM con la opcion gltf)."""
    os.makedirs(out_dir, exist_ok=True)
    glb = _find(results_dir, "*.glb")
    if glb:
        dest = os.path.join(out_dir, "model.glb")
        shutil.copy(glb, dest)
        return dest
    # Respaldo: si no hay .glb, deja el .obj texturizado para convertirlo
    obj = _find(results_dir, "odm_textured_model_geo.obj")
    if obj:
        print("AVISO: no hay .glb; convierte el .obj con `obj2gltf -i ... -o model.glb`")
    return None
