import numpy as np
import matplotlib.patches as patches
from beam import Beam, Support, ReactionMoment, UniformDistributedLoad, UniformVaryingLoad, PointLoad, AppliedMoment, FIXED, PINNED, \
    ROLLER


def plot_beam_results(beam: Beam, x_vals: np.ndarray, V_vals: np.ndarray, M_vals: np.ndarray, fig,
                      reactions_dict: dict):
    """
    Renders the Beam Diagram, Shear Force Diagram (SFD), and Bending Moment Diagram (BMD).
    Renders onto the provided Matplotlib Figure (fig).
    """
    fig.clear()

    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)

    L = beam.length

    # ---------------------------------------------------------
    # 1. BEAM DIAGRAM
    # ---------------------------------------------------------
    ax1.plot([0, L], [0, 0], color='black', linewidth=4)
    ax1.set_xlim(-0.1 * L, L * 1.1)
    ax1.set_ylim(-2, 2)
    ax1.axis('off')

    # Build Header Text based on beam type
    if reactions_dict["type"] == "cantilever":
        rxn_text = (f"Cantilever Fixed Support at x = {reactions_dict['x_A']} m\n"
                    f"Reaction R = {reactions_dict['R_A']:.2f} kN, M = {reactions_dict['M_A']:.2f} kNm")
    else:
        rxn_text = (f"Simply Supported\n"
                    f"R_A (x={reactions_dict['x_A']}m) = {reactions_dict['R_A']:.2f} kN, "
                    f"R_B (x={reactions_dict['x_B']}m) = {reactions_dict['R_B']:.2f} kN")
    ax1.set_title(f"Beam Diagram\n{rxn_text}")

    # Draw Supports
    for p in beam.points:
        for ev in p.events:
            if isinstance(ev, Support):
                if ev.support_type == FIXED:
                    # Draw a gray wall. If it's on the left, wall goes left. If right, wall goes right.
                    width = 0.03 * L if L > 0 else 0.1
                    x_start = p.x - width if p.x < L / 2 else p.x
                    rect = patches.Rectangle((x_start, -1), width, 2, facecolor='gray', hatch='//', edgecolor='black')
                    ax1.add_patch(rect)
                elif ev.support_type == PINNED:
                    # Draw a blue triangle
                    triangle = patches.Polygon([[p.x, 0], [p.x - 0.05 * L, -0.5], [p.x + 0.05 * L, -0.5]], color='blue')
                    ax1.add_patch(triangle)
                elif ev.support_type == ROLLER:
                    # Draw a green circle
                    circle = patches.Circle((p.x, -0.25), 0.25, color='green')
                    ax1.add_patch(circle)

    # Draw Point Loads
    for x, load in beam.point_loads():
        sign = 1 if load.force > 0 else -1
        y_start = 1 * sign
        ax1.annotate("", xy=(x, 0), xytext=(x, y_start),
                     arrowprops=dict(facecolor='red', shrink=0.05, width=2, headwidth=8))
        ax1.text(x, y_start * 1.2, f"{abs(load.force):.1f} kN", color='red', ha='center', va='center')

    # Draw Applied Moments
    for x, moment in beam.applied_moments():
        arc = patches.Arc((x, 0), L * 0.1, 1, angle=0, theta1=0, theta2=180, color='purple', linewidth=2)
        ax1.add_patch(arc)
        ax1.text(x, 0.6, f"{moment.moment:.1f} kNm", color='purple', ha='center', va='bottom')

    # Draw Reaction Moments (The Fixed Support Moment)
    for p in beam.points:
        for ev in p.events:
            if isinstance(ev, ReactionMoment):
                # Draw a red dashed arc to distinguish it from applied moments
                arc = patches.Arc((p.x, 0), L * 0.15, 1.5, angle=0, theta1=0, theta2=180,
                                  color='red', linewidth=2, linestyle='--')
                ax1.add_patch(arc)
                ax1.text(p.x, 0.9, f"M_R = {ev.moment:.1f} kNm",
                         color='red', ha='center', va='bottom')

    # Draw Distributed Loads
    for udl in beam.udls():
        ax1.add_patch(patches.Rectangle((udl.start_x, 0), udl.span, 0.5, color='orange', alpha=0.3))
        ax1.text(udl.centroid_x, 0.6, f"{udl.intensity:.1f} kN/m", color='darkorange', ha='center')

    for uvl in beam.uvls():
        poly = patches.Polygon([
            (uvl.start_x, 0),
            (uvl.start_x, 0.5 * (uvl.w1 / max(abs(uvl.w1), abs(uvl.w2), 1e-5))),
            (uvl.end_x, 0.5 * (uvl.w2 / max(abs(uvl.w1), abs(uvl.w2), 1e-5))),
            (uvl.end_x, 0)
        ], color='cyan', alpha=0.3)
        ax1.add_patch(poly)
        ax1.text(uvl.centroid_x, 0.6, f"UVL", color='teal', ha='center')

    # ---------------------------------------------------------
    # 2. SHEAR FORCE DIAGRAM (SFD)
    # ---------------------------------------------------------
    ax2.plot(x_vals, V_vals, color='blue', linewidth=2)
    ax2.fill_between(x_vals, V_vals, 0, color='blue', alpha=0.1)
    ax2.axhline(0, color='black', linewidth=1)
    ax2.set_xlim(0, L)
    ax2.set_ylabel("Shear Force (kN)")
    ax2.set_title("Shear Force Diagram")
    ax2.grid(True, linestyle='--', alpha=0.6)

    # ---------------------------------------------------------
    # 3. BENDING MOMENT DIAGRAM (BMD)
    # ---------------------------------------------------------
    ax3.plot(x_vals, M_vals, color='green', linewidth=2)
    ax3.fill_between(x_vals, M_vals, 0, color='green', alpha=0.1)
    ax3.axhline(0, color='black', linewidth=1)
    ax3.set_xlim(0, L)
    ax3.set_xlabel("Beam Length (m)")
    ax3.set_ylabel("Bending Moment (kNm)")
    ax3.set_title("Bending Moment Diagram")
    ax3.grid(True, linestyle='--', alpha=0.6)

    fig.tight_layout()