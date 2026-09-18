import asyncio
import json
import csv
import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from copains_api import CopainsClient

async def export_json(profils, filename="resultats/export.json"):
    data = [p.to_dict() for p in profils]
    # S'assurer que le dossier existe
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ {len(data)} profil(s) exporté(s) dans {filename}")

async def export_csv(profils, filename="resultats/export.csv"):
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["nom", "lieu", "type", "url",
                         "categorie", "etablissement", "ville", "dates"])
        for p in profils:
            if not p.parcours:
                writer.writerow([p.nom, p.lieu, p.type, p.url, "", "", "", ""])
            else:
                for parc in p.parcours:
                    writer.writerow([
                        p.nom, p.lieu, p.type, p.url,
                        parc.categorie,
                        parc.etablissement,
                        parc.ville,
                        parc.dates,
                    ])
    print(f"✅ Export CSV terminé dans {filename}")

async def main():
    async with CopainsClient() as client:
        print("Recherche de 'Martin'...")
        # On limite aux résultats sans enrichissement pour l'exemple rapide,
        # ou on peut laisser l'enrichissement en retirant enrichir_parcours=False du init.
        profils = await client.rechercher(nom="Martin")

    if profils:
        await export_json(profils)
        await export_csv(profils)
    else:
        print("Aucun profil à exporter.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
