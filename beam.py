TOLERANCE = 1e-6

# *********     SUPPORT TYPE CONSTANTS     **********
PINNED = "pinned"
ROLLER = "roller"
FIXED = "fixed"


# *********     EVENTS     **********

class Event:
    """Base class for any physical event at a location."""
    pass


class PointLoad(Event):
    """Represents a concentrated vertical load acting at a point."""

    def __init__(self, force: float):
        self.force = force


class AppliedMoment(Event):
    """Represents a concentrated moment acting at a point."""

    def __init__(self, moment: float):
        self.moment = moment


class Reaction(Event):
    """Represents a reaction force calculated at a support."""

    def __init__(self, force: float):
        self.force = force


class Support(Event):
    """Represents a physical support boundary condition."""

    def __init__(self, support_type: str):
        self.support_type = support_type


# *********     POINTS     **********

class Point:
    """Represents a specific x-coordinate along the beam where events occur."""

    def __init__(self, x: float):
        self.x = x
        self.events: list[Event] = []

    def add_event(self, event: Event) -> None:
        """Attaches an Event object to this point."""
        self.events.append(event)


# *********     BEAM     **********

class Beam:
    """
    Main Beam class representing span geometry and managing attached points and events.
    """

    def __init__(self, length: float):
        self.length = length
        self.points: list[Point] = []

    def get_or_create_point(self, x: float) -> Point:
        """Finds an existing Point at coordinate x, or creates and attaches a new one."""
        for p in self.points:
            if abs(p.x - x) < TOLERANCE:
                return p

        new_p = Point(x)
        self.points.append(new_p)
        self.points.sort(key=lambda item: item.x)
        return new_p

    def add_event(self, x: float, event: Event) -> None:
        """
        High-level wrapper to attach an Event at coordinate x.
        Encapsulates Point retrieval and creation within Beam.
        """
        point = self.get_or_create_point(x)
        point.add_event(event)