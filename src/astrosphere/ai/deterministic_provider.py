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

        sections = []

        if not request.facts.facts:
            sections.append(
                f"No grounded scientific facts are "
                f"available for {object_name}."
            )
        else:
            fact_names = {
                fact.name
                for fact in request.facts.facts
            }

            if "trajectory_sample_count" in fact_names:
                sections.append(
                    self._render_planetary_trajectory(
                        object_name,
                        request.facts.facts,
                    )
                )
            elif self._has_relationship_facts(
                request.facts.facts
            ):
                sections.append(
                    self._render_relationship_answer(
                        request.question,
                        object_name,
                        request.facts.facts,
                    )
                )
            else:
                fact_text = "\n".join(
                    self._render_fact(fact)
                    for fact in request.facts.facts
                )

                sections.append(
                    f"Grounded scientific information for "
                    f"{object_name}:\n"
                    f"{fact_text}"
                )

        if (
            request.explanations is not None
            and request.explanations.explanations
        ):
            explanation_text = "\n".join(
                self._render_explanation(explanation)
                for explanation
                in request.explanations.explanations
            )

            sections.append(
                f"Scientific explanation:\n"
                f"{explanation_text}"
            )

        answer = "\n\n".join(sections)

        return AILanguageResponse(
            answer=answer,
            provenance=request.provenance,
            uncertainties=request.uncertainties,
        )

    @staticmethod
    @staticmethod
    def _has_relationship_facts(facts):
        return any(
            fact.source_capability == "relationships"
            for fact in facts
        )

    @staticmethod
    def _render_relationship_answer(
        question,
        object_name,
        facts,
    ):
        normalized_question = question.strip().lower()

        if "cosmic hierarchy" in normalized_question:
            return DeterministicLanguageProvider._render_hierarchy(
                object_name,
                facts,
            )

        if "what orbits" in normalized_question:
            return DeterministicLanguageProvider._render_incoming_orbits(
                object_name,
                facts,
            )

        if "associated" in normalized_question:
            return DeterministicLanguageProvider._render_associated_objects(
                object_name,
                facts,
            )

        if "what does" in normalized_question and "orbit" in normalized_question:
            return DeterministicLanguageProvider._render_outgoing_orbits(
                object_name,
                facts,
            )

        return DeterministicLanguageProvider._render_relationship_facts(
            object_name,
            facts,
        )
    @staticmethod
    def _render_outgoing_orbits(object_name, facts):
        targets = [
            fact.metadata.get("name", fact.value)
            for fact in facts
            if fact.name == "relationship_orbits"
        ]

        if not targets:
            return f"No orbital relationship is recorded for {object_name}."

        if len(targets) == 1:
            return f"{object_name} orbits the {targets[0]}."

        target_text = ", ".join(targets[:-1])
        target_text += f" and {targets[-1]}"
        return f"{object_name} orbits {target_text}."

    @staticmethod
    def _render_incoming_orbits(object_name, facts):
        sources = [
            fact.metadata.get("name", fact.value)
            for fact in facts
            if fact.name == "incoming_relationship_orbits"
        ]

        if not sources:
            return f"No orbital relationships are recorded for {object_name}."

        if len(sources) == 1:
            return f"{sources[0]} orbits {object_name}."

        source_text = ", ".join(sources[:-1])
        source_text += f" and {sources[-1]}"
        return f"The {source_text} orbit {object_name}."

    @staticmethod
    def _render_hierarchy(object_name, facts):
        names = [object_name]

        parent = next(
            (
                fact.metadata.get("name", fact.value)
                for fact in facts
                if fact.name == "object_parent"
            ),
            None,
        )

        if parent is not None:
            names.append(parent)

        for fact in facts:
            if fact.name == "object_ancestor":
                ancestor_name = fact.metadata.get(
                    "name",
                    fact.value,
                )
                if ancestor_name not in names:
                    names.append(ancestor_name)

        return (
            f"{object_name} is in the following cosmic hierarchy: "
            f"{' → '.join(names)}."
        )

    @staticmethod
    def _render_associated_objects(object_name, facts):
        associated_objects = [
            fact.metadata.get("name", fact.value)
            for fact in facts
            if fact.name == "associated_object"
        ]

        if not associated_objects:
            return f"No associated objects are recorded for {object_name}."

        if len(associated_objects) == 1:
            return (
                f"{object_name} is associated with "
                f"{associated_objects[0]}."
            )

        if len(associated_objects) == 2:
            object_text = (
                f"{associated_objects[0]} and "
                f"{associated_objects[1]}"
            )
        else:
            object_text = ", ".join(associated_objects[:-1])
            object_text += f", and {associated_objects[-1]}"

        return (
            f"{object_name} is associated with "
            f"{object_text}."
        )
    @staticmethod
    def _render_relationship_facts(object_name, facts):
        fact_text = "\n".join(
            DeterministicLanguageProvider._render_fact(fact)
            for fact in facts
            if fact.source_capability == "relationships"
        )

        return (
            f"Grounded relationship information for "
            f"{object_name}:\n{fact_text}"
        )

    @staticmethod
    def _render_planetary_trajectory(
        object_name,
        facts,
    ):
        fact_map = {
            fact.name: fact.value
            for fact in facts
        }

        sample_count = fact_map.get(
            "trajectory_sample_count"
        )
        start_date = fact_map.get(
            "trajectory_start_date"
        )
        end_date = fact_map.get(
            "trajectory_end_date"
        )
        coordinate_frame = fact_map.get(
            "trajectory_coordinate_frame"
        )

        start_x = fact_map.get("trajectory_start_x")
        start_y = fact_map.get("trajectory_start_y")
        start_z = fact_map.get("trajectory_start_z")

        end_x = fact_map.get("trajectory_end_x")
        end_y = fact_map.get("trajectory_end_y")
        end_z = fact_map.get("trajectory_end_z")

        lines = [
            f"{object_name} trajectory:",
        ]

        if (
            start_date is not None
            and end_date is not None
        ):
            lines.append(
                f"Calculated from {start_date} "
                f"to {end_date}."
            )

        if sample_count is not None:
            lines.append(
                f"Trajectory samples: {sample_count}."
            )

        if coordinate_frame is not None:
            lines.append(
                f"Reference frame: {coordinate_frame}."
            )

        if all(
            value is not None
            for value in (
                start_x,
                start_y,
                start_z,
            )
        ):
            lines.append(
                "Start position: "
                f"({start_x:.3f}, "
                f"{start_y:.3f}, "
                f"{start_z:.3f}) AU."
            )

        if all(
            value is not None
            for value in (
                end_x,
                end_y,
                end_z,
            )
        ):
            lines.append(
                "End position: "
                f"({end_x:.3f}, "
                f"{end_y:.3f}, "
                f"{end_z:.3f}) AU."
            )

        return "\n".join(lines)


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
