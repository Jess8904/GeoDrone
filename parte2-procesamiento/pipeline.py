#!/usr/bin/env python3
"""Pipeline completo de un vuelo.

Ejemplos:
  python pipeline.py run ./fotos/aukerman ./salida/vuelo1
  python pipeline.py status <uuid>
  python pipeline.py post <uuid> ./salida/vuelo1     # si ya termino y solo falta post-proceso
"""
import argparse
import os
import sys
from geodrone import odm_client, products


def post(uuid: str, out: str):
    raw = os.path.join(out, "odm")
    odm_client.download(uuid, raw)
    ortho = products._find(raw, "odm_orthophoto.tif")
    dsm = products._find(raw, "dsm.tif")
    if not ortho or not dsm:
        sys.exit("Faltan odm_orthophoto.tif o dsm.tif. Revisa que dsm=True.")
    products.make_tiles(ortho, os.path.join(out, "tiles"))
    products.make_contours(dsm, os.path.join(out, "contours.geojson"))
    products.export_model(raw, os.path.join(out, "model"))
    print("\nListo. Productos en", out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("photos"); r.add_argument("out")
    s = sub.add_parser("status"); s.add_argument("uuid")
    p = sub.add_parser("post"); p.add_argument("uuid"); p.add_argument("out")
    a = ap.parse_args()

    if a.cmd == "status":
        print(odm_client.status(a.uuid))
    elif a.cmd == "post":
        post(a.uuid, a.out)
    else:
        uuid = odm_client.submit(a.photos)
        print("Tarea creada:", uuid)
        odm_client.wait(uuid, lambda i: print(f"  {i.progress:.0f}%"))
        post(uuid, a.out)


if __name__ == "__main__":
    main()
