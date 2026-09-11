"""Figures for the scoped asymptotic obstruction study; no solver calls."""

from pathlib import Path

import numpy as np

from core.born_structure_plotting import plt, save_figure


def plot_asymptotic_audit(
    output: Path, records: list[dict], profiles: dict[str, np.ndarray],
    scaling: np.ndarray, field_means: np.ndarray, root_samples: dict[str, np.ndarray],
) -> None:
    """Render seven diagnostic views from saved numerical/analytical data."""
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "legend.frameon": False})
    theta, densities, times = profiles["theta"], profiles["density"], profiles["times"]
    ratios = densities / (densities + densities[:, ::-1])
    born = (1 + np.cos(theta)) / 2
    for name, ylabel, arrays in [
        ("polar_densities", r"$P_t(\theta)$ [rad$^{-1}$]", densities),
        ("polar_response", r"$R_t(\theta)$", ratios),
        ("polar_residual", r"$R_t(\theta)-\cos^2(\theta/2)$", ratios-born),
    ]:
        fig, axes = plt.subplots(1, 3, figsize=(10.6, 3.1), sharex=True, sharey=True)
        for i, ax in enumerate(axes):
            ax.plot(theta/np.pi, arrays[i], color="#225e91", label="N-first exact limit")
            if name == "polar_densities":
                ax.plot(theta/np.pi, densities[i, ::-1], "--", color="#bb5939",
                        label="reflected density")
            elif name == "polar_response":
                ax.plot(theta/np.pi, born, "--", color="#bb5939", label="Born")
            else:
                ax.axhline(0, color=".6", lw=.7)
            ax.set(xlabel=r"$\theta/\pi$", title=f"g t = {profiles['g']*times[i]:.2f}")
            ax.grid(alpha=.15)
        axes[0].set_ylabel(ylabel)
        axes[0].legend(fontsize=8)
        fig.suptitle("Collective commuting control: instantaneous thermodynamic law")
        fig.tight_layout()
        save_figure(fig, output/name)

    largest_size = max(r["size"] for r in records)
    latest_time = max(r["time"] for r in records)
    selected = [r for r in records if r["size"] == largest_size and r["field"] == 0]
    fig, axes = plt.subplots(2, 2, figsize=(10, 6.6), sharex=True)
    for seed in sorted({r["seed"] for r in selected}):
        rows = [r for r in selected if r["seed"] == seed and not r["control"]]
        t = [r["time"] for r in rows]
        for ax, metric in zip(axes.ravel(), ["rmse_occupied", "moment_max", "coverage", "max_occupied"]):
            ax.semilogx(t, [r[metric] for r in rows], ".-", lw=.8,
                        label=f"{seed}, {rows[0]['graph']}")
    labels = ["R RMSE, occupied bins only", "max |Born moment residual|",
              "reflected coverage (64 bins)", "max R error, occupied centers only"]
    for ax, label in zip(axes.ravel(), labels):
        ax.set_ylabel(label)
        ax.grid(alpha=.2)
    for ax in axes[-1]:
        ax.set_xlabel("t [inverse energy]")
    axes[0, 0].legend(fontsize=7, ncol=2)
    fig.suptitle(f"Native homogeneous-QZ controls, N={largest_size}; missing support is not filled")
    fig.tight_layout()
    save_figure(fig, output/"long_time_native")

    fig, axes = plt.subplots(1, 2, figsize=(9.3, 3.5))
    axes[0].loglog(scaling[:, 0], scaling[:, 1], "o-", label="exact moment error")
    axes[0].loglog(scaling[:, 0], scaling[:, 2], "--", label="derived leading 1/N term")
    axes[1].loglog(scaling[:, 0], scaling[:, 3], "o-", label="log-moment remainder")
    axes[1].loglog(scaling[:, 0], scaling[0, 3]*(scaling[0, 0]/scaling[:, 0])**2,
                   "--", label="1/N² reference")
    for ax in axes:
        ax.set_xlabel("detector spins N")
        ax.grid(alpha=.2)
        ax.legend(fontsize=8)
    axes[0].set_ylabel(r"$|a_1(N,t)-a_1(\infty,t)|$")
    axes[1].set_ylabel("remainder after derived 1/N correction")
    fig.suptitle(f"Collective exact counting moments at fixed t={float(profiles['scaling_time']):g}, "
                 f"g={float(profiles['g']):g}")
    fig.tight_layout()
    save_figure(fig, output/"finite_size_correction")

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.7))
    for control, marker, label in [(False, "o", "X-conserving"), (True, "x", "central-Z control")]:
        subset = [r for r in records if r["control"] == control]
        axes[0].scatter([r["time"] for r in subset],
                        [max(r["trace_error"], 1e-16) for r in subset],
                        s=12, alpha=.5, marker=marker, label=label)
    axes[0].set(xscale="log", yscale="log", xlabel="t [inverse energy]",
                ylabel="QZ / conditional-trace discrepancy")
    for field in sorted({r["field"] for r in records}):
        subset = [r for r in records if not r["control"] and r["size"] == largest_size
                  and r["field"] == field and r["time"] == latest_time]
        axes[1].plot([r["seed"] for r in subset], [r["d0"] for r in subset],
                     ".-", label=f"hx0={field:g}")
    axes[1].axhline(0, color=".5", lw=.7)
    axes[1].set(xlabel="random Hamiltonian seed",
                ylabel=rf"$d_0$ at t={latest_time:g}, N={largest_size}")
    for ax in axes:
        ax.grid(alpha=.2)
        ax.legend(fontsize=8)
    fig.suptitle("Independent detector/coupling/field variations; theorem scope checked")
    fig.tight_layout()
    save_figure(fig, output/"microscopic_perturbations")

    fig, ax = plt.subplots(figsize=(6.4, 3.7))
    for seed in np.unique(field_means[:, 0]):
        rows = field_means[field_means[:, 0] == seed]
        ax.semilogx(rows[:, 1], rows[:, 2], ".-", lw=.9, label=f"seed {int(seed)}")
    t = np.unique(field_means[:, 1])
    width = float(profiles["field_width"])
    bounds = 2.5/(width*t)
    ax.fill_between(t, -1-np.minimum(bounds, 5), -1+np.minimum(bounds, 5),
                    color=".8", alpha=.5, label="rigorous field-mean bound (clipped)")
    ax.axhline(0, color="#bb5939", ls="--", label="required for Born at every field")
    ax.axhline(-1, color=".4", lw=.7)
    ax.set(xlabel="t [inverse energy]", ylabel=r"field mean of $d_0$",
           ylim=(-3, 1), title=f"Necessary moment obstruction, field interval width {width:g}")
    ax.legend(fontsize=7, ncol=2)
    ax.grid(alpha=.2)
    fig.tight_layout()
    save_figure(fig, output/"field_moment_obstruction")

    chosen_seeds = sorted({r["seed"] for r in records})[:3]
    late_times = sorted({r["time"] for r in records})[-3:]
    fig, axes = plt.subplots(3, 3, figsize=(10.5, 7.5), sharex=True, sharey="row")
    from core.born import born_ratio_from_theta
    for col, (seed, time) in enumerate(zip(chosen_seeds, late_times)):
        row = next(r for r in records if r["seed"] == seed and r["time"] == time
                   and r["size"] == largest_size and r["field"] == 0 and not r["control"])
        angles = root_samples[row["key"]]
        data = born_ratio_from_theta(angles, np.pi-angles, n_theta=64, empty_value=np.nan)
        edges = np.linspace(0, 1, 65)
        axes[0, col].stairs(data.counts_0/angles.size*64/np.pi, edges, label="P")
        axes[0, col].stairs(data.counts_1/angles.size*64/np.pi, edges, label="reflected P", ls="--")
        x = data.theta_centers/np.pi
        axes[1, col].plot(x, data.ratio, ".", ms=4, label="QZ occupied bins")
        axes[1, col].plot(x, data.born, "--", color="#bb5939", label="Born")
        axes[2, col].plot(x, data.ratio-data.born, ".", ms=4)
        axes[2, col].axhline(0, color=".5", lw=.7)
        axes[0, col].set_title(f"{row['graph']}, seed {seed}, t={time:g}\n"
                               f"N={largest_size}; coverage={row['coverage']:.2f}", fontsize=9)
        axes[2, col].set_xlabel(r"$\theta/\pi$")
    for ax, label in zip(axes[:, 0], [r"$P$ [rad$^{-1}$]", r"$R$", r"$R-B$"]):
        ax.set_ylabel(label)
    axes[0, 0].legend(fontsize=7)
    axes[1, 0].legend(fontsize=7)
    for ax in axes.ravel():
        ax.grid(alpha=.15)
    fig.suptitle("Finite native root profiles: missing ratio bins remain missing")
    fig.tight_layout()
    save_figure(fig, output/"native_polar_profiles")
