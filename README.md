# 📚 Documentation — `copains-api` (usage personnel)

> **Version** : 1.0.0
> **Auteur** : sofki
> **Usage** : personnel uniquement (pas de publication)
> **Python requis** : ≥ 3.10

---

## 📋 Table des matières

1. [Introduction](#1-introduction)
2. [Prérequis](#2-prérequis)
3. [Installation locale](#3-installation-locale)
4. [Démarrage rapide](#4-démarrage-rapide)
5. [Concepts clés](#5-concepts-clés)
6. [Référence API](#6-référence-api)
   - 6.1 [Classe `CopainsClient`](#61-classe-copainsclient)
   - 6.2 [Modèle `Profil`](#62-modèle-profil)
   - 6.3 [Modèle `Parcours`](#63-modèle-parcours)
   - 6.4 [Exceptions](#64-exceptions)
7. [Fonctions bas niveau (parsers)](#7-fonctions-bas-niveau-parsers)
8. [Constantes](#8-constantes)
9. [Guide d'utilisation](#9-guide-dutilisation)
   - 9.1 [Recherche simple](#91-recherche-simple)
   - 9.2 [Recherche avancée](#92-recherche-avancée)
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
12. [Sélecteurs CSS & maintenance](#12-sélecteurs-css--maintenance)
13. [Dépannage](#13-dépannage)
14. [FAQ](#14-faq)
15. [Sécurité & éthique](#15-sécurité--éthique)

---

## 1. Introduction

`copains-api` est un **module Python personnel** permettant d'interroger le site **Copains d'avant** (`copainsdavant.linternaute.com`) pour récupérer :

- Les **profils** correspondant à des critères (prénom, nom, ville, année de naissance) ;
- Le **parcours scolaire et professionnel** associé à chaque profil (établissements, villes, dates).

**Objectif** : usage perso (recherche généalogique, curiosité, retrouver d'anciens camarades).

> ⚠️ **Ce module n'est pas affilié** à Copains d'avant ni à Linternaute. Il utilise du **scraping HTML**. Utilise-le de manière **raisonnable**.

---

## 2. Prérequis

| Élément | Version minimale |
|---|---|
| Python | 3.10 |
| pip | 23.0 |
| Connexion internet | ✅ |

**Dépendances** :
- `aiohttp>=3.9`
- `beautifulsoup4>=4.12`

---

## 3. Installation locale

### 3.1 Créer un dossier pour ton projet

```bash
mkdir ~/copains-api
cd ~/copains-api
```

### 3.2 Créer un environnement virtuel (recommandé)

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3.3 Installer les dépendances

```bash
pip install aiohttp beautifulsoup4
```

### 3.4 Créer la structure des fichiers

```
copains-api/
├── .venv/                 (environnement virtuel)
├── copains_api/
│   ├── __init__.py
│   ├── constants.py
│   ├── exceptions.py
│   ├── models.py
│   ├── parsers.py
│   └── client.py
├── mes_scripts/
│   ├── recherche.py
│   └── export.py
└── resultats/             (dossier pour tes exports)
```

Copie le code des fichiers `copains_api/*.py` (voir la section [Architecture interne](#10-architecture-interne)).

### 3.5 Vérification

```bash
python -c "from copains_api import CopainsClient; print('✅ OK')"
```

---

## 4. Démarrage rapide

Crée un fichier `mes_scripts/recherche.py` :

```python
import asyncio
from copains_api import CopainsClient

async def main():
    async with CopainsClient() as client:
        profils = await client.rechercher(
            prenom="Jean",
            nom="Dupont",
            ville="Besançon",
            annee="1980",
        )

        for p in profils:
            print(f"👤 {p.nom} — {p.lieu} ({p.type})")
            print(f"   🔗 {p.url}")
            for parc in p.parcours:
                print(f"   🎓 [{parc.categorie}] {parc.etablissement} "
                      f"— {parc.ville} ({parc.dates})")

if __name__ == "__main__":
    asyncio.run(main())
```

**Lancer** :
```bash
python mes_scripts/recherche.py
```

**Sortie attendue** :
```
👤 Jean Dupont — Besançon (25) (Lycée)
   🔗 https://copainsdavant.linternaute.com/profil/...
   🎓 [Lycée] Lycée Victor Hugo — Besançon (1995 - 1998)
   🎓 [Université] Université de Franche-Comté — Besançon (1998 - 2001)
```

---

## 5. Concepts clés

| Concept | Description |
|---|---|
| **Client** | `CopainsClient` est le point d'entrée. Il gère la session HTTP et expose `rechercher()`. |
| **Profil** | Représente un utilisateur trouvé (`nom`, `url`, `lieu`, `type`, `parcours`). |
| **Parcours** | Une entrée du CV (`categorie`, `etablissement`, `ville`, `dates`). |
| **Enrichissement** | Après la recherche, chaque profil est visité pour récupérer son parcours. |
| **Session** | Utilise `async with CopainsClient() as client:` pour une gestion propre. |

---

## 6. Référence API

### 6.1 Classe `CopainsClient`

#### Constructeur
```python
CopainsClient(
    timeout: int = 15,
    enrichir_parcours: bool = True,
    headers: dict[str, str] | None = None,
)
```

| Paramètre | Type | Défaut | Description |
|---|---|---|---|
| `timeout` | `int` | `15` | Timeout HTTP en secondes par requête. |
| `enrichir_parcours` | `bool` | `True` | Si `False`, une seule requête HTTP est faite par recherche (pas de parcours → plus rapide). |
| `headers` | `dict \| None` | `None` | En-têtes HTTP personnalisés. Par défaut : navigateur FR. |

#### Méthodes

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

| Paramètre | Type | Défaut | Description |
|---|---|---|---|
| `prenom` | `str` | `""` | Prénom recherché. |
| `nom` | `str` | `""` | Nom de famille. |
| `ville` | `str` | `""` | Filtre ville (optionnel). |
| `annee` | `str` | `""` | Année de naissance (optionnel). |
| `delta` | `int` | `5` | Tolérance d'années autour de `annee`. |

**Retour** : `list[Profil]` — liste vide en cas d'erreur réseau.

##### Context manager
```python
async with CopainsClient() as client:
    ...
```
Ouvre automatiquement une `aiohttp.ClientSession` et la ferme à la sortie.

---

### 6.2 Modèle `Profil`

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
| `nom` | `str` | Nom affiché du profil. |
| `url` | `str` | URL absolue du profil Copains d'avant. |
| `id` | `str \| None` | Identifiant interne (`data-id`). |
| `lieu` | `str \| None` | Ville / région affichée. |
| `type` | `str \| None` | Type d'établissement affiché. |
| `parcours` | `list[Parcours]` | Liste du parcours enrichi. |

**Méthode** : `to_dict() -> dict` (sérialisation JSON).

---

### 6.3 Modèle `Parcours`

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
| `categorie` | `str` | Catégorie (ex: "Lycée", "Université"). |
| `etablissement` | `str \| None` | Nom de l'établissement. |
| `ville` | `str \| None` | Ville de l'établissement. |
| `dates` | `str \| None` | Période (ex: "1995 - 1998"). |

**Méthode** : `to_dict() -> dict`.

---

### 6.4 Exceptions

| Exception | Hérite de | Description |
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

Ces fonctions sont utilisables directement si tu veux parser du HTML toi-même.

### `extraire_parcours(html: str) -> list[Parcours]`
Parse une page de profil et retourne la liste des `Parcours`.

### `extraire_profils(html: str) -> list[Profil]`
Parse une page de résultats et retourne la liste des `Profil` (sans parcours).

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
            print(p.nom, "—", p.lieu)

asyncio.run(main())
```

### 9.2 Recherche avancée

```python
profils = await client.rechercher(
    prenom="Marie",
    nom="Martin",
    ville="Paris",
    annee="1985",
    delta=2,  # tolérance ±2 ans
)
```

### 9.3 Recherche sans parcours (rapide)

Utile si tu veux juste la liste des profils sans visiter chaque page.

```python
async with CopainsClient(enrichir_parcours=False) as client:
    profils = await client.rechercher(nom="Dupont")
    # 1 seule requête HTTP
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

    print(f"✅ {len(data)} profil(s) exporté(s)")

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

    print(f"✅ Export CSV terminé")

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
    print(f"✅ {len(profils)} profil(s) inséré(s) dans copains.db")

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

Pour éviter de te faire bloquer par le site, limite le nombre de requêtes simultanées :

```python
import asyncio
from copains_api import CopainsClient

sem = asyncio.Semaphore(3)  # max 3 requêtes simultanées

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
        print("Erreur réseau :", e)
    else:
        if not profils:
            print("Aucun résultat (ou erreur silencieuse).")
```

> 💡 **Astuce** : `rechercher()` ne lève **jamais** d'exception réseau — il retourne `[]`. Si tu veux gérer les erreurs finement, appelle directement `client._get_html()`.

### 9.10 Petit serveur web local (FastAPI)

Si tu veux tester depuis un navigateur :

```python
# mes_scripts/serveur.py
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
        raise HTTPException(status_code=404, detail="Aucun profil trouvé")
    return [p.to_dict() for p in profils]
```

**Installer FastAPI** :
```bash
pip install fastapi uvicorn
```

**Lancer** :
```bash
uvicorn mes_scripts.serveur:app --reload
```

**Tester dans le navigateur** :
```
http://localhost:8000/search?prenom=Jean&nom=Dupont
```

---

## 10. Architecture interne

```
copains_api/
├── __init__.py        → exports publics
├── constants.py       → URLs, headers, defaults
├── exceptions.py      → CopainsError, NetworkError, ParseError
├── models.py          → Profil, Parcours (dataclasses)
├── parsers.py         → extraire_profils, extraire_parcours
└── client.py          → CopainsClient (orchestrateur)
```

**Flux d'exécution d'une recherche** :

```
CopainsClient.rechercher()
   │
   ├─► _get_html(URL recherche) ─► aiohttp
   │       │
   │       └─► extraire_profils(html)  ──┐
   │                                     │
   └─► pour chaque profil :              │
         _enrichir(profil)               │
            └─► _get_html(URL profil)    │
                 └─► extraire_parcours ──┘
                                          │
                                          ▼
                                    list[Profil]
```

---

## 11. Performance & bonnes pratiques

### ⚡ Optimisations

| Astuce | Gain |
|---|---|
| `enrichir_parcours=False` | 1 requête au lieu de N+1 |
| `asyncio.Semaphore(3)` | Évite rate-limit et blocage |
| Cache local (JSON sur disque) | Évite requêtes redondantes |
| Réutiliser `CopainsClient` | Évite reconnexion TCP |

### ⚠️ À éviter

- ❌ Lancer 100 recherches simultanées (ban IP).
- ❌ Appeler `rechercher()` sans `async with`.
- ❌ Ignorer les erreurs réseau.
- ❌ Stocker les `aiohttp.ClientSession` globalement.

### 📊 Budget requêtes

| Action | Requêtes HTTP |
|---|---|
| Recherche sans enrichissement | 1 |
| Recherche avec enrichissement | 1 + N profils |
| Parsing HTML seul | 0 |

---

## 12. Sélecteurs CSS & maintenance

Le site peut changer sa structure HTML à tout moment. Voici les sélecteurs utilisés :

### Recherche
| Élément | Sélecteur |
|---|---|
| Item de résultat | `ul.app_list--result__search li` |
| Bloc (data-id) | `.grid_line` |
| Nom + lien | `h3 a` |
| Lieu | `.app_list--result__search__place` |
| Type | `.app_list--result__search__type` |

### Profil
| Élément | Sélecteur |
|---|---|
| Section parcours | `#jCareerList section` |
| Catégorie | `h3` |
| Établissement | `.jCareerLabel` |
| Ville | `.jCcareerTown` |
| Dates | `.jCareerDate` |

> 🔧 **Si le site change** : modifie uniquement `parsers.py`. Le reste du code n'a pas besoin de bouger.

---

## 13. Dépannage

### 🔴 `CopainsNetworkError: Client non initialisé`
**Cause** : tu as oublié `async with`.
```python
# ❌ Mauvais
client = CopainsClient()
await client.rechercher(...)

# ✅ Bon
async with CopainsClient() as client:
    await client.rechercher(...)
```

### 🔴 `[]` retourné alors qu'il y a des résultats
**Causes possibles** :
1. Le site a changé ses sélecteurs CSS → vérifier `parsers.py`.
2. Blocage IP → ralentir avec `asyncio.Semaphore`.
3. Timeout trop court → augmenter `timeout=30`.

### 🔴 Timeouts fréquents
```python
CopainsClient(timeout=30)
```

### 🔴 Caractères bizarres dans la sortie
**Cause** : encodage. Utilise toujours `encoding="utf-8"` :
```python
with open("out.json", "w", encoding="utf-8") as f: ...
```

### 🔴 `ModuleNotFoundError: No module named 'aiohttp'`
```bash
pip install aiohttp beautifulsoup4
```

### 🔴 `RuntimeError: asyncio.run() cannot be called from a running event loop`
**Cause** : tu utilises `asyncio.run()` dans un contexte déjà async (Jupyter, FastAPI…).
**Solution** : utilise `await` directement dans un contexte async.

---

## 14. FAQ

**Q : Est-ce légal ?**
R : Le scraping est un vide juridique. Utilise-le de manière **raisonnable** (pas de spam, pas de revente de données). Respecte les CGU.

**Q : Ça marche pour d'autres pays ?**
R : Non, le site est **français** uniquement.

**Q : Puis-je chercher par nom de jeune fille ?**
R : Pas encore exposé dans l'API. Le paramètre `nomjf` existe dans l'URL mais n'est pas branché. Tu peux modifier `client.py` si besoin.

**Q : Puis-je obtenir l'email/téléphone ?**
R : ❌ Non, et c'est illégal (RGPD). L'API ne récupère que des données **publiques**.

**Q : Combien de profils max par recherche ?**
R : Le site renvoie ce qu'il veut. L'API ne tronque pas — c'est à toi de gérer.

**Q : Puis-je utiliser avec `requests` (sync) ?**
R : Non, tout est async. Utilise `asyncio.run()` dans un script synchrone.

**Q : Comment cacher mon IP ?**
R : Passe un `aiohttp.ClientSession` avec un proxy custom via `headers`/session.

**Q : Y a-t-il une limite de requêtes ?**
R : Non documentée. Reste sous **1 req/sec** pour être safe.

**Q : Puis-je exécuter plusieurs recherches en parallèle ?**
R : Oui, avec `asyncio.gather()` + `asyncio.Semaphore` pour limiter.

**Q : Est-ce que ça marche sous Windows ?**
R : Oui, mais utilise `asyncio.run()` et évite les `ProactorEventLoop` problématiques. Si souci :
```python
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

---

## 15. Sécurité & éthique

- 🔒 **RGPD** : ne stocke pas les données personnelles sans consentement.
- 🚫 **Pas de spam** : ne lance pas 1000 requêtes/minute.
- 🕵️ **Anonymat** : utilise un User-Agent réaliste (fourni par défaut).
- 📜 **CGU** : lis les conditions d'utilisation de Copains d'avant.
- 🎯 **Usage** : éducatif, recherche généalogique **personnelle**, curiosité.

> ⚠️ L'auteur décline toute responsabilité en cas d'usage abusif.

---

**Fin de la documentation.** 🎓
