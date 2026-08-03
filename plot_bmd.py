import matplotlib.pyplot as plt


def plot_bmd(bmd_data: list[tuple[float, float]]) -> tuple:
    """
    Plots the Bending Moment Diagram (BMD) using Object-Oriented Matplotlib.
    """
    x, y = zip(*bmd_data)

    # 1. Create Figure and Axes objects
    fig, ax = plt.subplots(figsize=(9, 4.5))

    # 2. Plot continuous moment diagram with ax.plot
    ax.plot(x, y, color="tab:red", linewidth=2, label="Bending Moment (M)")

    # 3. Reference line, labels, and grid using ax methods
    ax.axhline(0, color="black", linestyle="--", linewidth=1)
    ax.set_xlabel("Position along beam x (m)")
    ax.set_ylabel("Bending Moment M (kNm)")
    ax.set_title("Bending Moment Diagram (BMD)")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right")

    fig.tight_layout()
    plt.show()

    return (fig, ax)