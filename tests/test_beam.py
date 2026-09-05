import pytest
from beam import *

def test_beam_creation():
    beam = Beam(10.0)
    assert beam.length == 10

def test_gocp_creates_point():
    beam = Beam(10.0)
    point = beam.get_or_create_point(3)

    assert point.x == 3
    assert len(beam.points) == 1


def test_gocp_sorts_points():
    beam = Beam(10.0)
    beam.get_or_create_point(7)
    beam.get_or_create_point(3)

    assert beam.points[0].x == 3
    assert beam.points[1].x == 7


def test_gocp_reuses_point_within_tolerance():
    beam = Beam(10.0)
    original = beam.get_or_create_point(7)
    same_point = beam.get_or_create_point(7 + TOLERANCE / 10)

    assert original is same_point
    assert len(beam.points) == 1

def test_add_event():
    beam = Beam(10.0)
    point = beam.get_or_create_point(7)
    beam.add_event(point.x, PointLoad(15))

    assert len(point.events) == 1

    event = point.events[0]

    assert isinstance(event, PointLoad)
    assert event.force == 15


def test_clear_reactions():
    beam = Beam(10.0)
    beam.add_event(0, Support(FIXED))
    beam.add_event(0, Reaction(15.0))
    beam.add_event(0, ReactionMoment(30.0))
    beam.add_event(5, PointLoad(-10.0))

    assert len(beam.get_or_create_point(0).events) == 3

    beam.clear_reactions()
    point_0 = beam.get_or_create_point(0).events
    point_5 = beam.get_or_create_point(5).events
    point_5_event = point_5[0]

    assert len(point_0) == 1
    assert isinstance(point_0[0], Support)

    assert len(point_5) == 1
    assert isinstance(point_5_event, PointLoad)
    assert point_5_event.force == -10.0


def test_query_methods_filter_correctly():
    beam = Beam(10.0)

    # Setup
    beam.add_event(0, Support(PINNED))
    beam.add_event(10, Support(ROLLER))
    beam.add_event(5, PointLoad(-20.0))
    beam.add_event(7, AppliedMoment(15.0))
    beam.add_distributed_event(UniformDistributedLoad(0, 5, -10.0))
    beam.add_distributed_event(UniformVaryingLoad(5, 10, 0, -10.0))

    # Supports
    supports = list(beam.supports())

    assert len(supports) == 2
    assert supports[0][0] == 0  # x location
    assert isinstance(supports[0][1], Support)

    # Point Loads
    pt_loads = list(beam.point_loads())

    assert len(pt_loads) == 1
    assert pt_loads[0][0] == 5
    assert pt_loads[0][1].force == -20.0
    assert isinstance(pt_loads[0][1], PointLoad)

    # Applied Moments
    moments = list(beam.applied_moments())

    assert len(moments) == 1
    assert moments[0][0] == 7
    assert moments[0][1].moment == 15.0
    assert isinstance(moments[0][1], AppliedMoment)

    # UDLs
    udls = list(beam.udls())

    assert len(udls) == 1
    assert isinstance(udls[0], UniformDistributedLoad)
    assert udls[0].start_x == 0
    assert udls[0].end_x == 5
    assert udls[0].intensity == -10.0

    # UVLs
    uvls = list(beam.uvls())

    assert len(uvls) == 1
    assert isinstance(uvls[0], UniformVaryingLoad)
    assert uvls[0].start_x == 5
    assert uvls[0].end_x == 10
    assert uvls[0].w1 == 0
    assert uvls[0].w2 == -10.0


def test_udl_math():
    udl = UniformDistributedLoad(2.0, 6.0, -10.0)

    assert udl.span == 4.0
    assert udl.centroid_x == 4.0  # (2 + 6) / 2
    assert udl.resultant_force == pytest.approx(-40.0)  # 4 * -10


def test_uvl_math():
    uvl = UniformVaryingLoad(0.0, 15.0, 0.0, -10.0)

    assert uvl.span == 15.0
    assert uvl.resultant_force == pytest.approx(-75.0)  # 0.5 * 15 * -10
    assert uvl.centroid_x == pytest.approx(10)  # Centroid of a triangle from 0 to 15 leaning right is at 2/3 of the base


def test_equivalent_loads():
    beam = Beam(10.0)

    beam.add_distributed_event(UniformDistributedLoad(0, 4, -10))
    beam.add_distributed_event(UniformVaryingLoad(4, 10, 0, -6))
    beam.add_event(3, PointLoad(-20))
    beam.add_event(7, AppliedMoment(15))

    equivalent = list(beam.equivalent_loads())
    equivalent.sort(key=lambda item: item[0])

    assert len(equivalent) == 3

    assert equivalent[0][0] == pytest.approx(2.0)
    assert equivalent[0][1] == pytest.approx(-40.0)

    assert equivalent[1][0] == pytest.approx(3.0)
    assert equivalent[1][1] == pytest.approx(-20.0)

    assert equivalent[2][0] == pytest.approx(8.0)
    assert equivalent[2][1] == pytest.approx(-18.0)
