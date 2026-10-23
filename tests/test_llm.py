import os
import sys
import unittest
from types import ModuleType
from types import SimpleNamespace
from unittest.mock import patch

# Permite executar estes testes de unidade em um ambiente sem o SDK instalado.
# O código de produção continua exigindo as dependências de requirements.txt.
try:
    import httpx  # noqa: F401
except ModuleNotFoundError:
    httpx_stub = ModuleType("httpx")
    httpx_stub.HTTPError = type("HTTPError", (Exception,), {})
    sys.modules["httpx"] = httpx_stub

try:
    from dotenv import load_dotenv as _load_dotenv  # noqa: F401
except ModuleNotFoundError:
    dotenv_stub = ModuleType("dotenv")
    dotenv_stub.load_dotenv = lambda *args, **kwargs: None
    sys.modules["dotenv"] = dotenv_stub

try:
    from google import genai as _genai  # noqa: F401
except (ImportError, ModuleNotFoundError):
    google_stub = ModuleType("google")
    genai_stub = ModuleType("google.genai")
    errors_stub = ModuleType("google.genai.errors")
    types_stub = ModuleType("google.genai.types")

    errors_stub.APIError = type("APIError", (Exception,), {})

    class GenerateContentConfig:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    types_stub.GenerateContentConfig = GenerateContentConfig
    genai_stub.Client = object
    genai_stub.errors = errors_stub
    genai_stub.types = types_stub
    google_stub.genai = genai_stub
    sys.modules.update(
        {
            "google": google_stub,
            "google.genai": genai_stub,
            "google.genai.errors": errors_stub,
            "google.genai.types": types_stub,
        }
    )

from agent import llm
from agent.llm import (
    EmptyModelResponseError,
    GeminiService,
    GeminiServiceError,
    MissingAPIKeyError,
)


class FakeModels:
    def __init__(self, available, response_text="Resposta real simulada.", error=None):
        self.available = available
        self.response_text = response_text
        self.error = error
        self.calls = []

    def list(self):
        return [
            SimpleNamespace(name=name, supported_actions=["generateContent"])
            for name in self.available
        ]

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return SimpleNamespace(text=self.response_text)


class FakeClient:
    def __init__(self, available, response_text="Resposta real simulada.", error=None):
        self.models = FakeModels(available, response_text, error)


class GeminiServiceTests(unittest.TestCase):
    def test_requires_api_key_when_creating_real_client(self):
        with patch.dict(os.environ, {}, clear=True), patch("agent.llm.load_dotenv"):
            with self.assertRaises(MissingAPIKeyError):
                GeminiService()

    def test_selects_an_available_preferred_model_and_sends_history(self):
        client = FakeClient(
            ["models/gemini-3.5-flash-lite", "models/gemini-3.8-flash"]
        )
        service = GeminiService(client=client)
        messages = [
            {"role": "assistant", "content": "Olá."},
            {"role": "user", "content": "Preciso de uma informação."},
        ]

        response = service.generate_reply(messages, "info_chat")

        self.assertEqual(response, "Resposta real simulada.")
        self.assertEqual(client.models.calls[0]["model"], "gemini-3.8-flash")
        self.assertEqual(client.models.calls[0]["contents"][-1]["role"], "user")
        self.assertIn(
            "modo informativo",
            client.models.calls[0]["config"].system_instruction,
        )

    def test_rejects_an_empty_model_response(self):
        service = GeminiService(
            client=FakeClient(["models/gemini-3.8-flash"], response_text="  ")
        )

        with self.assertRaises(EmptyModelResponseError):
            service.generate_reply(
                [{"role": "user", "content": "Olá"}], "talk_chat"
            )

    def test_translates_rate_limit_without_exposing_api_details(self):
        class FakeAPIError(Exception):
            code = 429

        service = GeminiService(
            client=FakeClient(
                ["models/gemini-3.8-flash"], error=FakeAPIError("secret detail")
            )
        )

        with patch.object(llm.errors, "APIError", FakeAPIError):
            with self.assertRaisesRegex(GeminiServiceError, "limite de uso") as raised:
                service.generate_reply(
                    [{"role": "user", "content": "Olá"}], "talk_chat"
                )

        self.assertNotIn("secret detail", str(raised.exception))

    def test_translates_authentication_model_and_service_errors(self):
        class FakeAPIError(Exception):
            def __init__(self, code):
                self.code = code

        expectations = {
            401: "autenticar",
            404: "modelo selecionado",
            503: "temporariamente indisponível",
        }
        with patch.object(llm.errors, "APIError", FakeAPIError):
            for code, expected_text in expectations.items():
                with self.subTest(code=code):
                    service = GeminiService(
                        client=FakeClient(
                            ["models/gemini-3.8-flash"],
                            error=FakeAPIError(code),
                        )
                    )
                    with self.assertRaisesRegex(
                        GeminiServiceError, expected_text
                    ):
                        service.generate_reply(
                            [{"role": "user", "content": "Olá"}],
                            "talk_chat",
                        )

    def test_translates_network_errors(self):
        service = GeminiService(
            client=FakeClient(
                ["models/gemini-3.8-flash"],
                error=OSError("private network detail"),
            )
        )

        with self.assertRaisesRegex(GeminiServiceError, "conectar") as raised:
            service.generate_reply(
                [{"role": "user", "content": "Olá"}], "talk_chat"
            )

        self.assertNotIn("private network detail", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
