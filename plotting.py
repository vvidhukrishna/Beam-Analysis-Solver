import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from beam import Beam, Reaction, Support, PointLoad, AppliedMoment, PINNED


def plot_beam_results(beam: Beam, x_grid: np.ndarray, V_grid: np.ndarray, M_grid: np.ndarray) -> None:
    fig, (ax_beam, ax_sfd, ax_bmd) = plt.subplots(3, 1, figsize=(16, 9), sharex=True)
    fig.suptitle("Simply Supported Beam Analysis", fontsize=14, fontweight="bold")

    # ==========================================
    # 1. TOP PANEL: BEAM SCHEMATIC & LOADS
    # ==========================================
    ax_beam.set_title("Beam Loading Schematic")
    ax_beam.plot([0, beam.length], [0, 0], color="black", linewidth=5, zorder=3)
    ax_beam.set_ylim(-2.8, 2.8)
    ax_beam.set_yticks([])
    ax_beam.grid(True, linestyle="--", alpha=0.4)
    # --- Draw UDLs (Tier 1: Inner Load) ---
    for udl in beam.udls():
        is_downward = udl.intensity < 0
        # Tier 1 sits close to the beam (0.08 to 0.48)
        box_bottom = 0.08 if is_downward else -0.48

        rect = patches.Rectangle((udl.start_x, box_bottom), udl.span, 0.40, color="orange", alpha=0.3, zorder=1)
        ax_beam.add_patch(rect)

        arrow_x_coords = np.linspace(udl.start_x, udl.end_x, num=max(3, int(udl.span * 2.5)))
        for ax_pos in arrow_x_coords:
            if is_downward:
                ax_beam.annotate("", xy=(ax_pos, 0.08), xytext=(ax_pos, 0.48),
                                 arrowprops=dict(arrowstyle="->", color="darkorange", lw=1.2), zorder=2)
            else:
                ax_beam.annotate("", xy=(ax_pos, -0.08), xytext=(ax_pos, -0.48),
                                 arrowprops=dict(arrowstyle="->", color="darkorange", lw=1.2), zorder=2)

        # Label placed just above Tier 1
        label_y = 0.65 if is_downward else -0.65
        ax_beam.text(udl.centroid_x, label_y, f"w = {abs(udl.intensity)} kN/m", ha="center", va="center",
                     color="darkorange", fontweight="bold", fontsize=9,
                     bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="orange", alpha=0.85), zorder=5)

    # --- Draw UVLs (Tier 2: Stacked outside UDLs) ---
    for uvl in beam.uvls():
        is_downward = (uvl.w1 + uvl.w2) <= 0
        direction = 1 if is_downward else -1

        # Tier 2 starts at 0.55 (just above the UDL maximum height of 0.48)
        base_y = 0.55 if is_downward else -0.55

        max_w = max(abs(uvl.w1), abs(uvl.w2))
        if max_w == 0: continue

        h1 = (abs(uvl.w1) / max_w) * 0.40
        h2 = (abs(uvl.w2) / max_w) * 0.40

        pts = [
            (uvl.start_x, base_y),
            (uvl.end_x, base_y),
            (uvl.end_x, base_y + h2 * direction),
            (uvl.start_x, base_y + h1 * direction)
        ]

        # Using coral/orangered to distinguish from the standard UDL orange
        poly = patches.Polygon(pts, color="coral", alpha=0.3, zorder=1)
        ax_beam.add_patch(poly)

        arrow_x_coords = np.linspace(uvl.start_x, uvl.end_x, num=max(3, int(uvl.span * 2.5)))
        for ax_pos in arrow_x_coords:
            frac = (ax_pos - uvl.start_x) / uvl.span
            h_x = h1 + frac * (h2 - h1)
            if h_x > 0.02:
                # Arrows point towards base_y
                if is_downward:
                    ax_beam.annotate("", xy=(ax_pos, base_y), xytext=(ax_pos, base_y + h_x),
                                     arrowprops=dict(arrowstyle="->", color="orangered", lw=1.2), zorder=2)
                else:
                    ax_beam.annotate("", xy=(ax_pos, base_y), xytext=(ax_pos, base_y - h_x),
                                     arrowprops=dict(arrowstyle="->", color="orangered", lw=1.2), zorder=2)

        # Label placed just above Tier 2
        label_y = 1.15 if is_downward else -1.15
        ax_beam.text(uvl.centroid_x, label_y, f"w1={abs(uvl.w1)}, w2={abs(uvl.w2)}", ha="center", va="center",
                     color="orangered", fontweight="bold", fontsize=9,
                     bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="coral", alpha=0.85), zorder=5)

    # --- Draw Point Loads, Supports, Reactions & Moments ---
    for point in beam.points:
        x = point.x
        p_loads = [ev for ev in point.events if isinstance(ev, PointLoad)]
        app_moments = [ev for ev in point.events if isinstance(ev, AppliedMoment)]
        reactions = [ev for ev in point.events if isinstance(ev, Reaction)]
        supports = [ev for ev in point.events if isinstance(ev, Support)]

        for sup in supports:
            marker = "^" if sup.support_type == PINNED else "o"
            ax_beam.plot(x, -0.08, marker=marker, markersize=12, color="black", zorder=4)

        for load in p_loads:
            if load.force < 0:
                ax_beam.annotate(f"P = {abs(load.force)} kN", xy=(x, 0.12), xytext=(x, 1.45),
                                 arrowprops=dict(arrowstyle="->", color="red", lw=2.2), ha="center", va="bottom",
                                 color="red", fontweight="bold", fontsize=9.5,
                                 bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="red", alpha=0.85))
            else:
                ax_beam.annotate(f"P = {abs(load.force)} kN", xy=(x, -0.12), xytext=(x, -1.45),
                                 arrowprops=dict(arrowstyle="->", color="red", lw=2.2), ha="center", va="top",
                                 color="red", fontweight="bold", fontsize=9.5,
                                 bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="red", alpha=0.85))

        for rxn in reactions:
            if rxn.force >= 0:
                ax_beam.annotate(f"R = {rxn.force:.1f} kN", xy=(x, -0.20), xytext=(x, -1.85),
                                 arrowprops=dict(arrowstyle="->", color="blue", lw=2.2), ha="center", va="top",
                                 color="blue", fontweight="bold", fontsize=9.5,
                                 bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="blue", alpha=0.85))
            else:
                ax_beam.annotate(f"R = {rxn.force:.1f} kN", xy=(x, 0.20), xytext=(x, 1.85),
                                 arrowprops=dict(arrowstyle="->", color="blue", lw=2.2), ha="center", va="bottom",
                                 color="blue", fontweight="bold", fontsize=9.5,
                                 bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="blue", alpha=0.85))

        for mom in app_moments:
            symbol = "↺" if mom.moment > 0 else "↻"
            ax_beam.text(x, 2.25, f"M = {abs(mom.moment)} kNm {symbol}", ha="center", va="center", color="purple",
                         fontweight="bold", fontsize=9.5,
                         bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="purple", alpha=0.85))
            ax_beam.plot([x, x], [0.1, 1.95], color="purple", linestyle=":", linewidth=1.2)

    # ==========================================
    # SFD & BMD
    # ==========================================
    ax_sfd.set_title("Shear Force Diagram (SFD)")
    ax_sfd.plot(x_grid, V_grid, color="crimson", linewidth=2)
    ax_sfd.fill_between(x_grid, V_grid, 0, color="crimson", alpha=0.15)
    ax_sfd.axhline(0, color="black", linewidth=0.8)
    ax_sfd.set_ylabel("Shear Force (kN)")
    ax_sfd.grid(True, linestyle="--", alpha=0.6)

    ax_bmd.set_title("Bending Moment Diagram (BMD)")
    ax_bmd.plot(x_grid, M_grid, color="navy", linewidth=2)
    ax_bmd.fill_between(x_grid, M_grid, 0, color="navy", alpha=0.15)
    ax_bmd.axhline(0, color="black", linewidth=0.8)
    ax_bmd.set_xlabel("Beam Position x (m)")
    ax_bmd.set_ylabel("Moment (kNm)")
    ax_bmd.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()

    canvas_manager = fig.canvas.manager
    if canvas_manager is not None:
        try:
            canvas_manager.window.state("zoomed")
        except Exception:
            try:
                canvas_manager.window.showMaximized()
            except Exception:
                try:
                    canvas_manager.full_screen_toggle()
                except Exception:
                    pass

    plt.show()