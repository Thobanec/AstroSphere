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

    if available is not None:
        tracking_available = (
            "tracking" in available
        )
        scientific_data_available = (
            "scientific-data" in available
        )

        position_requested = any(
            keyword in normalized_question
            for keyword in _POSITION_KEYWORDS
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

    specific_intents = tuple(
        intent
        for intent in intents
        if intent.capability_id != "context"
    )

    if specific_intents:
        return specific_intents

    return tuple(intents)
