# GeoDrone · Parte 2: Procesamiento y servidor

Convierte las fotos de un vuelo en ortomosaico, modelo de alturas (DSM), mosaicos
para el mapa, modelo 3D (.glb) y curvas de nivel (GeoJSON).

## 1. Primer paso (esta semana)
1. Instala Docker y levanta NodeODM:
   `docker compose up -d`  -> abre http://localhost:3000 (debe verse la interfaz de NodeODM).
2. Baja las fotos de prueba: github.com/OpenDroneMap/odm_data_aukerman (carpeta `images`).
3. Instala dependencias: `pip install -r requirements.txt`
   y GDAL (`gdal2tiles.py`, `gdal_contour`, `ogr2ogr`; en Ubuntu: `sudo apt install gdal-bin python3-gdal`).
4. Corre todo: `python pipeline.py run ./fotos/aukerman ./salida/vuelo1`

## 2. Salida
salida/vuelo1/
  odm/                resultados crudos de ODM (orthophoto, dsm.tif, nube de puntos .laz)
  tiles/{z}/{x}/{y}.png   mosaicos XYZ -> la app los usa como capa del mapa (Parte 3)
  contours.geojson    curvas de nivel en lat/lon
  model/model.glb     modelo 3D para el visor Three.js (Parte 3)

## 3. Que debe hacer el backend (acordar con Parte 1)
- `POST /flights/:id/process`  -> `odm_client.submit(carpeta_fotos)`, guarda el uuid.
- `GET  /flights/:id/status`   -> `odm_client.status(uuid)` (code 40 = listo).
- Al terminar: `pipeline.post(uuid, carpeta_salida)` y guarda rutas en la tabla de modelos 3D.
- Sirve `tiles/` como archivos estaticos.
Opciones: llamar estos scripts como proceso hijo desde Node, o envolverlos en un
servicio pequeno (FastAPI) en el mismo servidor.

## 4. Notas
- Necesita >= 16 GB de RAM. Con pocas fotos (<50) usa `fast-orthophoto: True` para pruebas.
- Si GDAL no esta instalado, corre post-proceso dentro de contenedor: `ghcr.io/osgeo/gdal`.
- El .glb queda en coordenadas locales del modelo; guarda tambien el origen
  (odm_georeferencing/coords.txt) para ubicarlo en el mapa.
- Fotos de entrada: .jpg con GPS en EXIF y 70-80 % de traslape.
