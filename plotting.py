import matplotlib.patches as patches
import numpy as np
from beam import (Beam, Support, FIXED, PINNED, ROLLER)

min_arrow_length = 0.45
max_arrow_length = 1.0

def draw_fixed_support(ax, x, L):
    wall_width = 0.035 * L
    wall_height = 1.8

    wall = patches.Rectangle(
        (x - wall_width, -0.9), wall_width, wall_height, facecolor="#AEB6BE", edgecolor="#7F8992", linewidth=1.2)
    ax.add_patch(wall)

    hatch_spacing = 0.12 * L
    for i in range(6):
        y = -0.75 + i * 0.3
        ax.plot([x - wall_width, x - wall_width - hatch_spacing], [y, y - 0.25], color="#7F8992", linewidth=1)

def draw_pinned_support(ax, x, L):
    triangle_width = 0.06 * L
    triangle_height = 0.55

    triangle = patches.Polygon([(x, 0), (x - triangle_width, -triangle_height), (x + triangle_width, -triangle_height)],
        closed=True, facecolor="#AEB6BE", edgecolor="#7F8992", linewidth=1.2)
    ax.add_patch(triangle)

    ax.plot([x - triangle_width * 1.25, x + triangle_width * 1.25], [-triangle_height, -triangle_height], color="#7F8992", linewidth=2)

    hatch_spacing = triangle_width * 0.45
    for i in range(-2, 3):
        hatch_x = x + i * hatch_spacing
        ax.plot([hatch_x, hatch_x - hatch_spacing * 0.45], [-triangle_height, -triangle_height - 0.18],
            color="#7F8992", linewidth=1)

def draw_roller_support(ax, x, L):
    triangle_width = 0.06 * L
    triangle_height = 0.5
    roller_radius = 0.11

    triangle = patches.Polygon([(x, 0), (x - triangle_width, -triangle_height), (x + triangle_width, -triangle_height)],
        closed=True, facecolor="#AEB6BE", edgecolor="#7F8992", linewidth=1.2)
    ax.add_patch(triangle)

    roller_y = -triangle_height - roller_radius

    for dx in (-triangle_width * 0.45, triangle_width * 0.45):
        roller = patches.Circle((x + dx, roller_y), roller_radius, facecolor="#D5D9DD", edgecolor="#7F8992", linewidth=1.2)
        ax.add_patch(roller)

    ground_y = roller_y - roller_radius

    ax.plot([x - triangle_width * 1.4, x + triangle_width * 1.4], [ground_y, ground_y], color="#7F8992", linewidth=2)

    hatch_spacing = triangle_width * 0.5
    for i in range(-2, 3):
        hatch_x = x + i * hatch_spacing
        ax.plot([hatch_x, hatch_x - hatch_spacing * 0.4], [ground_y, ground_y - 0.16], color="#7F8992", linewidth=1)


def draw_point_moment(ax, x, moment, L):
    radius = 0.32
    arrow_colour = "#C7A6E6"

    if moment.moment > 0:
        connection_style = "arc3,rad=0.8"
        start = (x + radius, 0)
        end = (x - radius, 0)
    else:
        connection_style = "arc3,rad=-0.8"
        start = (x - radius, 0)
        end = (x + radius, 0)

    arrow = patches.FancyArrowPatch(start, end, connectionstyle=connection_style, arrowstyle="->", mutation_scale=16, linewidth=2.5, color=arrow_colour)
    ax.add_patch(arrow)

    ax.text(x, radius + 0.12, f"{abs(moment.moment):.1f} kNm", color=arrow_colour, ha="center", va="bottom")


def draw_reaction_moment(ax, x, moment, L):
    reaction_moment_color = "#B8A1D9"
    radius = 0.32

    if moment > 0:
        connection_style = "arc3,rad=0.8"
        start = (x + radius, 0)
        end = (x - radius, 0)
    else:
        connection_style = "arc3,rad=-0.8"
        start = (x - radius, 0)
        end = (x + radius, 0)

    arrow = patches.FancyArrowPatch(start, end,connectionstyle=connection_style, arrowstyle="->", mutation_scale=16, linewidth=2.5, color=reaction_moment_color)
    ax.add_patch(arrow)

    ax.text(x, radius + 0.12, f"M_R = {abs(moment):.1f} kNm", color=reaction_moment_color, ha="center", va="bottom")

def draw_reaction(ax, x, force, max_reaction, L, label="R"):
    reaction_color = "#9FD3C7"

    if max_reaction > 0:
        magnitude_ratio = abs(force) / max_reaction
    else:
        magnitude_ratio = 0

    arrow_length = (min_arrow_length + magnitude_ratio * (max_arrow_length - min_arrow_length))

    sign = 1 if force > 0 else -1
    y_start = arrow_length * sign

    ax.annotate("", xy=(x, 0), xytext=(x, y_start), arrowprops=dict(facecolor=reaction_color, edgecolor=reaction_color, shrink=0.05, width=2, headwidth=8))

    label_offset = 0.18

    ax.text(x, (arrow_length + label_offset) * sign, f"{label} = {abs(force):.1f} kN", color=reaction_color, ha="center", va="center")


