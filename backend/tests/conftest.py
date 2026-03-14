import pytest
import app.utils.prompt_loader as pl


@pytest.fixture(autouse=True)
def reset_prompt_loader_singleton():
    """Reset prompt loader singleton between tests"""
    pl._prompt_loader = None
    yield
    pl._prompt_loader = None
