import pytest
from shapely import LineString

from ainter.models.autonomous_intersection.intersection_directions import IntersectionEntranceDirection
from ainter.models.nagel_schreckenberg.intersection import create_edge_directions


@pytest.fixture
def intersection_data():
    return {
        'osm_id': 123,
        'x': 100.0,
        'y': 100.0
    }

def test_empty_edges(intersection_data):
    edge_directions, used_directions = create_edge_directions(
        intersection_data['osm_id'],
        intersection_data['x'],
        intersection_data['y'],
        {}
    )

    assert len(edge_directions) == 0
    assert len(used_directions) == 0

def test_cardinal_directions(intersection_data):
    edges_info = {
        # EAST
        (456, 123): {
            'geometry': LineString([[120.0, 100.0], [100.0, 100.0]]),
            'name': 'abc',
            'lanes': 2
        },
        # NORTH
        (123, 789): {
            'geometry': LineString([[100.0, 100.0], [100.0, 120.0]]),
            'name': 'abc',
            'lanes': 1
        },
        # WEST
        (101, 123): {
            'geometry': LineString([[080.0, 100.0], [100.0, 100.0]]),
            'name': 'abc',
            'lanes': 3
        },
        # SOUTH
        (123, 202): {
            'geometry': LineString([[100.0, 100.0], [100.0, 80.0]]),
            'name': 'abc',
            'lanes': 2
        }
    }

    edge_directions, used_directions = create_edge_directions(
        intersection_data['osm_id'],
        intersection_data['x'],
        intersection_data['y'],
        edges_info
    )

    assert len(edge_directions) == 4
    assert len(used_directions) == 4

    assert edge_directions[(456, 123)].direction == IntersectionEntranceDirection.EAST
    assert edge_directions[(123, 789)].direction == IntersectionEntranceDirection.NORTH
    assert edge_directions[(101, 123)].direction == IntersectionEntranceDirection.WEST
    assert edge_directions[(123, 202)].direction == IntersectionEntranceDirection.SOUTH

    assert edge_directions[(456, 123)].lanes == 2
    assert edge_directions[(123, 789)].lanes == 1
    assert edge_directions[(101, 123)].lanes == 3
    assert edge_directions[(123, 202)].lanes == 2

    assert (IntersectionEntranceDirection.EAST, True) in used_directions
    assert (IntersectionEntranceDirection.NORTH, False) in used_directions
    assert (IntersectionEntranceDirection.WEST, True) in used_directions
    assert (IntersectionEntranceDirection.SOUTH, False) in used_directions

def test_diagonal_directions(intersection_data):
    edges_info = {
        (123, 456): {
            'geometry': LineString([[100.0, 100.0], [110.0, 115.0]]),
            'name': 'abc',
            'lanes': 1
        },
        (123, 789): {
            'geometry': LineString([[100.0, 100.0], [115.0, 90.0]]),
            'name': 'abc',
            'lanes': 2
        }
    }

    edge_directions, used_directions = create_edge_directions(
        intersection_data['osm_id'],
        intersection_data['x'],
        intersection_data['y'],
        edges_info
    )

    assert edge_directions[(123, 456)].direction == IntersectionEntranceDirection.NORTH
    assert edge_directions[(123, 789)].direction == IntersectionEntranceDirection.EAST

def test_edge_case_angles(intersection_data):
    edges_info = {
        (123, 456): {
            'geometry': LineString([[100.0, 100.0], [110.0, 110.0]]),
            'name': 'abc',
            'lanes': 1
        },
        (123, 789): {
            'geometry': LineString([[100.0, 100.0], [90.0, 110.0]]),
            'name': 'abc',
            'lanes': 1
        },
        (123, 101): {
            'geometry': LineString([[100.0, 100.0], [90.0, 90.0]]),
            'name': 'abc',
            'lanes': 1
        }
    }

    edge_directions, used_directions = create_edge_directions(
        intersection_data['osm_id'],
        intersection_data['x'],
        intersection_data['y'],
        edges_info
    )

    assert edge_directions[(123, 456)].direction == IntersectionEntranceDirection.NORTH
    assert edge_directions[(123, 789)].direction == IntersectionEntranceDirection.WEST
    assert edge_directions[(123, 101)].direction == IntersectionEntranceDirection.SOUTH

def test_duplicate_directions_error(intersection_data):
    edges_info = {
        (456, 123): {
            'geometry': LineString([[120.0, 100.0], [100.0, 100.0]]),
            'name': 'abc',
            'lanes': 2
        },
        (789, 123): {
            'geometry': LineString([[130.0, 105.0], [100.0, 100.0]]),
            'name': 'abc',
            'lanes': 1
        }
    }

    with pytest.raises(AssertionError, match="Two many one way directions"):
        create_edge_directions(
            intersection_data['osm_id'],
            intersection_data['x'],
            intersection_data['y'],
            edges_info
        )

def test_all_directions_with_incoming_outgoing(intersection_data):
    edges_info = {
        # Wchodząca ze wschodu
        (456, 123): {
            'geometry': LineString([[120.0, 100.0], [100.0, 100.0]]),
            'name': 'abc',
            'lanes': 2
        },
        # Wychodząca na wschód
        (123, 457): {
            'geometry': LineString([[100.0, 100.0], [120.0, 100.0]]),
            'name': 'abc',
            'lanes': 1
        },
        # Wchodząca z północy
        (789, 123): {
            'geometry': LineString([[100.0, 120.0], [100.0, 100.0]]),
            'name': 'abc',
            'lanes': 1
        },
        # Wychodząca na północ
        (123, 790): {
            'geometry': LineString([[100.0, 100.0], [100.0, 120.0]]),
            'name': 'abc',
            'lanes': 2
        },
        # Wchodząca z zachodu
        (101, 123): {
            'geometry': LineString([[80.0, 100.0], [100.0, 100.0]]),
            'name': 'abc',
            'lanes': 2
        },
        # Wychodząca na zachód
        (123, 102): {
            'geometry': LineString([[100.0, 100.0], [80.0, 100.0]]),
            'name': 'abc',
            'lanes': 1
        },
        # Wchodząca z południa
        (201, 123): {
            'geometry': LineString([[100.0, 80.0], [100.0, 100.0]]),
            'name': 'abc',
            'lanes': 1
        },
        # Wychodząca na południe
        (123, 202): {
            'geometry': LineString([[100.0, 100.0], [100.0, 80.0]]),
            'name': 'abc',
            'lanes': 2
        }
    }

    edge_directions, used_directions = create_edge_directions(
        intersection_data['osm_id'],
        intersection_data['x'],
        intersection_data['y'],
        edges_info
    )

    assert len(edge_directions) == 8
    assert len(used_directions) == 8

    assert (IntersectionEntranceDirection.EAST, True) in used_directions
    assert (IntersectionEntranceDirection.EAST, False) in used_directions
    assert (IntersectionEntranceDirection.NORTH, True) in used_directions
    assert (IntersectionEntranceDirection.NORTH, False) in used_directions
    assert (IntersectionEntranceDirection.WEST, True) in used_directions
    assert (IntersectionEntranceDirection.WEST, False) in used_directions
    assert (IntersectionEntranceDirection.SOUTH, True) in used_directions
    assert (IntersectionEntranceDirection.SOUTH, False) in used_directions