def plot_beam_results(
    beam: Beam,
    x_vals: np.ndarray,
    V_vals: np.ndarray,
    M_vals: np.ndarray,
    fig,
    reactions_dict: dict
):
    fig.clear()

    TEXT_COLOR = "#E6E9EC"

    fig.patch.set_facecolor("#2F3942")

    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)

    for ax in (ax1, ax2, ax3):
        ax.set_facecolor("#3B4650")
        ax.tick_params(colors=TEXT_COLOR)
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        ax.title.set_color(TEXT_COLOR)

    L = beam.length

    # ------------------------------------------------------------------
    # Beam diagram
    # ------------------------------------------------------------------

    ax1.plot([0, L], [0, 0], color="#D5D9DD", linewidth=4, solid_capstyle="butt")

    ax1.set_xlim(-0.1 * L, L * 1.1)
    ax1.set_ylim(-2, 2)
    ax1.axis("off")

    if reactions_dict["type"] == "cantilever":
        rxn_text = (f'''Cantilever Fixed Support at x = {reactions_dict['x_A']} m\n
            Reaction R = {reactions_dict['R_A']:.2f} kN, 
            M = {reactions_dict['M_A']:.2f} kNm''')
    else:
        rxn_text = ("Simply Supported\n"
            f"R_A (x={reactions_dict['x_A']}m) = "
            f"{reactions_dict['R_A']:.2f} kN, "
            f"R_B (x={reactions_dict['x_B']}m) = "
            f"{reactions_dict['R_B']:.2f} kN")

    ax1.text(0.5, 1.08, "Beam Diagram\n", transform=ax1.transAxes, ha="center", va="bottom", fontsize=16, fontweight="bold", color=TEXT_COLOR)
    ax1.text(0.5, 1.05, rxn_text, transform=ax1.transAxes, ha="center", va="bottom", fontsize=11, fontweight="bold", color=TEXT_COLOR)

    # Supports
    for p in beam.points:
        for ev in p.events:
            if isinstance(ev, Support):
                if ev.support_type == FIXED:
                    draw_fixed_support(ax1, p.x, L)
                elif ev.support_type == PINNED:
                    draw_pinned_support(ax1, p.x, L)
                elif ev.support_type == ROLLER:
                    draw_roller_support(ax1, p.x, L)

    # Point loads
    point_loads = list(beam.point_loads())

    if point_loads:
        max_load = max(abs(load.force) for _, load in point_loads)

        for x, load in point_loads:
            sign = 1 if load.force > 0 else -1

            if max_load > 0:
                magnitude_ratio = abs(load.force) / max_load
            else:
                magnitude_ratio = 0

            arrow_length = (min_arrow_length + magnitude_ratio * (max_arrow_length - min_arrow_length))
            y_start = arrow_length * sign

            ax1.annotate("", xy=(x, 0), xytext=(x, y_start), arrowprops=dict(facecolor="#F0D58A", edgecolor="#F0D58A", shrink=0.05, width=2,headwidth=8))
            label_offset = 0.18
            ax1.text(x,(arrow_length + label_offset) * sign, f"{abs(load.force):.1f} kN", color="#F0D58A", ha="center", va="center")

    # Applied moments
    for x, moment in beam.applied_moments():
        draw_point_moment(ax1, x, moment, L)

    # Reaction forces and moments
    if reactions_dict["type"] == "cantilever":
        reaction_force = reactions_dict["R_A"]
        reaction_moment = reactions_dict["M_A"]

        max_reaction = abs(reaction_force)
        draw_reaction(ax1, reactions_dict["x_A"], reaction_force, max_reaction, L, label="R")
        draw_reaction_moment(ax1, reactions_dict["x_A"], reaction_moment, L)

    else:
        reaction_A = reactions_dict["R_A"]
        reaction_B = reactions_dict["R_B"]

        max_reaction = max(abs(reaction_A), abs(reaction_B))
        draw_reaction(ax1, reactions_dict["x_A"], reaction_A, max_reaction, L, label="R_A")
        draw_reaction(ax1, reactions_dict["x_B"], reaction_B, max_reaction, L, label="R_B")

    # UDL
    for udl in beam.udls():
        ax1.add_patch(patches.Rectangle((udl.start_x, 0), udl.span, 0.5, color="#E6B566", alpha=0.3))
        ax1.text(udl.centroid_x, 0.6, f"{udl.intensity:.1f} kN/m", color="#E6B566", ha="center")

    # UVL
    for uvl in beam.uvls():
        max_intensity = max(abs(uvl.w1), abs(uvl.w2), 1e-5)

        poly = patches.Polygon([(uvl.start_x, 0),
                (uvl.start_x, 0.5 * (uvl.w1 / max_intensity)),
                (uvl.end_x, 0.5 * (uvl.w2 / max_intensity)),
                (uvl.end_x, 0)], color="#63C7C7", alpha=0.3)

        ax1.add_patch(poly)

        ax1.text(uvl.centroid_x, 0.6, "UVL", color="#63C7C7", ha="center")

    # ------------------------------------------------------------------
    # Shear Force Diagram
    # ------------------------------------------------------------------

    ax2.plot(x_vals, V_vals, color="#E05A5A", linewidth=2)

    ax2.fill_between(x_vals, V_vals, 0, color="#E05A5A", alpha=0.1)

    ax2.axhline(0, color="black", linewidth=1)

    ax2.set_xlim(0, L)
    ax2.set_ylabel("Shear Force (kN)")
    ax2.set_title("Shear Force Diagram")

    ax2.grid(True, linestyle="--", alpha=0.6)

    # ------------------------------------------------------------------
    # Bending Moment Diagram
    # ------------------------------------------------------------------

    ax3.plot(x_vals, M_vals, color="#4DA3D9", linewidth=2)

    ax3.fill_between(x_vals, M_vals, 0, color="#4DA3D9", alpha=0.1)

    ax3.axhline(0, color="black", linewidth=1)

    ax3.set_xlim(0, L)
    ax3.set_xlabel("Beam Length (m)")
    ax3.set_ylabel("Bending Moment (kNm)")
    ax3.set_title("Bending Moment Diagram")

    ax3.grid(True, linestyle="--", alpha=0.6)
    fig.tight_layout()
