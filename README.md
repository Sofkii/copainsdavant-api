# ðŸ“š Documentation â€” `copains-api` (usage personnel)

> **Version** : 1.0.0
> **Auteur** : sofki
> **Usage** : personnel uniquement (pas de publication)
> **Python requis** : â‰¥ 3.10

---

## ðŸ“‹ Table des matiÃ¨res

1. [Introduction](#1-introduction)
2. [PrÃ©requis](#2-prÃ©requis)
3. [Installation locale](#3-installation-locale)
4. [DÃ©marrage rapide](#4-dÃ©marrage-rapide)
5. [Concepts clÃ©s](#5-concepts-clÃ©s)
6. [RÃ©fÃ©rence API](#6-rÃ©fÃ©rence-api)
   - 6.1 [Classe `CopainsClient`](#61-classe-copainsclient)
   - 6.2 [ModÃ¨le `Profil`](#62-modÃ¨le-profil)
   - 6.3 [ModÃ¨le `Parcours`](#63-modÃ¨le-parcours)
   - 6.4 [Exceptions](#64-exceptions)
7. [Fonctions bas niveau (parsers)](#7-fonctions-bas-niveau-parsers)
8. [Constantes](#8-constantes)
9. [Guide d'utilisation](#9-guide-dutilisation)
   - 9.1 [Recherche simple](#91-recherche-simple)
   - 9.2 [Recherche avancÃ©e](#92-recherche-avancÃ©e)
   - 9.3 [Recherche sans parcours (rapide)](#93-recherche-sans-parcours-rapide)
   - 9.4 [Export JSON](#94-export-json)
   - 9.5 [Export CSV](#95-export-csv)
   - 9.6 [Export SQLite](#96-export-sqlite)
   - 9.7 [Traitement par lots](#97-traitement-par-lots)
   - 9.8 [Rate-limiting](#98-rate-limiting)
   - 9.9 [Gestion des erreurs](#99-gestion-des-erreurs)
   - 9.10 [Petit serveur web local (FastAPI)](#910-petit-serveur-web-local-fastapi)
10. [Architecture interne](#10-architecture-interne)
11. [Performance & bonnes pratiques](#11-performance--bonnes-pratiques)
12. [SÃ©lecteurs CSS & maintenance](#12-sÃ©lecteurs-css--maintenance)
13. [DÃ©pannage](#13-dÃ©pannage)
14. [FAQ](#14-faq)
15. [SÃ©curitÃ© & Ã©thique](#15-sÃ©curitÃ©--Ã©thique)

---

## 1. Introduction

`copains-api` est un **module Python personnel** permettant d'interroger le site **Copains d'avant** (`copainsdavant.linternaute.com`) pour rÃ©cupÃ©rer :

- Les **profils** correspondant Ã  des critÃ¨res (prÃ©nom, nom, ville, annÃ©e de naissance) ;
- Le **parcours scolaire et professionnel** associÃ© Ã  chaque profil (Ã©tablissements, villes, dates).

**Objectif** : usage perso (recherche gÃ©nÃ©alogique, curiositÃ©, retrouver d'anciens camarades).

> âš ï¸ **Ce module n'est pas affiliÃ©** Ã  Copains d'avant ni Ã  Linternaute. Il utilise du **scraping HTML**. Utilise-le de maniÃ¨re **raisonnable**.

---

## 2. PrÃ©requis

| Ã‰lÃ©ment | Version minimale |
|---|---|
| Python | 3.10 |
| pip | 23.0 |
| Connexion internet | âœ… |

**DÃ©pendances** :
- `aiohttp>=3.9`
- `beautifulsoup4>=4.12`

---

## 3. Installation locale

### 3.1 CrÃ©er un dossier pour ton projet

```bash
mkdir ~/copains-api
cd ~/copains-api
```

### 3.2 CrÃ©er un environnement virtuel (recommandÃ©)

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3.3 Installer les dÃ©pendances

```bash
pip install aiohttp beautifulsoup4
```

### 3.4 CrÃ©er la structure des fichiers

```
copains-api/
â”œâ”€â”€ .venv/                 (environnement virtuel)
â”œâ”€â”€ copains_api/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ constants.py
â”‚   â”œâ”€â”€ exceptions.py
â”‚   â”œâ”€â”€ models.py
â”‚   â”œâ”€â”€ parsers.py
â”‚   â””â”€â”€ client.py
â”œâ”€â”€ scripts/
â”‚   â”œâ”€â”€ recherche.py
â”‚   â””â”€â”€ export.py
â””â”€â”€ resultats/             (dossier pour tes exports)
```

Copie le code des fichiers `copains_api/*.py` (voir la section [Architecture interne](#10-architecture-interne)).

### 3.5 VÃ©rification

```bash
python -c "from copains_api import CopainsClient; print('âœ… OK')"
```

---

## 4. DÃ©marrage rapide

CrÃ©e un fichier `scripts/recherche.py` :

```python
import asyncio
from copains_api import CopainsClient

async def main():
    async with CopainsClient() as client:
        profils = await client.rechercher(
            prenom="Jean",
            nom="Dupont",
            ville="BesanÃ§on",
            annee="1980",
        )

        for p in profils:
            print(f"ðŸ‘¤ {p.nom} â€” {p.lieu} ({p.type})")
            print(f"   ðŸ”— {p.url}")
            for parc in p.parcours:
                print(f"   ðŸŽ“ [{parc.categorie}] {parc.etablissement} "
                      f"â€” {parc.ville} ({parc.dates})")

if __name__ == "__main__":
    asyncio.run(main())
```

**Lancer** :
```bash
python scripts/recherche.py
```

**Sortie attendue** :
```
ðŸ‘¤ Jean Dupont â€” BesanÃ§on (25) (LycÃ©e)
   ðŸ”— https://copainsdavant.linternaute.com/profil/...
   ðŸŽ“ [LycÃ©e] LycÃ©e Victor Hugo â€” BesanÃ§on (1995 - 1998)
   ðŸŽ“ [UniversitÃ©] UniversitÃ© de Franche-ComtÃ© â€” BesanÃ§on (1998 - 2001)
```

---

## 5. Concepts clÃ©s

| Concept | Description |
|---|---|
| **Client** | `CopainsClient` est le point d'entrÃ©e. Il gÃ¨re la session HTTP et expose `rechercher()`. |
| **Profil** | ReprÃ©sente un utilisateur trouvÃ© (`nom`, `url`, `lieu`, `type`, `parcours`). |
| **Parcours** | Une entrÃ©e du CV (`categorie`, `etablissement`, `ville`, `dates`). |
| **Enrichissement** | AprÃ¨s la recherche, chaque profil est visitÃ© pour rÃ©cupÃ©rer son parcours. |
| **Session** | Utilise `async with CopainsClient() as client:` pour une gestion propre. |

---

## 6. RÃ©fÃ©rence API

### 6.1 Classe `CopainsClient`

#### Constructeur
```python
CopainsClient(
    timeout: int = 15,
    enrichir_parcours: bool = True,
    headers: dict[str, str] | None = None,
)
```

| ParamÃ¨tre | Type | DÃ©faut | Description |
|---|---|---|---|
| `timeout` | `int` | `15` | Timeout HTTP en secondes par requÃªte. |
| `enrichir_parcours` | `bool` | `True` | Si `False`, une seule requÃªte HTTP est faite par recherche (pas de parcours â†’ plus rapide). |
| `headers` | `dict \| None` | `None` | En-tÃªtes HTTP personnalisÃ©s. Par dÃ©faut : navigateur FR. |

#### MÃ©thodes

##### `async rechercher(...)`
```python
async def rechercher(
    prenom: str = "",
    nom: str = "",
    ville: str = "",
    annee: str = "",
    delta: int = 5,
) -> list[Profil]
```

| ParamÃ¨tre | Type | DÃ©faut | Description |
|---|---|---|---|
| `prenom` | `str` | `""` | PrÃ©nom recherchÃ©. |
| `nom` | `str` | `""` | Nom de famille. |
| `ville` | `str` | `""` | Filtre ville (optionnel). |
| `annee` | `str` | `""` | AnnÃ©e de naissance (optionnel). |
| `delta` | `int` | `5` | TolÃ©rance d'annÃ©es autour de `annee`. |

**Retour** : `list[Profil]` â€” liste vide en cas d'erreur rÃ©seau.

##### Context manager
```python
async with CopainsClient() as client:
    ...
```
Ouvre automatiquement une `aiohttp.ClientSession` et la ferme Ã  la sortie.

---

### 6.2 ModÃ¨le `Profil`

```python
@dataclass(slots=True)
class Profil:
    nom: str
    url: str
    id: str | None = None
    lieu: str | None = None
    type: str | None = None
    parcours: list[Parcours] = field(default_factory=list)
```

| Attribut | Type | Description |
|---|---|---|
| `nom` | `str` | Nom affichÃ© du profil. |
| `url` | `str` | URL absolue du profil Copains d'avant. |
| `id` | `str \| None` | Identifiant interne (`data-id`). |
| `lieu` | `str \| None` | Ville / rÃ©gion affichÃ©e. |
| `type` | `str \| None` | Type d'Ã©tablissement affichÃ©. |
| `parcours` | `list[Parcours]` | Liste du parcours enrichi. |

**MÃ©thode** : `to_dict() -> dict` (sÃ©rialisation JSON).

---

### 6.3 ModÃ¨le `Parcours`

```python
@dataclass(slots=True)
class Parcours:
    categorie: str
    etablissement: str | None = None
    ville: str | None = None
    dates: str | None = None
```

| Attribut | Type | Description |
|---|---|---|
| `categorie` | `str` | CatÃ©gorie (ex: "LycÃ©e", "UniversitÃ©"). |
| `etablissement` | `str \| None` | Nom de l'Ã©tablissement. |
| `ville` | `str \| None` | Ville de l'Ã©tablissement. |
| `dates` | `str \| None` | PÃ©riode (ex: "1995 - 1998"). |

**MÃ©thode** : `to_dict() -> dict`.

---

### 6.4 Exceptions

| Exception | HÃ©rite de | Description |
|---|---|---|
| `CopainsError` | `Exception` | Base de toutes les erreurs. |
| `CopainsNetworkError` | `CopainsError` | Timeout, statut HTTP, connexion. |
| `CopainsParseError` | `CopainsError` | Structure HTML inattendue. |

**Import** :
```python
from copains_api import CopainsError, CopainsNetworkError, CopainsParseError
```

---

## 7. Fonctions bas niveau (parsers)

Ces fonctions sont utilisables directement si tu veux parser du HTML toi-mÃªme.

### `extraire_parcours(html: str) -> list[Parcours]`
Parse une page de profil et retourne la liste des `Parcours`.

### `extraire_profils(html: str) -> list[Profil]`
Parse une page de rÃ©sultats et retourne la liste des `Profil` (sans parcours).

**Exemple** :
```python
from copains_api.parsers import extraire_profils, extraire_parcours

html = "<html>...</html>"
profils = extraire_profils(html)

html_profil = "<html>...</html>"
parcours = extraire_parcours(html_profil)
```

---

## 8. Constantes

Importables depuis `copains_api.constants` :

| Constante | Type | Valeur |
|---|---|---|
| `COPAINS_BASE` | `str` | `"https://copainsdavant.linternaute.com"` |
| `HEADERS_COPAINS` | `dict` | UA navigateur + `Accept-Language: fr-FR` |
| `DEFAULT_TIMEOUT` | `int` | `15` |
| `DEFAULT_DELTA` | `int` | `5` |

---

## 9. Guide d'utilisation

### 9.1 Recherche simple

```python
import asyncio
from copains_api import CopainsClient

async def main():
    async with CopainsClient() as client:
        profils = await client.rechercher(prenom="Jean", nom="Dupont")
        for p in profils:
            print(p.nom, "â€”", p.lieu)

asyncio.run(main())
```

### 9.2 Recherche avancÃ©e

```python
profils = await client.rechercher(
    prenom="Marie",
    nom="Martin",
    ville="Paris",
    annee="1985",
    delta=2,  # tolÃ©rance Â±2 ans
)
```

### 9.3 Recherche sans parcours (rapide)

Utile si tu veux juste la liste des profils sans visiter chaque page.

```python
async with CopainsClient(enrichir_parcours=False) as client:
    profils = await client.rechercher(nom="Dupont")
    # 1 seule requÃªte HTTP
```

### 9.4 Export JSON

```python
import asyncio, json
from copains_api import CopainsClient

async def main():
    async with CopainsClient() as client:
        profils = await client.rechercher(prenom="Marie", nom="Martin")

    data = [p.to_dict() for p in profils]
    with open("resultats/martin.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"âœ… {len(data)} profil(s) exportÃ©(s)")

asyncio.run(main())
```

### 9.5 Export CSV

```python
import asyncio, csv
from copains_api import CopainsClient

async def main():
    async with CopainsClient() as client:
        profils = await client.rechercher(nom="Dupont")

    with open("resultats/dupont.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["nom", "lieu", "type", "url",
                         "categorie", "etablissement", "ville", "dates"])
        for p in profils:
            for parc in p.parcours or [None]:
                writer.writerow([
                    p.nom, p.lieu, p.type, p.url,
                    parc.categorie if parc else "",
                    parc.etablissement if parc else "",
                    parc.ville if parc else "",
                    parc.dates if parc else "",
                ])

    print(f"âœ… Export CSV terminÃ©")

asyncio.run(main())
```

### 9.6 Export SQLite

```python
import asyncio, sqlite3, json
from copains_api import CopainsClient

async def main():
    async with CopainsClient() as client:
        profils = await client.rechercher(nom="Dupont")

    conn = sqlite3.connect("resultats/copains.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS profils (
            id TEXT, nom TEXT, lieu TEXT, type TEXT, url TEXT,
            parcours_json TEXT
        )
    """)
    for p in profils:
        c.execute(
            "INSERT INTO profils VALUES (?, ?, ?, ?, ?, ?)",
            (p.id, p.nom, p.lieu, p.type, p.url,
             json.dumps([x.to_dict() for x in p.parcours], ensure_ascii=False))
        )
    conn.commit()
    conn.close()
    print(f"âœ… {len(profils)} profil(s) insÃ©rÃ©(s) dans copains.db")

asyncio.run(main())
```

### 9.7 Traitement par lots

```python
import asyncio
from copains_api import CopainsClient

async def chercher(client, prenom):
    return await client.rechercher(prenom=prenom, nom="Dupont")

async def main():
    prenoms = ["Jean", "Marie", "Paul", "Lucie", "Anne"]
    async with CopainsClient() as client:
        resultats = await asyncio.gather(*(chercher(client, p) for p in prenoms))
        for p, r in zip(prenoms, resultats):
            print(f"{p} : {len(r)} profil(s)")

asyncio.run(main())
```

### 9.8 Rate-limiting

Pour Ã©viter de te faire bloquer par le site, limite le nombre de requÃªtes simultanÃ©es :

```python
import asyncio
from copains_api import CopainsClient

sem = asyncio.Semaphore(3)  # max 3 requÃªtes simultanÃ©es

async def chercher(client, prenom):
    async with sem:
        return await client.rechercher(prenom=prenom, nom="Dupont")

async def main():
    async with CopainsClient() as client:
        await asyncio.gather(*(chercher(client, p) for p in ["Jean", "Marie", "Paul"]))

asyncio.run(main())
```

### 9.9 Gestion des erreurs

```python
from copains_api import CopainsClient, CopainsNetworkError

async with CopainsClient() as client:
    try:
        profils = await client.rechercher(nom="Dupont")
    except CopainsNetworkError as e:
        print("Erreur rÃ©seau :", e)
    else:
        if not profils:
            print("Aucun rÃ©sultat (ou erreur silencieuse).")
```

> ðŸ’¡ **Astuce** : `rechercher()` ne lÃ¨ve **jamais** d'exception rÃ©seau â€” il retourne `[]`. Si tu veux gÃ©rer les erreurs finement, appelle directement `client._get_html()`.

### 9.10 Petit serveur web local (FastAPI)

Si tu veux tester depuis un navigateur :

```python
# scripts/serveur.py
from fastapi import FastAPI, HTTPException
from copains_api import CopainsClient

app = FastAPI()

@app.get("/search")
async def search(prenom: str = "", nom: str = "", ville: str = "", annee: str = ""):
    async with CopainsClient() as client:
        profils = await client.rechercher(
            prenom=prenom, nom=nom, ville=ville, annee=annee
        )
    if not profils:
        raise HTTPException(status_code=404, detail="Aucun profil trouvÃ©")
    return [p.to_dict() for p in profils]
```

**Installer FastAPI** :
```bash
pip install fastapi uvicorn
```

**Lancer** :
```bash
uvicorn scripts.serveur:app --reload
```

**Tester dans le navigateur** :
```
http://localhost:8000/search?prenom=Jean&nom=Dupont
```

---

## 10. Architecture interne

```
copains_api/
â”œâ”€â”€ __init__.py        â†’ exports publics
â”œâ”€â”€ constants.py       â†’ URLs, headers, defaults
â”œâ”€â”€ exceptions.py      â†’ CopainsError, NetworkError, ParseError
â”œâ”€â”€ models.py          â†’ Profil, Parcours (dataclasses)
â”œâ”€â”€ parsers.py         â†’ extraire_profils, extraire_parcours
â””â”€â”€ client.py          â†’ CopainsClient (orchestrateur)
```

**Flux d'exÃ©cution d'une recherche** :

```
CopainsClient.rechercher()
   â”‚
   â”œâ”€â–º _get_html(URL recherche) â”€â–º aiohttp
   â”‚       â”‚
   â”‚       â””â”€â–º extraire_profils(html)  â”€â”€â”
   â”‚                                     â”‚
   â””â”€â–º pour chaque profil :              â”‚
         _enrichir(profil)               â”‚
            â””â”€â–º _get_html(URL profil)    â”‚
                 â””â”€â–º extraire_parcours â”€â”€â”˜
                                          â”‚
                                          â–¼
                                    list[Profil]
```

---

## 11. Performance & bonnes pratiques

### âš¡ Optimisations

| Astuce | Gain |
|---|---|
| `enrichir_parcours=False` | 1 requÃªte au lieu de N+1 |
| `asyncio.Semaphore(3)` | Ã‰vite rate-limit et blocage |
| Cache local (JSON sur disque) | Ã‰vite requÃªtes redondantes |
| RÃ©utiliser `CopainsClient` | Ã‰vite reconnexion TCP |

### âš ï¸ Ã€ Ã©viter

- âŒ Lancer 100 recherches simultanÃ©es (ban IP).
- âŒ Appeler `rechercher()` sans `async with`.
- âŒ Ignorer les erreurs rÃ©seau.
- âŒ Stocker les `aiohttp.ClientSession` globalement.

### ðŸ“Š Budget requÃªtes

| Action | RequÃªtes HTTP |
|---|---|
| Recherche sans enrichissement | 1 |
| Recherche avec enrichissement | 1 + N profils |
| Parsing HTML seul | 0 |

---

## 12. SÃ©lecteurs CSS & maintenance

Le site peut changer sa structure HTML Ã  tout moment. Voici les sÃ©lecteurs utilisÃ©s :

### Recherche
| Ã‰lÃ©ment | SÃ©lecteur |
|---|---|
| Item de rÃ©sultat | `ul.app_list--result__search li` |
| Bloc (data-id) | `.grid_line` |
| Nom + lien | `h3 a` |
| Lieu | `.app_list--result__search__place` |
| Type | `.app_list--result__search__type` |

### Profil
| Ã‰lÃ©ment | SÃ©lecteur |
|---|---|
| Section parcours | `#jCareerList section` |
| CatÃ©gorie | `h3` |
| Ã‰tablissement | `.jCareerLabel` |
| Ville | `.jCcareerTown` |
| Dates | `.jCareerDate` |

> ðŸ”§ **Si le site change** : modifie uniquement `parsers.py`. Le reste du code n'a pas besoin de bouger.

---

## 13. DÃ©pannage

### ðŸ”´ `CopainsNetworkError: Client non initialisÃ©`
**Cause** : tu as oubliÃ© `async with`.
```python
# âŒ Mauvais
client = CopainsClient()
await client.rechercher(...)

# âœ… Bon
async with CopainsClient() as client:
    await client.rechercher(...)
```

### ðŸ”´ `[]` retournÃ© alors qu'il y a des rÃ©sultats
**Causes possibles** :
1. Le site a changÃ© ses sÃ©lecteurs CSS â†’ vÃ©rifier `parsers.py`.
2. Blocage IP â†’ ralentir avec `asyncio.Semaphore`.
3. Timeout trop court â†’ augmenter `timeout=30`.

### ðŸ”´ Timeouts frÃ©quents
```python
CopainsClient(timeout=30)
```

### ðŸ”´ CaractÃ¨res bizarres dans la sortie
**Cause** : encodage. Utilise toujours `encoding="utf-8"` :
```python
with open("out.json", "w", encoding="utf-8") as f: ...
```

### ðŸ”´ `ModuleNotFoundError: No module named 'aiohttp'`
```bash
pip install aiohttp beautifulsoup4
```

### ðŸ”´ `RuntimeError: asyncio.run() cannot be called from a running event loop`
**Cause** : tu utilises `asyncio.run()` dans un contexte dÃ©jÃ  async (Jupyter, FastAPIâ€¦).
**Solution** : utilise `await` directement dans un contexte async.

---

## 14. FAQ

**Q : Est-ce lÃ©gal ?**
R : Le scraping est un vide juridique. Utilise-le de maniÃ¨re **raisonnable** (pas de spam, pas de revente de donnÃ©es). Respecte les CGU.

**Q : Ã‡a marche pour d'autres pays ?**
R : Non, le site est **franÃ§ais** uniquement.

**Q : Puis-je chercher par nom de jeune fille ?**
R : Pas encore exposÃ© dans l'API. Le paramÃ¨tre `nomjf` existe dans l'URL mais n'est pas branchÃ©. Tu peux modifier `client.py` si besoin.

**Q : Puis-je obtenir l'email/tÃ©lÃ©phone ?**
R : âŒ Non, et c'est illÃ©gal (RGPD). L'API ne rÃ©cupÃ¨re que des donnÃ©es **publiques**.

**Q : Combien de profils max par recherche ?**
R : Le site renvoie ce qu'il veut. L'API ne tronque pas â€” c'est Ã  toi de gÃ©rer.

**Q : Puis-je utiliser avec `requests` (sync) ?**
R : Non, tout est async. Utilise `asyncio.run()` dans un script synchrone.

**Q : Comment cacher mon IP ?**
R : Passe un `aiohttp.ClientSession` avec un proxy custom via `headers`/session.

**Q : Y a-t-il une limite de requÃªtes ?**
R : Non documentÃ©e. Reste sous **1 req/sec** pour Ãªtre safe.

**Q : Puis-je exÃ©cuter plusieurs recherches en parallÃ¨le ?**
R : Oui, avec `asyncio.gather()` + `asyncio.Semaphore` pour limiter.

**Q : Est-ce que Ã§a marche sous Windows ?**
R : Oui, mais utilise `asyncio.run()` et Ã©vite les `ProactorEventLoop` problÃ©matiques. Si souci :
```python
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

---

## 15. SÃ©curitÃ© & Ã©thique

- ðŸ”’ **RGPD** : ne stocke pas les donnÃ©es personnelles sans consentement.
- ðŸš« **Pas de spam** : ne lance pas 1000 requÃªtes/minute.
- ðŸ•µï¸ **Anonymat** : utilise un User-Agent rÃ©aliste (fourni par dÃ©faut).
- ðŸ“œ **CGU** : lis les conditions d'utilisation de Copains d'avant.
- ðŸŽ¯ **Usage** : Ã©ducatif, recherche gÃ©nÃ©alogique **personnelle**, curiositÃ©.

> âš ï¸ L'auteur dÃ©cline toute responsabilitÃ© en cas d'usage abusif.

---

**Fin de la documentation.** ðŸŽ“
