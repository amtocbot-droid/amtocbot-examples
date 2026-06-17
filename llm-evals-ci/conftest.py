import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "llm_judge: mark test as requiring LLM API (expensive — run on merge only)"
    )
