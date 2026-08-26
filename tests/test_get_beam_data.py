from beam import (
    PINNED, ROLLER, FIXED
)
from get_beam_data import get_beam_data

def test_get_beam_data_simply_supported(monkeypatch):
    inputs = iter([
        "10.0",  # length
        "2",  # supports count (simply supported)
        "",  # support A default (0.0)
        "",  # support B default (10.0)
        "5.0",  # point load locations
        "-20.0",  # point load magnitudes
        "",  # moment locations (skip)
        "0",  # udl count
        "0"  # uvl count
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    beam = get_beam_data()

    assert beam.length == 10.0

    supports = list(beam.supports())
    assert len(supports) == 2
    assert supports[0][0] == 0.0
    assert supports[0][1].support_type == PINNED
    assert supports[1][0] == 10.0
    assert supports[1][1].support_type == ROLLER

    pt_loads = list(beam.point_loads())
    assert len(pt_loads) == 1
    assert pt_loads[0][0] == 5.0
    assert pt_loads[0][1].force == -20.0


def test_get_beam_data_cantilever(monkeypatch):
    inputs = iter([
        "8.0",  # length
        "1",  # supports count (cantilever)
        "",  # point load locations (skip)
        "4.0",  # moment locations
        "15.0",  # moment magnitudes
        "0",  # udl count
        "0"  # uvl count
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    beam = get_beam_data()

    assert beam.length == 8.0

    supports = list(beam.supports())
    assert len(supports) == 1
    assert supports[0][0] == 0.0
    assert supports[0][1].support_type == FIXED

    moments = list(beam.applied_moments())
    assert len(moments) == 1
    assert moments[0][0] == 4.0
    assert moments[0][1].moment == 15.0


def test_get_beam_data_with_distributed_loads(monkeypatch):
    inputs = iter([
        "10.0",  # length
        "2",  # supports count
        "0",  # support A location
        "10",  # support B location
        "",  # point loads (skip)
        "",  # moments (skip)
        "1",  # udl count
        "0, 5, -10.0",  # udl spec: start, end, intensity
        "1",  # uvl count
        "5, 10, 0, -5.0"  # uvl spec: start, end, w1, w2
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    beam = get_beam_data()

    assert len(beam.distributed_events) == 2

    udls = list(beam.udls())
    uvls = list(beam.uvls())

    assert len(udls) == 1
    assert udls[0].start_x == 0.0
    assert udls[0].end_x == 5.0
    assert udls[0].intensity == -10.0

    assert len(uvls) == 1
    assert uvls[0].start_x == 5.0
    assert uvls[0].end_x == 10.0
    assert uvls[0].w1 == 0.0
    assert uvls[0].w2 == -5.0


def test_get_beam_data_invalid_length_retry(monkeypatch):
    inputs = iter([
        "-5.0",  # invalid length first (triggers retry loop)
        "10.0",  # valid length second
        "2",  # supports count
        "0",  # support A
        "10",  # support B
        "",  # point loads (skip)
        "",  # moments (skip)
        "0",  # udl count
        "0"  # uvl count
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    beam = get_beam_data()

    assert beam.length == 10.0