from astrosphere.config import AppConfig


def test_default_host():
    assert AppConfig.HOST == "127.0.0.1"


def test_default_port():
    assert AppConfig.PORT == 5000


def test_debug_is_boolean():
    assert isinstance(
        AppConfig.DEBUG,
        bool,
    )