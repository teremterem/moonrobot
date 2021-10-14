import pytest
from telegram import Bot

pytest_plugins = [
    # 'tests.fixtures',
]


@pytest.fixture
def fake_bot():
    return Bot('1111111111:TESTESTESTESTESTESTESTESTESTESTEST')
