"""Resolve celestial entities mentioned in natural-language AI questions."""
from dataclasses import dataclass
import re

from astrosphere.models.celestial_registry import CELESTIAL_OBJECTS, get_celestial_object


@dataclass(frozen=True)
class AIEntityResolution:
    entities: tuple
    reference_object_id: str | None = None
    target_object_id: str | None = None


_ALIASES = {
    "earth": "earth", "the earth": "earth", "terra": "earth",
    "mars": "mars", "the mars": "mars",
    "mercury": "mercury", "venus": "venus", "jupiter": "jupiter",
    "saturn": "saturn", "uranus": "uranus", "neptune": "neptune",
    "pluto": "pluto", "sun": "sun", "the sun": "sun",
    "moon": "moon", "the moon": "moon", "luna": "moon",
    "apophis": "asteroid:99942", "99942 apophis": "asteroid:99942",
    "99942": "asteroid:99942", "iss": "spacecraft:25544",
    "international space station": "spacecraft:25544",
}

# Prefer longer names first and match word boundaries.
_ENTITY_PATTERNS = sorted(
    ((alias, object_id) for alias, object_id in _ALIASES.items()),
    key=lambda item: len(item[0]), reverse=True,
)


def resolve_question_entities(question: str) -> AIEntityResolution:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("AI question is required.")

    normalized = re.sub(r"\s+", " ", question.strip().lower())

    # Scientific terminology can contain celestial-object names without
    # referring to that object as the subject of the question.
    #
    # Examples:
    #   "near-Earth object"
    #   "Earth-crossing asteroid"
    #   "Mars-crossing asteroid"
    #
    # These are concepts/classes, not references to the named body.
    concept_patterns = (
        r"\bnear[- ]earth\s+objects?\b",
        r"\bearth[- ]crossing\s+(?:asteroids?|objects?)\b",
        r"\bmars[- ]crossing\s+(?:asteroids?|objects?)\b",
    )

    concept_spans = []
    for pattern in concept_patterns:
        concept_spans.extend(
            (match.start(), match.end())
            for match in re.finditer(pattern, normalized)
        )

    found = []
    spans = list(concept_spans)

    for alias, object_id in _ENTITY_PATTERNS:
        pattern = r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])"
        for match in re.finditer(pattern, normalized):
            if any(match.start() < end and match.end() > start for start, end in spans):
                continue
            obj = get_celestial_object(object_id)
            if obj is None:
                continue
            found.append((match.start(), obj.id))
            spans.append((match.start(), match.end()))

    found.sort(key=lambda item: item[0])
    entity_ids = []
    for _, object_id in found:
        if object_id not in entity_ids:
            entity_ids.append(object_id)

    reference = entity_ids[0] if entity_ids else None
    target = entity_ids[1] if len(entity_ids) > 1 else None

    # For distance/relationship wording, the natural-language order is the
    # reference -> target order. "between X and Y" also follows mention order.
    return AIEntityResolution(
        entities=tuple(entity_ids),
        reference_object_id=reference,
        target_object_id=target,
    )


def resolve_object_or_default(question: str, explicit_object_id: str | None = None, conversation_object_id: str | None = None):
    """Resolve the primary subject while preserving explicit/conversation context.

    An explicit or conversation object represents the subject of a follow-up
    question. Entities discovered in the question may still represent a target
    body, such as Earth in "When is its closest approach to Earth?".
    """
    resolved = resolve_question_entities(question)

    for candidate in (explicit_object_id, conversation_object_id):
        if (
            isinstance(candidate, str)
            and candidate.strip()
            and get_celestial_object(candidate.strip().lower())
        ):
            subject = candidate.strip().lower()
            return AIEntityResolution(
                entities=tuple(
                    dict.fromkeys(
                        (subject,) + tuple(resolved.entities)
                    )
                ),
                reference_object_id=subject,
                target_object_id=resolved.target_object_id,
            )

    if resolved.reference_object_id:
        return resolved

    return AIEntityResolution(
        entities=("universe",),
        reference_object_id="universe",
    )
