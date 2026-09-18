import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour pouvoir importer copains_api sans l'installer via pip
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from copains_api import CopainsClient

async def main():
    async with CopainsClient() as client:
        print("Recherche en cours pour 'Jean Dupont'...")
        profils = await client.rechercher(
            prenom="Jean",
            nom="Dupont",
        )

        if not profils:
            print("Aucun profil trouvé ou erreur réseau.")
            return

        print(f"Trouvé {len(profils)} profil(s)!")
        for p in profils:
            print(f"\n👤 {p.nom} — {p.lieu} ({p.type})")
            print(f"   🔗 {p.url}")
            if p.parcours:
                for parc in p.parcours:
                    print(f"   🎓 [{parc.categorie}] {parc.etablissement} "
                          f"— {parc.ville} ({parc.dates})")
            else:
                print("   🎓 Aucun parcours trouvé")

if __name__ == "__main__":
    # Fix for proactor event loop in Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
