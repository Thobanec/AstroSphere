from openai import OpenAI

from astrosphere.ai.llm import (
    AILanguageRequest,
    AILanguageResponse,
)
from astrosphere.ai.provider_config import (
    AIProviderConfig,
)


class OpenAILanguageProvider:
    """OpenAI-backed implementation of the AstroSphere language provider."""

    def __init__(
        self,
        config: AIProviderConfig | None = None,
        client=None,
    ):
        self.config = (
            config
            if config is not None
            else AIProviderConfig.from_environment()
        )

        if client is not None:
            self.client = client
        else:
            if not self.config.api_key:
                raise ValueError(
                    "OPENAI_API_KEY is required for "
                    "OpenAILanguageProvider."
                )

            self.client = OpenAI(
                api_key=self.config.api_key,
            )

    def generate(
        self,
        request: AILanguageRequest,
    ) -> AILanguageResponse:
        if not isinstance(request, AILanguageRequest):
            raise ValueError(
                "AILanguageRequest is required."
            )

        response = self.client.responses.create(
            model=self.config.model,
            instructions=self._build_instructions(),
            input=self._build_input(request),
        )

        answer = response.output_text

        return AILanguageResponse(
            answer=answer,
            provenance=request.provenance,
            uncertainties=request.uncertainties,
        )

    @staticmethod
    def _build_instructions():
        return (
            "You are the AstroSphere scientific language assistant. "
            "Use only the supplied AstroSphere facts and interpretations "
            "as scientific evidence. "
            "Educational explanations are provided as controlled context "
            "to help explain scientific concepts. "
            "Do not treat an educational explanation as a new source of "
            "scientific measurements. "
            "Do not invent scientific measurements, sources, or observations. "
            "Do not claim access to data that was not supplied. "
            "Preserve uncertainty when it is provided. "
            "If the supplied information is insufficient to answer the "
            "question, clearly say so."
        )

    @staticmethod
    def _build_input(request):
        facts = "\n".join(
            OpenAILanguageProvider._render_fact(fact)
            for fact in request.facts.facts
        )

        interpretations = "\n".join(
            interpretation.statement
            for interpretation
            in request.interpretations.interpretations
        )

        explanations = ""

        if (
            request.explanations is not None
            and request.explanations.explanations
        ):
            explanations = "\n".join(
                OpenAILanguageProvider._render_explanation(
                    explanation
                )
                for explanation
                in request.explanations.explanations
            )

        return (
            f"Question:\n{request.question}\n\n"
            f"Celestial object:\n"
            f"{request.object.name} ({request.object.id})\n\n"
            f"Observation time:\n"
            f"{request.observation_time}\n\n"
            f"Grounded facts:\n"
            f"{facts or 'None supplied.'}\n\n"
            f"Deterministic interpretations:\n"
            f"{interpretations or 'None supplied.'}\n\n"
            f"Educational explanations:\n"
            f"{explanations or 'None supplied.'}\n\n"
            f"Uncertainties:\n"
            f"{chr(10).join(request.uncertainties) or 'None supplied.'}\n"
        )

    @staticmethod
    def _render_fact(fact):
        if fact.unit:
            return (
                f"{fact.name}: "
                f"{fact.value} "
                f"{fact.unit}"
            )

        return (
            f"{fact.name}: "
            f"{fact.value}"
        )

    @staticmethod
    def _render_explanation(explanation):
        return (
            f"{explanation.subject} "
            f"({explanation.explanation_type}, "
            f"{explanation.level}): "
            f"{explanation.explanation}"
        )
