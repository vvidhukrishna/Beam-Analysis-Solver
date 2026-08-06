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
    """Vertical force (kN). Downward is negative."""
    def __init__(self, force: float):
        self.force = force


class AppliedMoment(PointEvent):
    """Applied moment (kNm). Counter-clockwise is positive."""
    def __init__(self, moment: float):
        self.moment = moment


class Reaction(PointEvent):
    """Calculated support reaction force (kN)."""
    def __init__(self, force: float):
        self.force = force


class Support(PointEvent):
    """Physical support boundary condition."""
    def __init__(self, support_type: str):
        self.support_type = support_type


# --- Distributed Events ---

class UniformDistributedLoad(DistributedEvent):
    """Uniform Distributed Load (kN/m). Downward intensity is negative."""

    def __init__(self, start_x: float, end_x: float, intensity: float):
        super().__init__(start_x, end_x)
        self.intensity = intensity

    @property
    def resultant_force(self) -> float:
        """Total equivalent point force (w * L)."""
        return self.intensity * self.span

    @property
    def centroid_x(self) -> float:
        """Midpoint of the load distribution."""
        return self.start_x + (self.span / 2.0)


# --- Beam Structure ---

class Point:
    """Stores all PointEvents occurring at coordinate x."""

    def __init__(self, x: float):
        self.x = x
        self.events: list[PointEvent] = []

    def add_event(self, event: PointEvent) -> None:
        self.events.append(event)


class Beam:
    """Represents the complete beam model."""

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

    # Helpers for iterating events
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

    def clear_reactions(self) -> None:
        """Removes all Reaction events from every point on the beam."""
        for p in self.points:
            p.events = [ev for ev in p.events if not isinstance(ev, Reaction)]