"""Render review alternatives from the committed Python 3.10 benchmark data."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import matplotlib.pyplot as plt
from benchmark_plots import COLORS, STYLE, make_plot
from benchmark_report import LAYERS, WORKLOADS, comparison_groups, load_results


def main() -> None:
    """Write a full linear-scale comparison and an alternative with workload panels."""
    group = comparison_groups(
        load_results(
            [
                ROOT / "benchmarks/results/py310-benchmark.json",
                ROOT / "benchmarks/results/pypy310-benchmark.json",
            ]
        )
    )[0]
    output = ROOT / "chart-previews"
    with plt.rc_context(STYLE):
        figure = make_plot(group, "times")
        figure.suptitle("Python 3.10: median operation times — linear scale", fontsize=14)
        for axis in figure.axes:
            axis.set_xscale("linear")
            axis.set_xlim(left=0)
            axis.set_xlabel("Median time (µs) — lower is faster")
            axis.set_ylim(len(WORKLOADS) - 0.5, -0.5)
            axis.grid(axis="y", color="#666666", alpha=0.4, linewidth=0.8)
            for row in range(len(WORKLOADS)):
                if row % 2 == 0:
                    axis.axhspan(row - 0.5, row + 0.5, color="#000000", alpha=0.045, zorder=0)
                axis.axhline(row + 0.5, color="#888888", alpha=0.25, linewidth=0.7)
        figure.savefig(output / "python-3.10-linear-points.png", dpi=160)
        figure.savefig(output / "python-3.10-linear-points.svg", metadata={"Date": None})
        plt.close(figure)

        backends = group["backends"]
        figure, axes = plt.subplots(len(WORKLOADS), len(LAYERS), figsize=(13, 16))
        for row, workload in enumerate(WORKLOADS):
            for col, layer in enumerate(LAYERS):
                axis = axes[row, col]
                stats = [group["cases"][layer, workload, backend] for backend in backends]
                medians = [s["median"] * 1e6 for s in stats]
                axis.barh(
                    range(len(backends)),
                    medians,
                    height=0.65,
                    color=[COLORS[b] for b in backends],
                    alpha=0.85,
                    zorder=2,
                )
                axis.errorbar(
                    medians,
                    range(len(backends)),
                    xerr=[
                        [(s["median"] - s["q1"]) * 1e6 for s in stats],
                        [(s["q3"] - s["median"]) * 1e6 for s in stats],
                    ],
                    fmt="none",
                    ecolor="#222222",
                    capsize=3,
                    linewidth=1,
                    zorder=3,
                )
                upper = max(s["q3"] * 1e6 for s in stats)
                for index, value in enumerate(medians):
                    axis.text(
                        max(value, stats[index]["q3"] * 1e6) + upper * 0.025,
                        index,
                        f"{value:.3g}",
                        va="center",
                        fontsize=9,
                    )
                axis.set_yticks(range(len(backends)), backends, fontsize=9)
                axis.invert_yaxis()
                axis.set_xlim(0, upper * 1.23)
                axis.set_title(
                    f'{workload} · {"Serialization" if layer == "serialization" else "Complete formatting"}',
                    fontsize=11,
                )
                axis.set_xlabel("Median time (µs)", fontsize=9)
                axis.grid(axis="x", alpha=0.25, zorder=0)
                axis.set_axisbelow(True)
                axis.spines[["top", "right"]].set_visible(False)
        figure.suptitle(
            "Python 3.10: median operation times — linear bars by workload", fontsize=15
        )
        figure.text(
            0.5,
            0.012,
            "Every panel starts at zero; axis ranges differ by panel. Lower is faster.\n"
            "Whiskers span Q1–Q3, not confidence intervals. Labels show median µs.",
            ha="center",
            fontsize=10,
        )
        figure.tight_layout(rect=(0, 0.045, 1, 0.97), h_pad=1.5, w_pad=2)
        figure.savefig(output / "python-3.10-linear-bars.png", dpi=150)
        figure.savefig(output / "python-3.10-linear-bars.svg", metadata={"Date": None})
        plt.close(figure)
    return


if __name__ == "__main__":
    main()
