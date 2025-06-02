import pytest


@pytest.fixture(params=[0, 111, 222, 333, 444])
def seed(request):
    return request.param
