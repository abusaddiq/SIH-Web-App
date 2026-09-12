"""Test settings: disable the IP rate-limiter so the automated suite is hermetic.

Run with:  .venv/bin/python manage.py test --settings config.settings_test
"""
from .settings import *  # noqa: F401,F403

RATELIMIT_ENABLE = False