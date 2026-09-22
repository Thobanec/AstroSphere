from astrosphere.models.research import ResearchQuestion
from astrosphere.research.registry import ResearchRegistry


class ResearchQuestionRegistry:
    def __init__(self, investigation_registry: ResearchRegistry):
        self._investigation_registry = investigation_registry
        self._questions = {}

    def create_question(
        self,
        question: ResearchQuestion,
    ) -> ResearchQuestion:
        if question.id in self._questions:
            raise ValueError(
                f"Research question already exists: {question.id}"
            )

        self._validate_investigation(question.investigation_id)

        self._questions[question.id] = question
        return question

    def get_question(
        self,
        question_id: str,
    ) -> ResearchQuestion | None:
        return self._questions.get(question_id.strip())

    def list_questions(self) -> tuple[ResearchQuestion, ...]:
        return tuple(self._questions.values())

    def _validate_investigation(
        self,
        investigation_id: str,
    ) -> None:
        if self._investigation_registry.get_investigation(
            investigation_id
        ) is None:
            raise ValueError(
                f"Unknown research investigation: {investigation_id}"
            )
