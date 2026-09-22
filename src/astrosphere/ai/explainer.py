from astrosphere.ai.explanation import AIExplanation


_CONCEPTS = {
    "position": {
        "what": {
            "beginner": (
                "Position tells us where a celestial object is located "
                "at a particular time."
            ),
            "standard": (
                "Position describes where a celestial object is located "
                "relative to a specified reference frame at a particular time."
            ),
            "detailed": (
                "Position describes where a celestial object is located "
                "relative to a specified reference frame at a particular time. "
                "The reported coordinates depend on the reference frame and "
                "observation time used by the scientific data source."
            ),
        },
        "why": {
            "beginner": (
                "Position matters because knowing where an object is helps "
                "us understand where it is in space and how it relates to "
                "other objects."
            ),
            "standard": (
                "Position is important because it provides the object's "
                "location at a defined time and reference frame, allowing "
                "its spatial relationships and motion to be studied."
            ),
            "detailed": (
                "Position is important because celestial motion is described "
                "relative to both time and a reference frame. Accurate "
                "position information provides the basis for determining "
                "spatial relationships and evaluating motion."
            ),
        },
        "how": {
            "beginner": (
                "Position is represented using coordinates that tell us "
                "where the object is."
            ),
            "standard": (
                "Position is represented by coordinates in a specified "
                "reference frame at a specified observation time."
            ),
            "detailed": (
                "Position is determined and represented as coordinates in "
                "a defined reference frame and epoch. The scientific data "
                "source supplies the coordinate values for the requested "
                "observation time."
            ),
        },
    },
    "velocity": {
        "what": {
            "beginner": (
                "Velocity tells us how an object's position is changing, "
                "including how fast it is moving and in which direction."
            ),
            "standard": (
                "Velocity describes how an object's position changes over time. "
                "It includes both speed and direction."
            ),
            "detailed": (
                "Velocity describes the rate and direction of change of an "
                "object's position. A velocity vector therefore contains "
                "directional components as well as the resulting speed."
            ),
        },
        "why": {
            "beginner": (
                "Velocity matters because it tells us both how quickly an "
                "object is moving and where it is moving toward."
            ),
            "standard": (
                "Velocity is important because speed alone does not describe "
                "the complete motion of a celestial object; its direction "
                "is also required."
            ),
            "detailed": (
                "Velocity is important because celestial motion is vector "
                "motion. Both magnitude and direction are needed to describe "
                "how an object's position changes and to model its subsequent "
                "motion."
            ),
        },
        "how": {
            "beginner": (
                "Velocity can be understood by looking at how position "
                "changes as time passes."
            ),
            "standard": (
                "Velocity is obtained from the rate of change of position "
                "with respect to time."
            ),
            "detailed": (
                "Velocity is the time derivative of position. Its vector "
                "components describe the rate of change along the coordinate "
                "axes, while the vector magnitude gives the object's speed."
            ),
        },
    },
    "trajectory": {
        "what": {
            "beginner": (
                "A trajectory is the path an object follows through space."
            ),
            "standard": (
                "A trajectory describes the path an object follows or is "
                "projected to follow through space over time."
            ),
            "detailed": (
                "A trajectory describes an object's path through space over "
                "time. A projected trajectory is derived from an orbital or "
                "dynamical model and therefore represents a calculated future "
                "path rather than a direct observation of every future position."
            ),
        },
        "why": {
            "beginner": (
                "A trajectory helps us understand where an object has been "
                "and where it may travel next."
            ),
            "standard": (
                "A trajectory is useful because it provides a time-dependent "
                "view of an object's motion rather than describing only one "
                "position."
            ),
            "detailed": (
                "A trajectory is useful because celestial motion is dynamic. "
                "Representing the path over time allows observations and "
                "calculated future states to be considered as part of a "
                "continuous orbital or dynamical model."
            ),
        },
        "how": {
            "beginner": (
                "A trajectory can be found by following how an object's "
                "position changes over time."
            ),
            "standard": (
                "A trajectory is calculated from an object's position, "
                "velocity, and the dynamical model used to describe its motion."
            ),
            "detailed": (
                "A trajectory is calculated by propagating an object's "
                "state through time using the relevant orbital or dynamical "
                "model. Future positions are therefore model-derived rather "
                "than direct observations of every future point."
            ),
        },
    },
    "close_approach": {
        "what": {
            "beginner": (
                "A close approach happens when two objects come relatively "
                "close to each other."
            ),
            "standard": (
                "A close approach is an event in which two celestial objects "
                "reach a relatively small separation at a particular time."
            ),
            "detailed": (
                "A close approach is an event in which two celestial objects "
                "reach a minimum separation during a specified encounter. "
                "The reported distance and encounter time depend on the "
                "underlying orbital data and calculation."
            ),
        },
        "why": {
            "beginner": (
                "Close approaches are useful because they show when two "
                "objects pass relatively near each other."
            ),
            "standard": (
                "Close approaches are important because the separation and "
                "timing of an encounter describe how closely two objects "
                "pass during their motion."
            ),
            "detailed": (
                "Close approaches provide a defined way to characterize "
                "encounters between celestial objects. Their timing and "
                "minimum separation can be evaluated from the underlying "
                "orbital information."
            ),
        },
        "how": {
            "beginner": (
                "A close approach is identified by finding when the "
                "distance between two objects becomes smallest."
            ),
            "standard": (
                "A close approach is determined by evaluating the separation "
                "between two objects over time and identifying the minimum."
            ),
            "detailed": (
                "A close approach is determined by evaluating relative "
                "positions over an interval and locating the time at which "
                "the calculated separation reaches its minimum."
            ),
        },
    },
    "space_weather": {
        "what": {
            "beginner": (
                "Space weather describes changing conditions in space that "
                "can be affected by activity from the Sun."
            ),
            "standard": (
                "Space weather describes changing conditions in near-Earth "
                "space that can be influenced by solar activity."
            ),
            "detailed": (
                "Space weather describes changing conditions in near-Earth "
                "space associated with solar activity and its interaction "
                "with the space environment. Measurements can include solar "
                "wind properties and indicators of Earth's geomagnetic state."
            ),
        },
        "why": {
            "beginner": (
                "Space weather matters because changes in the space "
                "environment can affect systems operating near Earth."
            ),
            "standard": (
                "Space weather is monitored because changes in the "
                "near-Earth environment can affect technological and "
                "space-based systems."
            ),
            "detailed": (
                "Space weather is monitored because variations in the "
                "near-Earth environment can interact with spacecraft, "
                "communications, navigation systems, and Earth's "
                "geomagnetic environment."
            ),
        },
        "how": {
            "beginner": (
                "Space weather is described by measuring conditions such "
                "as the solar wind and Earth's magnetic environment."
            ),
            "standard": (
                "Space weather is characterized using measurements of "
                "solar-wind properties and indicators of geomagnetic activity."
            ),
            "detailed": (
                "Space weather is characterized using observations of "
                "solar-wind conditions, magnetic-field measurements, and "
                "geomagnetic indices that describe changes in the "
                "near-Earth environment."
            ),
        },
    },
    "solar_wind": {
        "what": {
            "beginner": (
                "The solar wind is a stream of charged particles that flows "
                "away from the Sun."
            ),
            "standard": (
                "The solar wind is a continuous flow of charged particles "
                "from the Sun through interplanetary space."
            ),
            "detailed": (
                "The solar wind is a flow of charged particles originating "
                "from the Sun and moving through interplanetary space. "
                "Scientific observations can characterize properties such "
                "as particle speed, density, and temperature."
            ),
        },
        "why": {
            "beginner": (
                "The solar wind matters because it carries solar activity "
                "through space and interacts with the space environment."
            ),
            "standard": (
                "The solar wind is important because its changing "
                "properties contribute to variations in the space "
                "environment around Earth."
            ),
            "detailed": (
                "The solar wind is important because variations in its "
                "particle and magnetic properties contribute to changes "
                "in the near-Earth space environment and can influence "
                "geomagnetic conditions."
            ),
        },
        "how": {
            "beginner": (
                "The solar wind can be described by measuring properties "
                "such as how fast its particles are moving."
            ),
            "standard": (
                "The solar wind is characterized using measurements such "
                "as particle speed, density, and temperature."
            ),
            "detailed": (
                "Solar-wind conditions are characterized through measured "
                "particle properties such as speed, density, and temperature, "
                "together with relevant magnetic-field measurements."
            ),
        },
    },
    "magnetic_field": {
        "what": {
            "beginner": (
                "A magnetic field describes the magnetic environment around "
                "an object or in a region of space."
            ),
            "standard": (
                "A magnetic field describes the magnetic environment around "
                "an object or within a region of space."
            ),
            "detailed": (
                "A magnetic field describes the magnetic environment at a "
                "location in space. Measurements can represent the field "
                "strength and directional components in a specified "
                "coordinate system."
            ),
        },
        "why": {
            "beginner": (
                "A magnetic field is useful for understanding the magnetic "
                "conditions surrounding an object or region."
            ),
            "standard": (
                "Magnetic-field information is important because it "
                "characterizes the magnetic environment in which an object "
                "or particle population exists."
            ),
            "detailed": (
                "Magnetic-field measurements are important because both "
                "field strength and direction describe the magnetic "
                "environment and its variation over time and location."
            ),
        },
        "how": {
            "beginner": (
                "A magnetic field can be described by measuring its strength "
                "and direction."
            ),
            "standard": (
                "A magnetic field is characterized by measurements of "
                "its magnitude and directional components."
            ),
            "detailed": (
                "A magnetic field is represented using vector components "
                "in a specified coordinate system. The components together "
                "describe the field's magnitude and direction."
            ),
        },
    },
    "geomagnetic": {
        "what": {
            "beginner": (
                "Geomagnetic conditions describe what is happening in "
                "Earth's magnetic environment."
            ),
            "standard": (
                "Geomagnetic conditions describe the response and state of "
                "Earth's magnetic environment."
            ),
            "detailed": (
                "Geomagnetic conditions describe the state and variability "
                "of Earth's magnetic environment. Indices such as Kp provide "
                "standardized measures used to characterize geomagnetic "
                "activity."
            ),
        },
        "why": {
            "beginner": (
                "Geomagnetic conditions help us understand changes in "
                "Earth's magnetic environment."
            ),
            "standard": (
                "Geomagnetic information is useful for describing changes "
                "in Earth's magnetic environment associated with varying "
                "space-weather conditions."
            ),
            "detailed": (
                "Geomagnetic information provides standardized measures "
                "of changes in Earth's magnetic environment and is used "
                "to characterize geomagnetic activity."
            ),
        },
        "how": {
            "beginner": (
                "Geomagnetic activity can be described using measurements "
                "and indices such as Kp."
            ),
            "standard": (
                "Geomagnetic conditions are characterized using magnetic "
                "measurements and standardized indices such as Kp."
            ),
            "detailed": (
                "Geomagnetic conditions are characterized using observations "
                "of Earth's magnetic environment together with standardized "
                "indices such as Kp that summarize geomagnetic activity."
            ),
        },
    },
    "relationships": {
        "what": {
            "beginner": (
                "Celestial relationships show how objects are connected, "
                "such as a planet belonging to a star system."
            ),
            "standard": (
                "Celestial relationships describe how objects are connected "
                "within a hierarchy, such as an object orbiting or belonging "
                "to another system."
            ),
            "detailed": (
                "Celestial relationships represent structural connections "
                "between canonical objects. These can include parent-child "
                "relationships and system membership, allowing objects to "
                "be understood within a larger celestial hierarchy."
            ),
        },
        "why": {
            "beginner": (
                "Relationships help us understand where an object belongs "
                "in the larger structure of a celestial system."
            ),
            "standard": (
                "Celestial relationships are useful because they place an "
                "object within its broader system and identify its structural "
                "connections to other objects."
            ),
            "detailed": (
                "Celestial relationships provide structural context for "
                "canonical objects. They allow an object's parent, children, "
                "and system membership to be represented consistently."
            ),
        },
        "how": {
            "beginner": (
                "Relationships can be described by identifying which "
                "objects belong to or are connected with one another."
            ),
            "standard": (
                "Relationships are represented using canonical object "
                "connections such as parent-child and system membership."
            ),
            "detailed": (
                "Relationships are represented through canonical object "
                "identifiers and explicit structural links. These links "
                "can then be traversed to determine parents, children, "
                "ancestors, and system membership."
            ),
        },
    },
}


