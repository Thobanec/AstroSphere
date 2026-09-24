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
        normalized_question = request.question.strip().lower()

        # Stable scientific concept definitions are answered directly from
        # the question. They do not require a celestial-object context.
        concept_answer = self._render_scientific_concept(
            normalized_question,
        )

        if concept_answer is not None:
            sections = [concept_answer]
        else:
            sections = []

        if concept_answer is not None:
            pass
        elif not request.facts.facts:
            sections.append(
                f"No grounded scientific facts are "
                f"available for {object_name}."
            )
        else:
            fact_names = {
                fact.name
                for fact in request.facts.facts
            }

            if "distance" in fact_names:
                sections.append(self._render_distance(request.facts.facts))
            elif "object_description" in fact_names or "object_name" in fact_names:
                sections.append(
                    self._render_context(
                        object_name,
                        request.facts.facts,
                    )
                )
            elif "impact_risk_object_count" in fact_names:
                normalized_question = request.question.strip().lower()

                yes_no_monitoring_question = (
                    (
                        normalized_question.startswith("is ")
                        or normalized_question.startswith("are ")
                        or normalized_question.startswith("was ")
                        or normalized_question.startswith("were ")
                    )
                    and any(
                        phrase in normalized_question
                        for phrase in (
                            "being monitored",
                            "being watched",
                            "being tracked",
                            "being observed",
                            "monitored",
                            "watched",
                            "tracked",
                            "observed",
                        )
                    )
                )

                if yes_no_monitoring_question and object_name:
                    sections.append(
                        f"Yes. {object_name} is monitored as a near-Earth object "
                        f"because its orbit is relevant to Earth's neighbourhood. "
                        f"Planetary-defence monitoring tracks its future Earth "
                        f"encounters, refines the object's orbit as new observations "
                        f"become available, and checks whether the calculated "
                        f"trajectory produces any impact-risk solution."
                    )
                else:
                    sections.append(
                        self._render_planetary_defence(
                            request.facts.facts,
                            question=request.question,
                            object_name=object_name,
                        )
                    )
            elif "trajectory_sample_count" in fact_names:
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
    def _render_scientific_concept(question):
        normalized = question.strip().lower()

        if (
            "near-earth object" in normalized
            or "near earth object" in normalized
            or "near-earth objects" in normalized
            or "near earth objects" in normalized
            or "near-earth asteroid" in normalized
            or "near earth asteroid" in normalized
        ):
            return (
                "A near-Earth object (NEO) is a small Solar System body "
                "whose orbit brings it into the near-Earth region. NEOs "
                "include asteroids and, less commonly, comets. Being a "
                "near-Earth object does not by itself mean that an object "
                "will impact Earth; its orbit and future encounters must "
                "be evaluated to determine whether an impact risk exists."
            )

        if (
            "earth-crossing asteroid" in normalized
            or "earth crossing asteroid" in normalized
            or "earth-crossing asteroids" in normalized
            or "earth crossing asteroids" in normalized
            or "earth-crossing object" in normalized
            or "earth crossing object" in normalized
        ):
            return (
                "An Earth-crossing asteroid is an asteroid whose orbit "
                "intersects or can cross the orbital region occupied by "
                "Earth. Earth-crossing describes the geometry of the "
                "orbit; it does not by itself mean that an impact will "
                "occur. The actual future separation from Earth depends "
                "on the timing and the object's orbital parameters."
            )

        if (
            "mars-crossing asteroid" in normalized
            or "mars crossing asteroid" in normalized
            or "mars-crossing asteroids" in normalized
            or "mars crossing asteroids" in normalized
        ):
            return (
                "A Mars-crossing asteroid is an asteroid whose orbit "
                "intersects or can cross the orbital region of Mars. "
                "The term describes orbital geometry and does not mean "
                "that the asteroid will necessarily encounter or impact "
                "Mars."
            )

        return None


    @staticmethod
    def _render_context(object_name, facts):
        description = next(
            (
                fact.value
                for fact in facts
                if fact.name == "object_description"
            ),
            None,
        )

        object_type = next(
            (
                fact.value
                for fact in facts
                if fact.name == "object_type"
            ),
            None,
        )

        parent = next(
            (
                fact.value
                for fact in facts
                if fact.name == "parent_object"
            ),
            None,
        )

        system = next(
            (
                fact.value
                for fact in facts
                if fact.name == "system"
            ),
            None,
        )

        text = f"{object_name} is"

        if object_type:
            text += f" a {object_type.replace('_', ' ')}"

        if description:
            text += f". {description}"
        else:
            text += "."

        if parent:
            text += f" Its parent object is {parent}."

        if system:
            text += f" It belongs to the {system} system."

        return text


    @staticmethod
    def _render_distance(facts):
        distance = next((f for f in facts if f.name == "distance"), None)
        velocity = next((f for f in facts if f.name == "relative_velocity"), None)
        if distance is None:
            return "AstroSphere could not calculate the requested distance."
        reference = distance.metadata.get("reference_body") or "the reference body"
        target = distance.metadata.get("target_body") or "the target body"
        text = f"The current distance from {reference} to {target} is {distance.value:,.0f} km."
        if velocity is not None:
            text += f" Their relative speed is {velocity.value:,.3f} km/s."
        return text

    @staticmethod
    def _render_planetary_defence(facts, question=None, object_name=None):
        normalized_question = (question or "").strip().lower()

        risk_count = next(
            (f.value for f in facts if f.name == "impact_risk_object_count"),
            0,
        )
        approach_count = next(
            (f.value for f in facts if f.name == "close_approach_count"),
            0,
        )
        risks = [f for f in facts if f.name == "impact_risk_object"]
        approaches = [f for f in facts if f.name == "close_approach_event"]

        monitoring_question = (
            any(
                phrase in normalized_question
                for phrase in (
                    "why is",
                    "why are",
                    "why is it being monitored",
                    "why is it monitored",
                    "why is it being watched",
                    "why is it being tracked",
                    "why is it being observed",
                )
            )
            and any(
                phrase in normalized_question
                for phrase in (
                    "monitor",
                    "monitored",
                    "monitoring",
                    "watch",
                    "watched",
                    "track",
                    "tracked",
                    "observ",
                )
            )
        )

        yes_no_monitoring_question = (
            (
                normalized_question.startswith("is ")
                or normalized_question.startswith("are ")
                or normalized_question.startswith("was ")
                or normalized_question.startswith("were ")
            )
            and any(
                phrase in normalized_question
                for phrase in (
                    "being monitored",
                    "being watched",
                    "being tracked",
                    "being observed",
                    "monitored",
                    "watched",
                    "tracked",
                    "observed",
                )
            )
        )

        if monitoring_question and object_name:
            object_key = object_name.strip().lower()

            matching_risks = [
                f for f in risks
                if object_key in str(f.value or "").lower()
                or object_key in str(f.metadata.get("name") or "").lower()
                or object_key in str(f.metadata.get("designation") or "").lower()
            ]

            matching_approaches = [
                f for f in approaches
                if object_key in str(f.value or "").lower()
                or object_key in str(f.metadata.get("name") or "").lower()
                or object_key in str(f.metadata.get("designation") or "").lower()
            ]

            if yes_no_monitoring_question:
                text = (
                    f"Yes. {object_name} is monitored as a near-Earth object "
                    f"because its orbit is relevant to Earth's neighbourhood. "
                    f"Planetary-defence monitoring tracks its future Earth "
                    f"encounters, refines the object's orbit as new observations "
                    f"become available, and checks whether the calculated "
                    f"trajectory produces any impact-risk solution."
                )
            else:
                text = (
                    f"{object_name} is monitored because it is a near-Earth object "
                    f"whose orbit is relevant to Earth's neighbourhood. "
                    f"Planetary-defence monitoring tracks its future Earth encounters, "
                    f"refines the object's orbit as new observations become available, "
                    f"and checks whether the calculated trajectory produces any "
                    f"impact-risk solution."
                )

            if matching_approaches:
                text += (
                    " Current CNEOS data includes Earth close-approach "
                    "record(s) for this object: "
                )
                text += "; ".join(
                    f"{f.metadata.get('date')} at "
                    f"{f.metadata.get('distance_au')} AU"
                    for f in matching_approaches[:5]
                ) + "."

            if matching_risks:
                text += (
                    " It also appears in the current Sentry impact-risk "
                    "dataset with the reported impact probability/probabilities: "
                )
                text += ", ".join(
                    str(f.metadata.get("impact_probability"))
                    for f in matching_risks[:5]
                ) + "."
            else:
                text += (
                    " A monitoring record or close approach does not by itself "
                    "mean that an impact is expected."
                )

            text += (
                " CNEOS risk and trajectory assessments can change as additional "
                "observations improve the orbit solution."
            )

            return text

        text = (
            f"NASA/JPL CNEOS monitoring reports {risk_count} object(s) "
            f"in the current Sentry impact-risk dataset and "
            f"{approach_count} upcoming Earth close-approach record(s) "
            f"in the selected monitoring window."
        )

        if risks:
            text += (
                " Impact-risk records include: "
                + "; ".join(
                    f"{f.value} "
                    f"(IP={f.metadata.get('impact_probability')})"
                    for f in risks[:5]
                )
                + "."
            )

        if approaches:
            text += (
                " Upcoming close approaches include: "
                + "; ".join(
                    f"{f.value} on {f.metadata.get('date')} "
                    f"at {f.metadata.get('distance_au')} AU"
                    for f in approaches[:5]
                )
                + "."
            )

        text += (
            " A close approach is not itself an impact prediction, "
            "and Sentry risk assessments can change as observations "
            "improve the orbit solution."
        )

        return text

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
