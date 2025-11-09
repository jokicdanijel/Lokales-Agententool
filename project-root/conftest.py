import pytest

@pytest.fixture
def hello_world():
    return "Hello, World!"

def test_hello_world(hello_world):
    assert hello_world == "Hello, World!"