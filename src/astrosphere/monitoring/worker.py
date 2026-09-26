from __future__ import annotations

import logging
import signal

from .analyzers.asteroid_risk import (
    assess_asteroid_event,
)
from .analyzers.space_weather import (
    assess_space_weather_event,
)
from .config import (
    get_monitoring_database_path,
)
from .engine import MonitoringEngine
from .runtime import (
    MonitoringWorker,
)
from .scheduler import (
    build_monitoring_scheduler,
)
from .store import MonitoringStore


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s "
            "%(message)s"
        ),
    )


def build_monitoring_worker() -> MonitoringWorker:
    database_path = (
        get_monitoring_database_path()
    )

    store = MonitoringStore(
        database_path
    )

    engine = MonitoringEngine(
        store=store,
        asteroid_analyzer=(
            assess_asteroid_event
        ),
        space_weather_analyzer=(
            assess_space_weather_event
        ),
    )

    scheduler = build_monitoring_scheduler(
        engine=engine,
        cneos_lookahead_days=30,
    )

    return MonitoringWorker(
        scheduler=scheduler,
    )


def main() -> None:
    configure_logging()

    worker = build_monitoring_worker()

    def shutdown(
        signum: int,
        _frame,
    ) -> None:
        logging.getLogger(__name__).info(
            "Received signal %s.",
            signum,
        )

        worker.stop()

    signal.signal(
        signal.SIGINT,
        shutdown,
    )

    if hasattr(signal, "SIGTERM"):
        signal.signal(
            signal.SIGTERM,
            shutdown,
        )

    worker.run_forever()


if __name__ == "__main__":
    main()