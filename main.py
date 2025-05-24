from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json

with open("dvf_nice_2023_2024.json", "r", encoding="utf-8") as f:
    ventes = json.load(f)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/estimation")
def estimation(adresse: str = Query(...), surface: float = Query(...)):
    rue = adresse.lower().strip().replace("'", "").replace(",", "").replace(".", "")
    surface = float(surface)

    resultats = []
    for v in ventes:
        if not v.get("Adresse") or not v.get("surface") or not v.get("valeur_fonciere"):
            continue
        try:
            if rue in v["Adresse"].lower() and abs(v["surface"] - surface) <= surface * 0.25:
                resultats.append(v)
                if len(resultats) >= 50:
                    break
        except:
            continue

    if not resultats:
        return JSONResponse(content={"message": "Pas de ventes comparables"}, status_code=404)

    prix_m2_list = [v["valeur_fonciere"] / v["surface"] for v in resultats if v["surface"]]
    prix_m2_moyen = sum(prix_m2_list) / len(prix_m2_list)

    return {
        "estimation_min": round(prix_m2_moyen * surface * 0.95),
        "estimation_max": round(prix_m2_moyen * surface * 1.05),
        "ventes_comparables": len(resultats)
    }
