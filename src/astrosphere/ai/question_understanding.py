from astrosphere.ai.intent import (
    AICapabilityIntent,
)
from astrosphere.ai.intent_selector import (
    select_capability_intents,
)
from astrosphere.ai.scientific_question import (
    AIScientificQuestion,
)


_INFORMATION_KEYWORDS = {
    "distance": ("how far", "distance between", "distance from", "separation"),
    "planetary_defence": (
        "impact risk",
        "impact probability",
        "planetary defense",
        "planetary defence",
        "approaching earth",
        "asteroid risk",
        "asteroids approaching",
        "asteroids worth watching",
        "asteroid worth watching",
        "worth watching",
        "being monitored",
        "is being monitored",
        "currently monitored",
        "currently monitoring",
        "asteroid monitoring",
        "monitoring asteroids",
    ),
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

    # Concept/definition questions must not be interpreted as live
    # close-approach or planetary-defence queries merely because the
    # concept contains terms such as "near Earth" or "asteroid".
    #
    # Examples:
    #   "What is a near-Earth object?"
    #   "What are Earth-crossing asteroids?"
    #   "Define a near-Earth asteroid."
    definition_question = (
        normalized_question.startswith("what is ")
        or normalized_question.startswith("what are ")
        or normalized_question.startswith("define ")
        or normalized_question.startswith("explain ")
        or "what does " in normalized_question
    )

    scientific_concept_question = any(
        phrase in normalized_question
        for phrase in (
            "near-earth object",
            "near earth object",
            "near-earth asteroid",
            "near earth asteroid",
            "earth-crossing asteroid",
            "earth crossing asteroid",
            "earth-crossing object",
            "earth crossing object",
            "mars-crossing asteroid",
            "mars crossing asteroid",
            "near-earth objects",
            "near earth objects",
        )
    )

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

    # Definition questions about scientific concepts are conceptual
    # context questions, not live trajectory/close-approach requests.
    if definition_question and scientific_concept_question:
        requested_information = ["context"]
    elif len(requested_information) > 1:
        # "what is" and similar phrases provide generic context.
        # Keep context only when no more specific information was found.
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

    # Scientific concept/definition questions must remain conceptual.
    # Do not let lexical matches such as "near Earth", "asteroid",
    # "crossing", or "orbit" turn a definition request into a live
    # planetary-defence / relationship query.
    if definition_question and scientific_concept_question:
        intents = (
            AICapabilityIntent(
                capability_id="context",
                reason=(
                    "Scientific concept-definition question routed "
                    "to contextual explanation."
                ),
            ),
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