_LEVELS = {
    "beginner",
    "standard",
    "detailed",
}

_EXPLANATION_TYPES = {
    "what",
    "why",
    "how",
}


def explain_scientific_concept(
    subject,
    level="standard",
    explanation_type="what",
):
    if not isinstance(subject, str) or not subject.strip():
        raise ValueError("Explanation subject is required.")

    if not isinstance(level, str) or not level.strip():
        raise ValueError("Explanation level is required.")

    if (
        not isinstance(explanation_type, str)
        or not explanation_type.strip()
    ):
        raise ValueError(
            "Explanation type is required."
        )

    normalized_subject = subject.strip().lower()
    normalized_level = level.strip().lower()
    normalized_type = explanation_type.strip().lower()

    if normalized_subject not in _CONCEPTS:
        raise ValueError(
            f"Unsupported scientific concept: {normalized_subject}"
        )

    if normalized_level not in _LEVELS:
        raise ValueError(
            f"Unsupported explanation level: {normalized_level}"
        )

    if normalized_type not in _EXPLANATION_TYPES:
        raise ValueError(
            f"Unsupported explanation type: {normalized_type}"
        )

    return AIExplanation(
        subject=normalized_subject,
        explanation=_CONCEPTS[
            normalized_subject
        ][normalized_type][normalized_level],
        level=normalized_level,
        explanation_type=normalized_type,
    )
