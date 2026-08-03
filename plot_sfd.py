import matplotlib.pyplot as plt


def plot_sfd(sfd_data: list[tuple[float, float]]) -> tuple:
    """
    Plots the Shear Force Diagram (SFD) using ax.step() and filled regions.
    """
    x, y = zip(*sfd_data)

    # 1. Create Figure and Axes objects
    fig, ax = plt.subplots(figsize=(9, 4.5))

    # 2. Plot step diagram (where="post" holds shear constant until next x)
    ax.step(x, y, color="tab:blue", linewidth=2, where="post", label="Shear Force (V)")

    # 3. Fill region under the step plot
    ax.fill_between(x, y, color="tab:blue", alpha=0.25, step="post")

    # 4. Reference line, labels, and grid using ax methods
    ax.axhline(0, color="black", linestyle="--", linewidth=1)
    ax.set_xlabel("Position along beam x (m)")
    ax.set_ylabel("Shear Force V (kN)")
    ax.set_title("Shear Force Diagram (SFD)")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right")

    fig.tight_layout()
    plt.show()

    return (fig, ax)