import pytest


@pytest.fixture(params=[0, 111, 222, 333])
def seed(request):
    return request.param
