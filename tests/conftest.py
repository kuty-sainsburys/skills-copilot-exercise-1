from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities(monkeypatch):
    baseline = deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", baseline)


@pytest.fixture
def client():
    with TestClient(app_module.app) as test_client:
        yield test_client
