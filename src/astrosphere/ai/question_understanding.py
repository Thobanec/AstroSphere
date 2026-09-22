from astrosphere.ai.intent_selector import (
    select_capability_intents,
)
from astrosphere.ai.scientific_question import (
    AIScientificQuestion,
)


_INFORMATION_KEYWORDS = {
    "position": (
        "where is",
        "where is it",
        "where are",
        "location",
        "position",
    ),
    "velocity": (
        "velocity",
        "how fast",
        "speed",
        "moving",
        "moving at",
    ),
    "trajectory": (
        "trajectory",
        "path",
        "projected path",
    ),
    "close_approach": (
        "close approach",
        "closest approach",
        "closest to earth",
        "approach earth",
        "near earth",
    ),
    "space_weather": (
        "space weather",
        "solar wind",
        "magnetic field",
        "geomagnetic",
        "kp index",
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


_CURRENT_KEYWORDS = (
    "current",
    "now",
    "today",
    "right now",
    "where is",
    "where are",
    "location",
    "how fast",
    "moving",
)


_FUTURE_KEYWORDS = (
    "future",
    "next",
    "projected",
    "trajectory",
    "close approach",
    "closest approach",
)


def understand_scientific_question(
    question,
    object_id=None,
    available_capabilities=None,
):
    if not isinstance(question, str) or not question.strip():
        raise ValueError("AI question is required.")

    if (
        object_id is not None
        and (
            not isinstance(object_id, str)
            or not object_id.strip()
        )
    ):
        raise ValueError(
            "Celestial object ID must be a string."
        )

    normalized_question = question.strip().lower()

    requested_information = []

    space_weather_requested = any(
        keyword in normalized_question
        for keyword in _INFORMATION_KEYWORDS["space_weather"]
    )

    for information, keywords in _INFORMATION_KEYWORDS.items():
        if information == "space_weather":
            if space_weather_requested:
                requested_information.append(
                    "space_weather"
                )
            continue

        # "solar wind speed" is space-weather information;
        # do not classify the generic "speed" as velocity too.
        if (
            information == "velocity"
            and space_weather_requested
        ):
            continue

        if any(
            keyword in normalized_question
            for keyword in keywords
        ):
            requested_information.append(
                information
            )

    # Cosmic hierarchy questions are relationship queries; the
    # "where is" wording must not classify them as position queries.
    if "hierarchy" in normalized_question:
        requested_information = [
            information
            for information in requested_information
            if information != "position"
        ]

    # "what is" and similar phrases provide generic context.
    # Keep context only when no more specific information was found.
    if len(requested_information) > 1:
        requested_information = [
            information
            for information in requested_information
            if information != "context"
        ]

    has_current_language = any(
        keyword in normalized_question
        for keyword in _CURRENT_KEYWORDS
    )
    has_future_language = any(
        keyword in normalized_question
        for keyword in _FUTURE_KEYWORDS
    )

    if has_current_language:
        temporal_context = "current"
    elif has_future_language:
        temporal_context = "future"
    else:
        temporal_context = "unspecified"

    temporal_contexts = []

    for information in requested_information:
        if information in (
            "trajectory",
            "close_approach",
        ):
            scope = "future"
        elif information in (
            "position",
            "velocity",
            "space_weather",
        ):
            if has_current_language:
                scope = "current"
            elif has_future_language:
                scope = "future"
            else:
                scope = "unspecified"
        else:
            scope = "unspecified"

        temporal_contexts.append(
            (information, scope)
        )

    intents = select_capability_intents(
        question,
        available_capabilities=available_capabilities,
    )

    normalized_object_id = (
        object_id.strip().lower()
        if isinstance(object_id, str)
        else None
    )

    return AIScientificQuestion(
        question=question.strip(),
        object_id=normalized_object_id,
        requested_information=tuple(
            requested_information
        ),
        temporal_context=temporal_context,
        temporal_contexts=tuple(
            temporal_contexts
        ),
        intents=tuple(intents),
    )
