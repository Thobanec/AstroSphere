from astrosphere.ai.intent import (
    AICapabilityIntent,
)


_CAPABILITY_KEYWORDS = {
    "tracking": (
        "where is",
        "where is it",
        "where are",
        "location",
        "position now",
        "current position",
        "track",
        "tracking",
    ),
    "trajectory": (
        "trajectory",
        "path",
        "orbit path",
        "projected path",
    ),
    "close-approaches": (
        "close approach",
        "closest approach",
        "closest to earth",
        "approach earth",
        "near earth",
        "how close does",
        "how close will",
        "how near does",
        "how near will",
    ),
    "space-weather": (
        "space weather",
        "solar wind",
        "solar wind speed",
        "magnetic field",
        "geomagnetic",
        "kp index",
    ),
    "scientific-data": (
        "scientific data",
        "scientific state",
        "velocity",
        "how fast",
        "moving",
        "speed",
        "position and velocity",
        "observation",
        "reference frame",
    ),
    "relationships": (
        "parent",
        "child",
        "children",
        "ancestor",
        "ancestors",
        "hierarchy",
        "relationship",
        "relationships",
        "orbit",
        "orbits",
        "associated",
        "associated with",
    ),
    "context": (
        "information about",
        "tell me about",
        "what is",
        "overview",
        "context",
    ),
}


_POSITION_KEYWORDS = (
    "where is",
    "where is it",
    "where are",
    "location",
    "position now",
    "current position",
)


def select_capability_intents(
    question,
    available_capabilities=None,
):
    if not isinstance(question, str):
        raise ValueError("AI question is required.")

    normalized_question = question.strip().lower()

    if not normalized_question:
        raise ValueError("AI question is required.")

    available = None

    if available_capabilities is not None:
        available = {
            capability
            for capability in available_capabilities
        }

    intents = []

    for capability_id, keywords in _CAPABILITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized_question:
                intents.append(
                    AICapabilityIntent(
                        capability_id=capability_id,
                        reason=(
                            f"Question matched the "
                            f"'{keyword}' intent."
                        ),
                    )
                )
                break

    # Domain-specific capabilities take precedence over generic
    # scientific-data matches. For example, "solar wind speed"
    # belongs to space-weather, not generic velocity data.
    if any(
        intent.capability_id == "space-weather"
        for intent in intents
    ):
        intents = [
            intent
            for intent in intents
            if intent.capability_id != "scientific-data"
        ]


    # Cosmic hierarchy questions are relationship queries, not
    # current-position tracking queries.
    if "hierarchy" in normalized_question:
        intents = [
            intent
            for intent in intents
            if intent.capability_id != "tracking"
        ]

    if available is not None:
        tracking_available = (
            "tracking" in available
        )
        scientific_data_available = (
            "scientific-data" in available
        )

        position_requested = (
            "hierarchy" not in normalized_question
            and any(
                keyword in normalized_question
                for keyword in _POSITION_KEYWORDS
            )
        )

        if (
            position_requested
            and not tracking_available
            and scientific_data_available
        ):
            intents = [
                intent
                for intent in intents
                if intent.capability_id != "tracking"
            ]

            intents.append(
                AICapabilityIntent(
                    capability_id="scientific-data",
                    reason=(
                        "Position intent mapped to "
                        "'scientific-data' because "
                        "'tracking' is unavailable."
                    ),
                )
            )
        else:
            intents = [
                intent
                for intent in intents
                if (
                    intent.capability_id != "tracking"
                    or tracking_available
                )
            ]

    if available is not None:
        trajectory_available = (
            "trajectory" in available
        )
        planetary_trajectory_available = (
            "planetary-trajectory" in available
        )
        orbital_analysis_available = (
            "orbital-analysis" in available
        )

        trajectory_requested = any(
            keyword in normalized_question
            for keyword in (
                "trajectory",
                "path",
                "orbit path",
                "projected path",
            )
        )

        # Explicit trajectory/path questions take precedence over the
        # generic relationship "orbit" keyword.
        if trajectory_requested:
            intents = [
                intent
                for intent in intents
                if intent.capability_id != "relationships"
            ]
        planetary_object_requested = any(
            planet in normalized_question
            for planet in (
                "mercury",
                "venus",
                "earth",
                "mars",
                "jupiter",
                "saturn",
                "uranus",
                "neptune",
                "pluto",
            )
        )

        if (
            trajectory_requested
            and planetary_object_requested
            and planetary_trajectory_available
        ):
            intents = [
                intent
                for intent in intents
                if intent.capability_id != "trajectory"
            ]

            intents.append(
                AICapabilityIntent(
                    capability_id="planetary-trajectory",
                    reason=(
                        "Trajectory intent mapped to "
                        "'planetary-trajectory' for a "
                        "planetary object."
                    ),
                )
            )

        elif (
            trajectory_requested
            and not trajectory_available
            and orbital_analysis_available
        ):
            intents = [
                intent
                for intent in intents
                if intent.capability_id != "trajectory"
            ]

            intents.append(
                AICapabilityIntent(
                    capability_id="orbital-analysis",
                    reason=(
                        "Trajectory intent mapped to "
                        "'orbital-analysis' because "
                        "'trajectory' is unavailable."
                    ),
                )
            )

    specific_intents = tuple(
        intent
        for intent in intents
        if intent.capability_id != "context"
    )

    if specific_intents:
        return specific_intents

    return tuple(intents)



