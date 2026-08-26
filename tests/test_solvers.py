import pytest
import numpy as np
from beam import *
from solvers import solve_reactions, calculate_sfd_bmd


def get_reaction_forces(beam):
    return {p.x: ev.force for p in beam.points for ev in p.events if isinstance(ev, Reaction)}


def get_reaction_moments(beam):
    return {p.x: ev.moment for p in beam.points for ev in p.events if isinstance(ev, ReactionMoment)}


def test_solve_reactions_central_point_load():
    beam = Beam(10.0)
    beam.add_event(0, Support(PINNED))
    beam.add_event(10, Support(ROLLER))
    beam.add_event(5, PointLoad(-20.0))

    results = solve_reactions(beam)

    # Check the dictionary return
    assert results["R_A"] == pytest.approx(10.0)
    assert results["R_B"] == pytest.approx(10.0)

    # Check the actual Beam state (were events added?)
    rxns = get_reaction_forces(beam)
    assert len(rxns) == 2
    assert rxns[0.0] == pytest.approx(10.0)
    assert rxns[10.0] == pytest.approx(10.0)


def test_solve_reactions_asymmetric_point_load():
    beam = Beam(10.0)
    beam.add_event(0, Support(PINNED))
    beam.add_event(10, Support(ROLLER))
    beam.add_event(4, PointLoad(-20.0))

    solve_reactions(beam)
    rxns = get_reaction_forces(beam)

    assert rxns[0.0] == pytest.approx(12.0)
    assert rxns[10.0] == pytest.approx(8.0)


def test_solve_reactions_udl():
    beam = Beam(10.0)
    beam.add_event(0, Support(PINNED))
    beam.add_event(10, Support(ROLLER))

    beam.add_distributed_event(UniformDistributedLoad(0, 10, -2.0))

    solve_reactions(beam)
    rxns = get_reaction_forces(beam)

    assert rxns[0.0] == pytest.approx(10.0)
    assert rxns[10.0] == pytest.approx(10.0)


def test_solve_reactions_uvl():
    beam = Beam(10.0)
    beam.add_event(0, Support(PINNED))
    beam.add_event(10, Support(ROLLER))

    beam.add_distributed_event(UniformVaryingLoad(0, 10, 0, -3.0))

    solve_reactions(beam)
    rxns = get_reaction_forces(beam)

    assert rxns[0.0] == pytest.approx(5.0)
    assert rxns[10.0] == pytest.approx(10.0)


def test_solve_reactions_applied_moment():
    beam = Beam(10.0)
    beam.add_event(0, Support(PINNED))
    beam.add_event(10, Support(ROLLER))

    beam.add_event(5, AppliedMoment(20.0))

    solve_reactions(beam)
    rxns = get_reaction_forces(beam)

    assert rxns[0.0] == pytest.approx(2.0)
    assert rxns[10.0] == pytest.approx(-2.0)


def test_solve_reactions_cantilever_point_load():
    beam = Beam(10.0)
    beam.add_event(0, Support(FIXED))
    beam.add_event(5, PointLoad(-20.0))

    solve_reactions(beam)

    rxns = get_reaction_forces(beam)
    moments = get_reaction_moments(beam)

    assert rxns[0.0] == pytest.approx(20.0)

    assert moments[0.0] == pytest.approx(100.0)


def test_solve_reactions_cantilever_distributed():
    beam = Beam(10.0)
    beam.add_event(0, Support(FIXED))
    beam.add_distributed_event(UniformDistributedLoad(0, 10, -2.0))

    solve_reactions(beam)
    rxns = get_reaction_forces(beam)
    moments = get_reaction_moments(beam)

    assert rxns[0.0] == pytest.approx(20.0)
    # Centroid at 5m -> Moment = -20 * 5 = -100 -> Reaction = 100
    assert moments[0.0] == pytest.approx(100.0)


def test_sfd_bmd_central_point_load():
    beam = Beam(10.0)
    beam.add_event(0, Support(PINNED))
    beam.add_event(10, Support(ROLLER))
    beam.add_event(5, PointLoad(-20.0))
    solve_reactions(beam)  # Required before calculating diagrams

    x_arr, sfd, bmd = calculate_sfd_bmd(beam)

    idx_center = np.argmin(np.abs(x_arr - 5.0))
    assert bmd[idx_center] == pytest.approx(50.0)

    idx_left = np.argmin(np.abs(x_arr - 2.5))
    idx_right = np.argmin(np.abs(x_arr - 7.5))

    assert sfd[idx_left] == pytest.approx(10.0)
    assert sfd[idx_right] == pytest.approx(-10.0)


def test_sfd_bmd_point_load_jump():
    beam = Beam(10.0)
    beam.add_event(0, Support(PINNED))
    beam.add_event(10, Support(ROLLER))
    beam.add_event(5, PointLoad(-20.0))
    solve_reactions(beam)

    x_arr, sfd, _ = calculate_sfd_bmd(beam)

    idx_before = np.argmin(np.abs(x_arr - (5.0 - 1e-7)))
    idx_after = np.argmin(np.abs(x_arr - (5.0 + 1e-7)))

    assert sfd[idx_before] == pytest.approx(10.0)
    assert sfd[idx_after] == pytest.approx(-10.0)
    assert sfd[idx_after] - sfd[idx_before] == pytest.approx(-20.0)


def test_sfd_bmd_applied_moment_jump():
    beam = Beam(10.0)
    beam.add_event(0, Support(PINNED))
    beam.add_event(10, Support(ROLLER))
    beam.add_event(5, AppliedMoment(20.0))
    solve_reactions(beam)

    x_arr, _, bmd = calculate_sfd_bmd(beam)

    idx_before = np.argmin(np.abs(x_arr - (5.0 - 1e-7)))
    idx_after = np.argmin(np.abs(x_arr - (5.0 + 1e-7)))

    jump = bmd[idx_after] - bmd[idx_before]
    assert jump == pytest.approx(20.0)


def test_solve_reactions_invalid_supports():
    beam = Beam(10.0)
    beam.add_event(0, Support(PINNED))
    beam.add_event(5, Support(ROLLER))
    beam.add_event(10, Support(ROLLER))  # 3 supports!

    with pytest.raises(ValueError, match="Solver requires 1 support"):
        solve_reactions(beam)


def test_solve_reactions_cantilever_not_at_zero():
    beam = Beam(10.0)
    beam.add_event(5, Support(FIXED))

    with pytest.raises(ValueError, match="Cantilever fixed support must be at x = 0.0m"):
        solve_reactions(beam)


def test_sfd_bmd_zero_load_beam():
    beam = Beam(10.0)
    beam.add_event(0, Support(PINNED))
    beam.add_event(10, Support(ROLLER))

    solve_reactions(beam)
    x_arr, sfd, bmd = calculate_sfd_bmd(beam)

    assert np.allclose(sfd, 0.0)
    assert np.allclose(bmd, 0.0)