from __future__ import annotations

import logging

from astrosphere.monitoring.worker import main


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


if __name__ == "__main__":
    logging.info("Starting AstroSphere monitoring WebJob.")
    main()
