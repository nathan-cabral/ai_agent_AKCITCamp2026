"""Integração simples e testável com a Gemini API."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from agent.config import (
    MAX_OUTPUT_TOKENS,
    PREFERRED_GEMINI_MODELS,
    TEMPERATURE,
    UNSUITABLE_MODEL_MARKERS,
)
from agent.prompts import build_system_instruction


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class GeminiServiceError(RuntimeError):
    """Erro seguro para apresentação na interface, sem detalhes sensíveis."""


class MissingAPIKeyError(GeminiServiceError):
    """Indica que a variável GEMINI_API_KEY não foi configurada."""


class EmptyModelResponseError(GeminiServiceError):
    """Indica que a API respondeu sem texto utilizável."""


def _normalize_model_name(name: str) -> str:
    return name.removeprefix("models/")


def _supports_text_generation(model: Any) -> bool:
    name = _normalize_model_name(str(getattr(model, "name", ""))).lower()
    if not name.startswith("gemini-"):
        return False
    if any(marker in name for marker in UNSUITABLE_MODEL_MARKERS):
        return False

    actions = getattr(model, "supported_actions", None)
    if actions:
        normalized_actions = {
            str(action).replace("_", "").lower() for action in actions
        }
        if "generatecontent" not in normalized_actions:
            return False
    return True


def _safe_api_error(error: Exception) -> GeminiServiceError:
    code = getattr(error, "code", None)
    if code in (400, 401, 403):
        return GeminiServiceError(
            "Não foi possível autenticar na Gemini API. Verifique a chave configurada."
        )
    if code == 404:
        return GeminiServiceError(
            "O modelo selecionado não está disponível para esta chave no momento."
        )
    if code == 429:
        return GeminiServiceError(
            "O limite de uso da Gemini API foi atingido. Aguarde um pouco e tente novamente."
        )
    if code in (408, 500, 502, 503, 504):
        return GeminiServiceError(
            "A Gemini API está temporariamente indisponível. Tente novamente em instantes."
        )
    return GeminiServiceError(
        "Não foi possível obter uma resposta da Gemini API. Tente novamente."
    )


class GeminiService:
    """Seleciona um modelo disponível e gera respostas sem persistir mensagens."""

    def __init__(self, client: Any | None = None) -> None:
        self._model_name: str | None = None
        if client is not None:
            self._client = client
            return

        load_dotenv(PROJECT_ROOT / ".env")
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise MissingAPIKeyError(
                "A Gemini API ainda não foi configurada. Adicione GEMINI_API_KEY ao arquivo .env."
            )
        self._client = genai.Client(api_key=api_key)

    def _select_model(self) -> str:
        if self._model_name:
            return self._model_name

        try:
            available = {
                _normalize_model_name(str(model.name))
                for model in self._client.models.list()
                if _supports_text_generation(model)
            }
        except errors.APIError as error:
            raise _safe_api_error(error) from None
        except (ConnectionError, OSError, TimeoutError, httpx.HTTPError):
            raise GeminiServiceError(
                "Não foi possível conectar à Gemini API. Verifique sua internet e tente novamente."
            ) from None

        for preferred in PREFERRED_GEMINI_MODELS:
            if preferred in available:
                self._model_name = preferred
                return preferred

        stable_fallbacks = sorted(
            name
            for name in available
            if "preview" not in name and "experimental" not in name and "exp" not in name
        )
        if not stable_fallbacks:
            raise GeminiServiceError(
                "Nenhum modelo Gemini de texto compatível está disponível para esta chave."
            )

        self._model_name = stable_fallbacks[-1]
        return self._model_name

    def generate_reply(self, messages: list[dict[str, str]], mode: str) -> str:
        """Envia o histórico da sessão e retorna somente texto validado."""
        contents = []
        for message in messages:
            content = str(message.get("content", "")).strip()
            role = message.get("role")
            if not content or role not in ("user", "assistant"):
                continue
            api_role = "user" if role == "user" else "model"
            if contents and contents[-1]["role"] == api_role:
                contents[-1]["parts"].append({"text": content})
            else:
                contents.append(
                    {"role": api_role, "parts": [{"text": content}]}
                )

        if not contents or contents[-1]["role"] != "user":
            raise GeminiServiceError("Não há uma nova mensagem para enviar.")

        try:
            response = self._client.models.generate_content(
                model=self._select_model(),
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=build_system_instruction(mode),
                    temperature=TEMPERATURE,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                ),
            )
            try:
                response_text = response.text
            except (AttributeError, ValueError):
                response_text = None
            text = (response_text or "").strip()
        except GeminiServiceError:
            raise
        except errors.APIError as error:
            raise _safe_api_error(error) from None
        except (ConnectionError, OSError, TimeoutError, httpx.HTTPError):
            raise GeminiServiceError(
                "Não foi possível conectar à Gemini API. Verifique sua internet e tente novamente."
            ) from None
        except Exception:
            raise GeminiServiceError(
                "Ocorreu um erro ao preparar a resposta. Tente novamente."
            ) from None

        if not text:
            raise EmptyModelResponseError(
                "A Gemini API não retornou uma resposta de texto. Tente reformular a mensagem."
            )
        return text
