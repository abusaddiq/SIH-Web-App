"""Future cloud AI providers (OpenAI / Anthropic / Gemini) behind the AIProvider interface.

Not instantiated unless AI_PROVIDER + AI_API_KEY are configured. Kept out of the default
"rules" path so the MVP never depends on external APIs.
"""
from .ai import AIProvider


class CloudProvider(AIProvider):
    name = "cloud"
    label = "Cloud provider"

    def __init__(self, provider, api_key, model=""):
        self.provider = provider
        self.api_key = api_key
        self.model = model

    def answer(self, question):
        # Integrate with the chosen provider SDK here when enabled.
        return self._fallback(question)

    def _fallback(self, question):
        from .ai import RulesProvider

        return RulesProvider().answer(question)