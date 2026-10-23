"""Dados e validação de municípios brasileiros para a interface."""

from __future__ import annotations

import json
import gzip
import unicodedata
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

import streamlit as st


IBGE_MUNICIPALITIES_URL = (
    "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
)

UF_NAMES = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}


class LocationDataError(RuntimeError):
    """Indica que a base pública de municípios não pôde ser carregada."""


def normalize_text(value: str) -> str:
    """Normaliza busca sem acentos e sem diferença entre maiúsculas/minúsculas."""
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char)).casefold()


def _parse_municipality(item: dict[str, Any]) -> dict[str, str] | None:
    try:
        uf = item["microrregiao"]["mesorregiao"]["UF"]
        name = str(item["nome"]).strip()
        sigla = str(uf["sigla"]).strip().upper()
        if not name or sigla not in UF_NAMES:
            return None
        return {"name": name, "uf": sigla, "state": UF_NAMES[sigla]}
    except (KeyError, TypeError):
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def load_municipalities() -> tuple[dict[str, str], ...]:
    # Carrega a base pública do IBGE uma vez por dia no cache do Streamlit.
    request = Request(
        IBGE_MUNICIPALITIES_URL,
        headers={"User-Agent": "CassiaIA/0.1 (prototipo)"},
    )
    try:
        with urlopen(request, timeout=20) as response:
            raw_payload = response.read()
            if response.headers.get("Content-Encoding", "").lower() == "gzip" or raw_payload[:2] == b"\x1f\x8b":
                raw_payload = gzip.decompress(raw_payload)
            payload = json.loads(raw_payload.decode("utf-8"))
    except (OSError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise LocationDataError(
            "Não foi possível carregar a base de municípios do IBGE agora."
        ) from error

    municipalities = [
        parsed
        for item in payload
        if isinstance(item, dict)
        for parsed in [_parse_municipality(item)]
        if parsed is not None
    ]
    if not municipalities:
        raise LocationDataError("A base de municípios do IBGE não retornou dados válidos.")
    return tuple(sorted(municipalities, key=lambda item: (item["uf"], normalize_text(item["name"]))))


def search_municipalities(
    municipalities: tuple[dict[str, str], ...] | list[dict[str, str]],
    query: str,
    uf: str = "",
    limit: int = 8,
) -> list[dict[str, str]]:
    #Busca por trecho do nome, com filtro opcional por UF.
    normalized_query = normalize_text(query.strip())
    normalized_uf = uf.strip().upper()
    if not normalized_query:
        return []

    matches = [
        item
        for item in municipalities
        if (not normalized_uf or item["uf"] == normalized_uf)
        and normalized_query in normalize_text(item["name"])
    ]
    return matches[:limit]


def format_location(location: dict[str, str] | None) -> str:
    if not location:
        return "Localização não informada"
    return f'{location["name"]} — {location["uf"]}'
