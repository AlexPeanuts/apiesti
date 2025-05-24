
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import math

# Charger les ventes géolocalisées
with open("dvf_nice_2023_2024_geo.json", "r", encoding="utf-8") as f:
    ventes = json.load(f)

app = FastAPI()

# Activer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Formule de Haversine
def distance(lat1, lon1, lat2, lon2):
    R = 6371e3  # rayon de la Terre en mètres
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # distance en mètres

# Estimation
@app.get("/estimation")
def estimation(
    lat: float = Query(...),
    lon: float = Query(...),
    surface: float = Query(...),
    pieces: int = Query(...)
):
    rayons = [50, 100, 200]
    ventes_filtrees = []

    # Déterminer la catégorie de surface
    if surface <= 30:
        min_surf, max_surf = 0, 35
    elif surface > 90:
        min_surf, max_surf = 75, 999
    else:
        min_surf, max_surf = surface * 0.75, surface * 1.25

    for rayon in rayons:
        ventes_filtrees = []
        for v in ventes:
            try:
                if "lat" not in v or "lon" not in v or not v.get("valeur_fonciere") or not v.get("surface"):
                    continue
                d = distance(lat, lon, v["lat"], v["lon"])
                if d <= rayon and min_surf <= v["surface"] <= max_surf:
                    if abs(v.get("nombre_pieces", pieces) - pieces) <= 1:
                        ventes_filtrees.append(v)
            except:
                continue
        if len(ventes_filtrees) >= 3:
            break

    if not ventes_filtrees:
        return JSONResponse(content={"message": "Aucune vente comparable trouvée"}, status_code=404)

    prix_m2_list = [v["valeur_fonciere"] / v["surface"] for v in ventes_filtrees]
    prix_m2_moyen = sum(prix_m2_list) / len(prix_m2_list)

    return {
        "estimation_min": round(prix_m2_moyen * surface * 0.95),
        "estimation_max": round(prix_m2_moyen * surface * 1.05),
        "ventes_comparables": len(ventes_filtrees),
        "rayon_utilise": rayon
    }
