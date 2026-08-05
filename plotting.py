import matplotlib.pyplot as plt


def plot_sfd(sfd_data: list[tuple[float, float]]) -> tuple:
    """Plots the Shear Force Diagram (SFD) using step lines."""
    x, y = zip(*sfd_data)

    fig, ax = plt.subplots(figsize=(9, 4.5))

    ax.step(x, y, color="tab:blue", linewidth=2, where="post", label="Shear Force (V)")
    ax.fill_between(x, y, color="tab:blue", alpha=0.25, step="post")

    ax.axhline(0, color="black", linestyle="--", linewidth=1)
    ax.set_xlabel("Position along beam x (m)")
    ax.set_ylabel("Shear Force V (kN)")
    ax.set_title("Shear Force Diagram (SFD)")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right")

    fig.tight_layout()
    plt.show()

    return fig, ax


def plot_bmd(bmd_data: list[tuple[float, float]]) -> tuple:
    """Plots the Bending Moment Diagram (BMD)."""
    x, y = zip(*bmd_data)

    fig, ax = plt.subplots(figsize=(9, 4.5))

    ax.plot(x, y, color="tab:red", linewidth=2, label="Bending Moment (M)")

    ax.axhline(0, color="black", linestyle="--", linewidth=1)
    ax.set_xlabel("Position along beam x (m)")
    ax.set_ylabel("Bending Moment M (kNm)")
    ax.set_title("Bending Moment Diagram (BMD)")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right")

    fig.tight_layout()
    plt.show()

    return fig, ax