from astrosphere.ai.llm import (
    AILanguageRequest,
    AILanguageResponse,
)


class DeterministicLanguageProvider:
    """Local provider for deterministic, non-LLM responses."""

    def generate(
        self,
        request: AILanguageRequest,
    ) -> AILanguageResponse:
        if not isinstance(
            request,
            AILanguageRequest,
        ):
            raise ValueError(
                "AILanguageRequest is required."
            )

        object_name = request.object.name

        if not request.facts.facts:
            answer = (
                f"No grounded scientific facts are "
                f"available for {object_name}."
            )
        else:
            fact_text = "\n".join(
                self._render_fact(fact)
                for fact in request.facts.facts
            )

            answer = (
                f"Grounded scientific information for "
                f"{object_name}:\n"
                f"{fact_text}"
            )

        return AILanguageResponse(
            answer=answer,
            provenance=request.provenance,
            uncertainties=request.uncertainties,
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
