import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from beam import Beam, Reaction, Support, PointLoad, AppliedMoment, PINNED, ROLLER


def plot_beam_results(beam: Beam, x_grid: np.ndarray, V_grid: np.ndarray, M_grid: np.ndarray) -> None:
    """Renders 3-panel figure: Beam Loading Schematic, SFD, and BMD with clean, non-overlapping labels."""
    fig, (ax_beam, ax_sfd, ax_bmd) = plt.subplots(3, 1, figsize=(16, 9), sharex=True)
    fig.suptitle("Simply Supported Beam Analysis", fontsize=14, fontweight="bold")

    # ==========================================
    # 1. TOP PANEL: BEAM SCHEMATIC & LOADS
    # ==========================================
    ax_beam.set_title("Beam Loading Schematic")
    ax_beam.plot([0, beam.length], [0, 0], color="black", linewidth=5, zorder=3)  # Beam line

    # Expand vertical clearance so stacked labels don't collide
    ax_beam.set_ylim(-2.8, 2.8)
    ax_beam.set_yticks([])
    ax_beam.grid(True, linestyle="--", alpha=0.4)

    # --- A. Draw UDLs ---
    for udl in beam.udls():
        is_downward = udl.intensity < 0
        box_bottom = 0.08 if is_downward else -0.48
        box_height = 0.40

        # Shaded UDL range
        rect = patches.Rectangle(
            (udl.start_x, box_bottom),
            udl.span,
            box_height,
            color="orange",
            alpha=0.25,
            zorder=1,
        )
        ax_beam.add_patch(rect)

        # Distributed arrows along UDL span
        num_arrows = max(3, int(udl.span * 2.5))
        arrow_x_coords = np.linspace(udl.start_x, udl.end_x, num=num_arrows)

        for ax_pos in arrow_x_coords:
            if is_downward:
                ax_beam.annotate(
                    "",
                    xy=(ax_pos, 0.08),
                    xytext=(ax_pos, 0.48),
                    arrowprops=dict(arrowstyle="->", color="darkorange", lw=1.2),
                    zorder=2,
                )
            else:
                ax_beam.annotate(
                    "",
                    xy=(ax_pos, -0.08),
                    xytext=(ax_pos, -0.48),
                    arrowprops=dict(arrowstyle="->", color="darkorange", lw=1.2),
                    zorder=2,
                )

        # UDL Label placed at y = 0.65 or -0.65
        label_y = 0.65 if is_downward else -0.65
        ax_beam.text(
            udl.centroid_x,
            label_y,
            f"w = {abs(udl.intensity)} kN/m",
            ha="center",
            va="center",
            color="darkorange",
            fontweight="bold",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="orange", alpha=0.85),
        )

    # --- B. Draw Point Events per Coordinate (Prevents Collisions) ---
    for point in beam.points:
        x = point.x

        # Separate events occurring at x
        p_loads = [ev for ev in point.events if isinstance(ev, PointLoad)]
        app_moments = [ev for ev in point.events if isinstance(ev, AppliedMoment)]
        reactions = [ev for ev in point.events if isinstance(ev, Reaction)]
        supports = [ev for ev in point.events if isinstance(ev, Support)]

        # 1. Supports (drawn right on beam centerline)
        for sup in supports:
            marker = "^" if sup.support_type == PINNED else "o"
            ax_beam.plot(x, -0.08, marker=marker, markersize=12, color="black", zorder=4)

        # 2. Downward / Upward Point Loads (Tier 2: y = +/- 1.45)
        for load in p_loads:
            if load.force < 0:
                ax_beam.annotate(
                    f"P = {abs(load.force)} kN",
                    xy=(x, 0.12),
                    xytext=(x, 1.45),
                    arrowprops=dict(arrowstyle="->", color="red", lw=2.2),
                    ha="center",
                    va="bottom",
                    color="red",
                    fontweight="bold",
                    fontsize=9.5,
                    bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="red", alpha=0.85),
                )
            else:
                ax_beam.annotate(
                    f"P = {abs(load.force)} kN",
                    xy=(x, -0.12),
                    xytext=(x, -1.45),
                    arrowprops=dict(arrowstyle="->", color="red", lw=2.2),
                    ha="center",
                    va="top",
                    color="red",
                    fontweight="bold",
                    fontsize=9.5,
                    bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="red", alpha=0.85),
                )

        # 3. Reactions (Tier 3: y = +/- 1.85, offset from supports)
        for rxn in reactions:
            direction = 1 if rxn.force >= 0 else -1
            if direction == 1:
                ax_beam.annotate(
                    f"R = {rxn.force:.1f} kN",
                    xy=(x, -0.20),
                    xytext=(x, -1.85),
                    arrowprops=dict(arrowstyle="->", color="blue", lw=2.2),
                    ha="center",
                    va="top",
                    color="blue",
                    fontweight="bold",
                    fontsize=9.5,
                    bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="blue", alpha=0.85),
                )
            else:
                ax_beam.annotate(
                    f"R = {rxn.force:.1f} kN",
                    xy=(x, 0.20),
                    xytext=(x, 1.85),
                    arrowprops=dict(arrowstyle="->", color="blue", lw=2.2),
                    ha="center",
                    va="bottom",
                    color="blue",
                    fontweight="bold",
                    fontsize=9.5,
                    bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="blue", alpha=0.85),
                )

        # 4. Applied Moments (Tier 4: high top position at y = 2.25)
        for mom in app_moments:
            symbol = "↺" if mom.moment > 0 else "↻"
            ax_beam.text(
                x,
                2.25,
                f"M = {abs(mom.moment)} kNm {symbol}",
                ha="center",
                va="center",
                color="purple",
                fontweight="bold",
                fontsize=9.5,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="purple", alpha=0.85),
            )
            # Dotted guide line connecting moment tag to beam coordinate
            ax_beam.plot([x, x], [0.1, 1.95], color="purple", linestyle=":", linewidth=1.2)

    # ==========================================
    # 2. MIDDLE PANEL: SHEAR FORCE DIAGRAM (SFD)
    # ==========================================
    ax_sfd.set_title("Shear Force Diagram (SFD)")
    ax_sfd.plot(x_grid, V_grid, color="crimson", linewidth=2)
    ax_sfd.fill_between(x_grid, V_grid, 0, color="crimson", alpha=0.15)
    ax_sfd.axhline(0, color="black", linewidth=0.8)
    ax_sfd.set_ylabel("Shear Force (kN)")
    ax_sfd.grid(True, linestyle="--", alpha=0.6)

    # ==========================================
    # 3. BOTTOM PANEL: BENDING MOMENT DIAGRAM (BMD)
    # ==========================================
    ax_bmd.set_title("Bending Moment Diagram (BMD)")
    ax_bmd.plot(x_grid, M_grid, color="navy", linewidth=2)
    ax_bmd.fill_between(x_grid, M_grid, 0, color="navy", alpha=0.15)
    ax_bmd.axhline(0, color="black", linewidth=0.8)
    ax_bmd.set_xlabel("Beam Position x (m)")
    ax_bmd.set_ylabel("Moment (kNm)")
    ax_bmd.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    plt.show()