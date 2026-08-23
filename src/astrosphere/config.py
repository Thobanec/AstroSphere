import os


class AppConfig:
    """
    Application configuration loaded from environment variables.
    """

    DEBUG = os.getenv(
        "ASTROSPHERE_DEBUG",
        "false",
    ).lower() == "true"

    HOST = os.getenv(
        "ASTROSPHERE_HOST",
        "127.0.0.1",
    )

    PORT = int(
        os.getenv(
            "ASTROSPHERE_PORT",
            "5000",
        )
    )