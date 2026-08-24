from typing import Generator

TOLERANCE = 1e-6

# Support Constants
PINNED = "pinned"
ROLLER = "roller"
FIXED = "fixed"


class Event:
    """Base class for any physical entity on the beam."""
    pass


class PointEvent(Event):
    """Base class for events at a discrete point x."""
    pass


class DistributedEvent(Event):
    """Base class for loads spanning from start_x to end_x."""

    def __init__(self, start_x: float, end_x: float):
        if end_x <= start_x:
            raise ValueError(f"end_x ({end_x}m) must be strictly greater than start_x ({start_x}m).")
        self.start_x = start_x
        self.end_x = end_x

    @property
    def span(self) -> float:
        return self.end_x - self.start_x


# --- Point Events ---

class PointLoad(PointEvent):
    def __init__(self, force: float):
        self.force = force


class AppliedMoment(PointEvent):
    def __init__(self, moment: float):
        self.moment = moment


class Reaction(PointEvent):
    def __init__(self, force: float):
        self.force = force


class ReactionMoment(PointEvent):
    def __init__(self, moment: float = 0.0):
        self.moment = moment


class Support(PointEvent):
    def __init__(self, support_type: str):
        self.support_type = support_type


# --- Distributed Events ---

class UniformDistributedLoad(DistributedEvent):
    def __init__(self, start_x: float, end_x: float, intensity: float):
        super().__init__(start_x, end_x)
        self.intensity = intensity

    @property
    def resultant_force(self) -> float:
        return self.intensity * self.span

    @property
    def centroid_x(self) -> float:
        return self.start_x + (self.span / 2.0)


class UniformVaryingLoad(DistributedEvent):
    """Uniform Varying Load (kN/m) spanning start_x to end_x."""

    def __init__(self, start_x: float, end_x: float, w1: float, w2: float):
        super().__init__(start_x, end_x)
        self.w1 = w1
        self.w2 = w2

    @property
    def resultant_force(self) -> float:
        """Area of trapezoid: ((w1 + w2) / 2) * L"""
        return ((self.w1 + self.w2) / 2.0) * self.span

    @property
    def centroid_x(self) -> float:
        """Centroid of trapezoid relative to start_x."""
        if abs(self.w1 + self.w2) < TOLERANCE:
            return self.start_x + (self.span / 2.0)

        # Standard centroid formula for trapezoid/triangle
        return self.start_x + (self.span / 3.0) * ((self.w1 + 2 * self.w2) / (self.w1 + self.w2))


# --- Beam Structure ---

class Point:
    def __init__(self, x: float):
        self.x = x
        self.events: list[PointEvent] = []

    def add_event(self, event: PointEvent) -> None:
        self.events.append(event)


class Beam:
    def __init__(self, length: float):
        self.length = length
        self.points: list[Point] = []
        self.distributed_events: list[DistributedEvent] = []

    def get_or_create_point(self, x: float) -> Point:
        for p in self.points:
            if abs(p.x - x) < TOLERANCE:
                return p
        new_p = Point(x)
        self.points.append(new_p)
        self.points.sort(key=lambda item: item.x)
        return new_p

    def add_event(self, x: float, event: PointEvent) -> None:
        point = self.get_or_create_point(x)
        point.add_event(event)

    def add_distributed_event(self, event: DistributedEvent) -> None:
        self.get_or_create_point(event.start_x)
        self.get_or_create_point(event.end_x)
        self.distributed_events.append(event)

    def clear_reactions(self) -> None:
        for p in self.points:
            p.events = [ev for ev in p.events if not isinstance(ev, (Reaction, ReactionMoment))]

    # --- Query Helpers ---

    def point_loads(self) -> Generator[tuple[float, PointLoad], None, None]:
        for p in self.points:
            for ev in p.events:
                if isinstance(ev, PointLoad):
                    yield p.x, ev

    def applied_moments(self) -> Generator[tuple[float, AppliedMoment], None, None]:
        for p in self.points:
            for ev in p.events:
                if isinstance(ev, AppliedMoment):
                    yield p.x, ev

    def supports(self) -> Generator[tuple[float, Support], None, None]:
        for p in self.points:
            for ev in p.events:
                if isinstance(ev, Support):
                    yield p.x, ev

    def udls(self) -> Generator[UniformDistributedLoad, None, None]:
        for dev in self.distributed_events:
            if isinstance(dev, UniformDistributedLoad):
                yield dev

    def uvls(self) -> Generator[UniformVaryingLoad, None, None]:
        for dev in self.distributed_events:
            if isinstance(dev, UniformVaryingLoad):
                yield dev

    def equivalent_loads(self) -> Generator[tuple[float, float], None, None]:
        """
        Yields (x_location, force) for EVERY applied load on the beam.
        This isolates the solver from caring about load shapes.
        """
        for x, load in self.point_loads():
            yield x, load.force
        for udl in self.udls():
            yield udl.centroid_x, udl.resultant_force
        for uvl in self.uvls():
            yield uvl.centroid_x, uvl.resultant_force