from dataclasses import dataclass
from datetime import datetime

from astrosphere.models.planetary import PlanetaryObject


@dataclass
class AnalysisConfig:
    start_date: datetime
    months: int
    interval_days: int
    reference_body: PlanetaryObject