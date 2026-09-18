import aiohttp
import asyncio
from typing import Optional, List, Dict
from urllib.parse import urlencode

from .constants import COPAINS_BASE, HEADERS_COPAINS, DEFAULT_TIMEOUT, DEFAULT_DELTA
from .exceptions import CopainsNetworkError
from .models import Profil
from .parsers import extraire_profils, extraire_parcours

class CopainsClient:
    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        enrichir_parcours: bool = True,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.enrichir_parcours = enrichir_parcours
        self.headers = headers or HEADERS_COPAINS
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=self.timeout
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def _get_html(self, url: str) -> str:
        if not self._session:
            raise CopainsNetworkError("Client non initialisé (utiliser 'async with')")
            
        try:
            async with self._session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except asyncio.TimeoutError:
            raise CopainsNetworkError(f"Timeout lors de la requête vers {url}")
        except aiohttp.ClientError as e:
            raise CopainsNetworkError(f"Erreur réseau: {e}")

    async def _enrichir(self, profil: Profil) -> None:
        if not profil.url:
            return
            
        try:
            html = await self._get_html(profil.url)
            profil.parcours = extraire_parcours(html)
        except Exception:
            # Ignore enrichment errors on individual profiles
            pass

    async def rechercher(
        self,
        prenom: str = "",
        nom: str = "",
        ville: str = "",
        annee: str = "",
        delta: int = DEFAULT_DELTA,
    ) -> List[Profil]:
        
        params = {
            "ty": "1", # Type = Personnes
        }
        if prenom: params["prenom"] = prenom
        if nom: params["nom"] = nom
        if ville: params["ville"] = ville
        if annee: 
            params["annee"] = annee
            params["annee_delta"] = str(delta)
            
        url = f"{COPAINS_BASE}/recherche/?{urlencode(params)}"
        
        try:
            html = await self._get_html(url)
        except CopainsNetworkError:
            return [] 

        profils = extraire_profils(html)
        
        if self.enrichir_parcours and profils:
            sem = asyncio.Semaphore(5)
            
            async def enrichir_with_sem(p):
                async with sem:
                    await self._enrichir(p)
                    
            await asyncio.gather(*(enrichir_with_sem(p) for p in profils))
            
        return profils
