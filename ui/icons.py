"""
A small, self-contained icon set for the application toolbar and buttons.

Rather than pulling in an external icon-font dependency (qtawesome, etc.)
for a handful of glyphs, icons are defined as plain SVG path data and
rasterized on demand with Qt's own QtSvg module (already part of the
PyQt5 distribution -- no new dependency). This keeps the icon language
coherent, monochrome and easy to recolor per design-system state
(default / hover / accent) without shipping image assets.
"""

from PyQt5.QtCore import QByteArray, Qt
from PyQt5.QtGui import QIcon, QPainter, QPixmap
from PyQt5.QtSvg import QSvgRenderer

_STROKE = 'stroke="{color}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" fill="none"'

_SVG_BODY = {
    # sheet / new document
    "new": '<path {s} d="M6 3h8l4 4v14H6z"/><path {s} d="M14 3v4h4"/><path {s} d="M9 13h6M9 16.5h6"/>',
    # play triangle
    "run": '<path stroke="{color}" stroke-width="1.4" stroke-linejoin="round" fill="{color}" d="M8 5.5v13l11-6.5z"/>',
    # clock
    "history": '<circle {s} cx="12" cy="12.5" r="8"/><path {s} d="M12 8v5l3.5 2"/><path {s} d="M9 2.5h6"/>',
    # export / download to tray
    "export": '<path {s} d="M12 3v12"/><path {s} d="M7.5 10.5 12 15l4.5-4.5"/><path {s} d="M4.5 17.5v3h15v-3"/>',
    # help / question mark
    "help": '<circle {s} cx="12" cy="12" r="8.5"/>'
            '<path {s} d="M9.6 9.6c.3-1.4 1.5-2.2 2.8-2 1.2.2 2.1 1.1 2 2.3-.1 1.4-2.2 1.7-2.4 3.4"/>'
            '<circle cx="12" cy="17" r="0.9" fill="{color}" stroke="none"/>',
    # plus (add row)
    "add": '<path {s} d="M12 6v12M6 12h12"/>',
    # close / remove
    "remove": '<path {s} d="M6.5 6.5l11 11M17.5 6.5l-11 11"/>',
    # beam / structural element
    "beam": '<path {s} d="M3 17h18"/><path {s} d="M3 17V9h18v8"/><path {s} d="M7 9V6h10v3"/>',
    # pinned support (triangle)
    "support": '<path stroke="{color}" stroke-width="1.4" stroke-linejoin="round" fill="{color}" '
               'd="M12 4 20 18H4z"/>',
    # point load (down arrow)
    "load": '<path {s} d="M12 4v13"/><path stroke="{color}" stroke-width="1.4" stroke-linejoin="round" '
            'fill="{color}" d="M7.5 15 12 20l4.5-5z"/>',
    # zoom / fit-view (magnifier)
    "zoom": '<circle {s} cx="10.5" cy="10.5" r="6.5"/><path {s} d="M15.3 15.3 20 20"/>',
    # settings / gear
    "settings": '<circle {s} cx="12" cy="12" r="3"/>'
                '<path {s} d="M12 3.5v2.4M12 18.1v2.4M4.6 12H2M22 12h-2.6'
                'M6 6l1.7 1.7M16.3 16.3 18 18M18 6l-1.7 1.7M7.7 16.3 6 18"/>',
    # chevron down (expand)
    "chevron_down": '<path {s} d="M6 9.5 12 15l6-5.5"/>',
    # info
    "info": '<circle {s} cx="12" cy="12" r="8.5"/><path {s} d="M12 11v5.5"/>'
            '<circle cx="12" cy="8" r="0.9" fill="{color}" stroke="none"/>',
}


def _svg_source(name: str, color: str) -> str:
    body = _SVG_BODY[name].format(s=_STROKE.format(color=color), color=color)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">{body}</svg>'


def pixmap(name: str, color: str = "#98A4AE", size: int = 18) -> QPixmap:
    """Rasterize a named icon at the given size/color."""
    svg = _svg_source(name, color)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing, True)
    renderer.render(painter)
    painter.end()
    return pm


def icon(name: str, color: str = "#98A4AE", size: int = 18) -> QIcon:
    """Build a QIcon for the named glyph. See _SVG_BODY for available names."""
    return QIcon(pixmap(name, color, size))
