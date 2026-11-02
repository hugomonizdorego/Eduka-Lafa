# Map data

* `posts.json` — the 65 administrative posts, derived from geoBoundaries gbOpen TLS ADM2, source: WHO, OCHA ROAP,
  licence: Creative Commons Attribution 3.0 Intergovernmental Organisations (CC BY 3.0 IGO) (https://data.humdata.org/dataset/timor-leste-administrative-boundaries-levels-0-3).
* `municipalities.json` — the 14 municipalities, each the union of its posts (official list of posts per
  municipality in tools/make-map.py), same source and licence. Ataúro is shown as the municipality created in 2022.
  Post boundaries may predate the administrative changes of 2022.
* geoBoundaries: Runfola, D. et al. (2020) geoBoundaries: A global database of political administrative
  boundaries. PLoS ONE 15(4): e0231866. https://www.geoboundaries.org

Simplified with tools/make-map.py; coordinates are WGS84 longitude/latitude.
