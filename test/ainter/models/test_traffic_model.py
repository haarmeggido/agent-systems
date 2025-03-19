from ainter.models.traffic_model import TrafficModel


def test_traffic_model():
    assert TrafficModel().intersection_center == (5, 5)