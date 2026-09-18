from bs4 import BeautifulSoup
from typing import List
from .models import Profil, Parcours
from .constants import COPAINS_BASE
from .exceptions import CopainsParseError

def extraire_profils(html: str) -> List[Profil]:
    soup = BeautifulSoup(html, 'html.parser')
    profils = []
    
    items = soup.select('ul.app_list--result__search li')
    for item in items:
        try:
            titre_a = item.select_one('h3 a')
            if not titre_a:
                continue
                
            nom = titre_a.get_text(strip=True)
            url = titre_a.get('href')
            if url and not url.startswith('http'):
                url = f"{COPAINS_BASE}{url}"
                
            profil_id = None
            grid_line = item.select_one('.grid_line')
            if grid_line and grid_line.has_attr('data-id'):
                profil_id = grid_line.get('data-id')
            elif item.has_attr('data-id'):
                profil_id = item.get('data-id')
                
            lieu_elem = item.select_one('.app_list--result__search__place')
            lieu = lieu_elem.get_text(strip=True) if lieu_elem else None
            
            type_elem = item.select_one('.app_list--result__search__type')
            type_etab = type_elem.get_text(strip=True) if type_elem else None
            
            profil = Profil(
                nom=nom,
                url=url,
                id=profil_id,
                lieu=lieu,
                type=type_etab
            )
            profils.append(profil)
        except Exception:
            continue
            
    return profils

def extraire_parcours(html: str) -> List[Parcours]:
    soup = BeautifulSoup(html, 'html.parser')
    parcours_list = []
    
    sections = soup.select('#jCareerList section')
    for section in sections:
        categorie_elem = section.select_one('h3')
        categorie = categorie_elem.get_text(strip=True) if categorie_elem else "Inconnu"
        
        # Look for structured lines first
        lignes = section.find_all(lambda tag: tag.name in ['li', 'div', 'article'] and tag.select_one('.jCareerLabel'))
        if not lignes:
            # Fallback simple
            etab = section.select_one('.jCareerLabel')
            ville = section.select_one('.jCcareerTown') or section.select_one('.jCareerTown')
            dates = section.select_one('.jCareerDate')
            
            if etab:
                parcours_list.append(Parcours(
                    categorie=categorie,
                    etablissement=etab.get_text(strip=True),
                    ville=ville.get_text(strip=True) if ville else None,
                    dates=dates.get_text(strip=True) if dates else None
                ))
        else:
            for ligne in lignes:
                etab = ligne.select_one('.jCareerLabel')
                ville = ligne.select_one('.jCcareerTown') or ligne.select_one('.jCareerTown')
                dates = ligne.select_one('.jCareerDate')
                
                parcours_list.append(Parcours(
                    categorie=categorie,
                    etablissement=etab.get_text(strip=True) if etab else None,
                    ville=ville.get_text(strip=True) if ville else None,
                    dates=dates.get_text(strip=True) if dates else None
                ))
                
    return parcours_list
