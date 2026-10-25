"""
TEG characterisation: model, fit and model-vs-measurement check.

Inputs are CSV files from teg_logger.py (or typed by hand with the same
column names: dT_C, V_V, R_ohm, and optionally t_s, T_hot_C, T_cold_C, T_bath_C).

    Part A  open-circuit log (R_ohm = 0) while the bath cools -> Seebeck coefficient S
    Part B  load sweep at roughly constant dT                 -> R_int, E, P(R), P_max
    Part C  matched load left on while the bath cools (optional) -> check P_max ~ dT^2

Usage:
    python teg_analysis.py --demo                      # simulated data, to test the script
    python teg_analysis.py --a partA.csv --b partB.csv [--c partC.csv]

Outputs: fig1_seebeck.png, fig2_VI.png, fig3_power.png, fig4_dT2.png and results.txt
in the --outdir folder (default: teg_results).

Model (Thevenin equivalent of the module):
    E = S * dT,  I = E / (R + R_int),  V = E - I * R_int,  P = E^2 R / (R + R_int)^2
    P_max = E^2 / (4 R_int) at R = R_int
"""
import argparse
import csv
import math
import os

import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DEFAULT_COLS = ["t_s", "T_hot_C", "T_cold_C", "dT_C", "T_bath_C", "V_V", "R_ohm", "I_A", "P_W"]
WATER_C = 4186.0  # J/(kg K)


# ---------------------------------------------------------------- loading
def load_csv(path):
    """Read a logger CSV, skipping '#' comment lines. Returns dict of numpy arrays."""
    header, rows = None, []
    with open(path, newline="") as f:
        for rec in csv.reader(f):
            if not rec or rec[0].strip().startswith("#"):
                continue
            if header is None and not _is_number(rec[0]):
                header = [h.strip() for h in rec]
                continue
            try:
                rows.append([float(x) if x.strip().lower() not in ("", "nan") else np.nan for x in rec])
            except ValueError:
                continue  # a line garbled by a reset
    header = header or DEFAULT_COLS[: len(rows[0])]
    width = len(header)
    rows = [r for r in rows if len(r) == width]
    data = np.array(rows, dtype=float)
    return {name: data[:, i] for i, name in enumerate(header)}


def _is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def group_by_load(d, settle):
    """Average each resistor's readings, skipping the first `settle` samples after a change."""
    R, V, dT, Th, n = [], [], [], [], []
    r_col = d["R_ohm"]
    boundaries = np.flatnonzero(np.diff(r_col) != 0) + 1
    for seg in np.split(np.arange(len(r_col)), boundaries):
        if r_col[seg[0]] <= 0:
            continue
        keep = seg[settle:] if len(seg) > settle else seg
        R.append(r_col[seg[0]])
        V.append(np.mean(d["V_V"][keep]))
        dT.append(np.mean(d["dT_C"][keep]))
        Th.append(np.mean(d["T_hot_C"][keep]) if "T_hot_C" in d else np.nan)
        n.append(len(keep))
    return np.array(R), np.array(V), np.array(dT), np.array(Th), np.array(n)


# ---------------------------------------------------------------- model
def p_model(R, E, R_int):
    return E**2 * R / (R + R_int) ** 2


def part_a(d, N, min_dT):
    m = (d["R_ohm"] == 0) & (d["dT_C"] >= min_dT) & np.isfinite(d["V_V"])
    dT, V = d["dT_C"][m], d["V_V"][m]
    fit = stats.linregress(dT, V)
    return {
        "dT": dT, "V": V,
        "S": fit.slope, "dS": fit.stderr, "c": fit.intercept, "r2": fit.rvalue**2,
        "S_couple_uV": fit.slope / N * 1e6, "n": len(dT),
    }


def part_b(d, args):
    R, V, dT, Th, n = group_by_load(d, args.settle)
    dT_ref = float(np.mean(dT))
    if not args.no_normalize:  # remove the effect of bath drift: V is proportional to dT at fixed R
        V = V * dT_ref / dT
    I = V / R
    P = V**2 / R

    # V-I line: V = E - I R_int
    vi = stats.linregress(I, V)
    E_vi, R_int_vi = vi.intercept, -vi.slope
    dE_vi, dR_int_vi = vi.intercept_stderr, vi.stderr

    # Uncertainty of each P point: dP/P = sqrt((2 dV/V)^2 + (dR/R)^2)
    dV = args.dV_abs + args.dV_rel * np.abs(V)
    dR = args.dR_abs + args.dR_rel * R
    dP = P * np.sqrt((2 * dV / V) ** 2 + (dR / R) ** 2)

    # Free two-parameter fit of P(R)
    popt, pcov = curve_fit(p_model, R, P, p0=[E_vi, R_int_vi], sigma=dP, absolute_sigma=True)
    E_fit, R_int_fit = popt
    dE_fit, dR_int_fit = np.sqrt(np.diag(pcov))

    return {
        "R": R, "V": V, "I": I, "P": P, "dP": dP, "dT": dT, "Th": Th, "n": n, "dT_ref": dT_ref,
        "E_vi": E_vi, "dE_vi": dE_vi, "R_int_vi": R_int_vi, "dR_int_vi": dR_int_vi, "r2_vi": vi.rvalue**2,
        "E_fit": E_fit, "dE_fit": dE_fit, "R_int_fit": R_int_fit, "dR_int_fit": dR_int_fit,
        "R_peak_meas": R[np.argmax(P)], "P_peak_meas": P.max(),
    }


def part_c(d, args):
    """Every sample at the (fixed) matched load, logged while the bath cools."""
    m = (d["R_ohm"] > 0) & (d["dT_C"] >= args.min_dT) & (d["V_V"] > 0)
    dT, P = d["dT_C"][m], d["V_V"][m] ** 2 / d["R_ohm"][m]
    fit = stats.linregress(np.log(dT), np.log(P))
    return {"dT": dT, "P": P, "slope": fit.slope, "dslope": fit.stderr, "coef": math.exp(fit.intercept)}


def efficiency(S, R_int, dT, Th_C, args):
    """Heat input at the hot face and efficiency at the matched load (R = R_int)."""
    Th = Th_C + 273.15
    Tc = Th - dT
    if args.K is not None:
        K = args.K
        Z = S**2 / (K * R_int)
    else:  # Z from the datasheet: dT_max = Z Tc_min^2 / 2, with Th = 25 C in the datasheet test
        Tc_min = 298.15 - args.dTmax
        Z = 2 * args.dTmax / Tc_min**2
        K = S**2 / (Z * R_int)
    E = S * dT
    I = E / (2 * R_int)
    P = E**2 / (4 * R_int)
    Qh = K * dT + S * Th * I - 0.5 * I**2 * R_int
    Tm = (Th + Tc) / 2
    eta_carnot = dT / Th
    root = math.sqrt(1 + Z * Tm)
    eta_ideal_max = eta_carnot * (root - 1) / (root + Tc / Th)
    eta_ideal_mp = eta_carnot / (2 - eta_carnot / 2 + 4 / (Z * Th))
    return {"K": K, "Z": Z, "ZT": Z * Tm, "I": I, "P": P, "Qh": Qh, "eta": P / Qh,
            "eta_carnot": eta_carnot, "eta_ideal_max": eta_ideal_max, "eta_ideal_mp": eta_ideal_mp}


def calorimetric_qh(d, args):
    """Q_h from the bath's cooling rate during the load sweep (needs a 3rd sensor in the bath)."""
    if "T_bath_C" not in d or "t_s" not in d:
        return None
    m = np.isfinite(d["T_bath_C"])
    if m.sum() < 10:
        return None
    rate = stats.linregress(d["t_s"][m], d["T_bath_C"][m]).slope  # K/s, negative
    return args.bath_mass * WATER_C * (-rate - args.baseline_rate)


# ---------------------------------------------------------------- plots
def plot_all(A, B, C, outdir):
    plt.rcParams.update({"figure.dpi": 130, "axes.grid": True, "grid.alpha": 0.3})

    if A:
        fig, ax = plt.subplots(figsize=(6, 4.2))
        ax.plot(A["dT"], A["V"] * 1000, ".", ms=3, alpha=0.5, label="measured (open circuit)")
        x = np.linspace(0, A["dT"].max() * 1.05, 50)
        ax.plot(x, (A["S"] * x + A["c"]) * 1000, "-",
                label=f"fit: S = {A['S']*1000:.2f} ± {A['dS']*1000:.2f} mV/°C")
        ax.set(xlabel="ΔT across module faces (°C)", ylabel="V_oc (mV)", title="Part A: Seebeck coefficient")
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, "fig1_seebeck.png"))

    if B:
        fig, ax = plt.subplots(figsize=(6, 4.2))
        ax.plot(B["I"], B["V"], "o", label="measured")
        x = np.linspace(0, B["E_vi"] / B["R_int_vi"], 50)
        ax.plot(x, B["E_vi"] - B["R_int_vi"] * x, "-",
                label=f"V = E − I·R_int:  E = {B['E_vi']:.3f} V, R_int = {B['R_int_vi']:.2f} Ω")
        ax.set(xlabel="I (A)", ylabel="V across load (V)", xlim=(0, None), ylim=(0, None),
               title=f"Part B: V-I line at ΔT = {B['dT_ref']:.1f} °C")
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, "fig2_VI.png"))

        fig, ax = plt.subplots(figsize=(6.4, 4.4))
        Rx = np.logspace(np.log10(B["R"].min() / 2), np.log10(B["R"].max() * 2), 200)
        ax.errorbar(B["R"], B["P"] * 1000, yerr=B["dP"] * 1000, fmt="o", capsize=3, label="measured", zorder=3)
        ax.plot(Rx, p_model(Rx, B["E_fit"], B["R_int_fit"]) * 1000, "-",
                label=f"free fit: R_int = {B['R_int_fit']:.2f} Ω")
        if A:
            ax.plot(Rx, p_model(Rx, A["S"] * B["dT_ref"], B["R_int_vi"]) * 1000, "--",
                    label="prediction (S from A, R_int from V-I)")
        ax.axvline(B["R_int_fit"], color="gray", ls=":", lw=1)
        ax.set_xscale("log")
        ax.set(xlabel="Load resistance R (Ω)", ylabel="Power P (mW)",
               title=f"Part B: power vs load at ΔT = {B['dT_ref']:.1f} °C")
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, "fig3_power.png"))

    if C:
        fig, ax = plt.subplots(figsize=(6, 4.2))
        ax.loglog(C["dT"], C["P"] * 1000, ".", ms=3, alpha=0.5, label="measured at matched load")
        x = np.linspace(C["dT"].min() * 0.9, C["dT"].max() * 1.1, 50)
        ax.loglog(x, C["coef"] * x ** C["slope"] * 1000, "-",
                  label=f"slope = {C['slope']:.2f} ± {C['dslope']:.2f} (theory 2)")
        ax.set(xlabel="ΔT (°C)", ylabel="P_max (mW)", title="Part C: P_max vs ΔT")
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, "fig4_dT2.png"))
    plt.close("all")


# ---------------------------------------------------------------- demo data
def make_demo(outdir, seed=1):
    """Simulated logger files with realistic noise and bath drift. NOT real measurements."""
    rng = np.random.default_rng(seed)
    S, R_int = 0.042, 2.3
    hdr = DEFAULT_COLS

    def row(t, th, tc, v, r):
        i = v / r if r > 0 else 0.0
        p = v * v / r if r > 0 else 0.0
        return [round(t, 1), th, tc, th - tc, np.nan, v, r, i, p]

    def write(name, rows):
        path = os.path.join(outdir, name)
        with open(path, "w", newline="") as f:
            f.write("# SIMULATED DATA for testing teg_analysis.py\n")
            w = csv.writer(f)
            w.writerow(hdr)
            for r in rows:
                w.writerow([f"{x:.5g}" if np.isfinite(x) else "nan" for x in r])
        return path

    # Part A: bath cools from 88 C, cold face near 8 C, 1 s samples for 25 min
    rows = []
    for t in range(1500):
        th = 18 + 70 * math.exp(-t / 900) + rng.normal(0, 0.06)
        tc = 8 + 0.08 * (th - 18) + rng.normal(0, 0.06)
        v = S * (th - tc) + rng.normal(0, 0.002)
        rows.append(row(t, th, tc, v, 0))
    pa = write("demo_partA.csv", rows)

    # Part B: load sweep, 30 s per resistor, slow drift in dT; loaded dT drops a little (Peltier back-flow)
    loads = [100.4, 47.1, 22.3, 10.1, 6.75, 4.68, 3.31, 2.21, 1.52, 1.02]
    rows, t = [], 0
    for r in [0] + loads + [0]:
        for _ in range(30):
            dT0 = 45 - 0.006 * t
            i_est = S * dT0 / (r + R_int) if r > 0 else 0
            dT = dT0 * (1 - 0.04 * i_est) + rng.normal(0, 0.05)
            tc = 9 + rng.normal(0, 0.05)
            r_true = r * (1 + rng.normal(0, 0.005)) if r > 0 else 0
            v = S * dT * r_true / (r_true + R_int) if r > 0 else S * dT
            v += rng.normal(0, 0.0015)
            rows.append(row(t, tc + dT, tc, v, r))
            t += 1
    pb = write("demo_partB.csv", rows)

    # Part C: matched load (2.2 ohm) left connected while the bath cools
    rows = []
    for t in range(0, 1200, 2):
        dT = 12 + 45 * math.exp(-t / 700) + rng.normal(0, 0.05)
        v = S * dT * 2.21 / (2.21 + R_int) + rng.normal(0, 0.0015)
        rows.append(row(t, 9 + dT, 9, v, 2.21))
    pc = write("demo_partC.csv", rows)
    return pa, pb, pc


# ---------------------------------------------------------------- report
def report(A, B, C, eff, qh_cal, args):
    L = []
    say = L.append
    say("TEG characterisation results")
    say("=" * 60)
    if args.demo:
        say("NOTE: these numbers come from SIMULATED demo data, not a measurement.")
    if A:
        say("\nPart A: Seebeck coefficient (open circuit)")
        say(f"  points used            {A['n']}")
        say(f"  S_module               {A['S']*1000:.2f} ± {A['dS']*1000:.2f} mV/°C   (R² = {A['r2']:.4f})")
        say(f"  intercept              {A['c']*1000:.2f} mV   (should be near 0; offset = sensor/ADC error)")
        say(f"  S per couple (N={args.N})   {A['S_couple_uV']:.0f} µV/°C   (Bi2Te3 p-n couple ~ 400 µV/K)")
    if B:
        say(f"\nPart B: load sweep at ΔT_ref = {B['dT_ref']:.2f} °C"
            f"{'' if args.no_normalize else ' (V normalised to ΔT_ref)'}")
        say("     R (Ω)    V (V)     I (A)     P (mW)   ±dP     ΔT (°C)")
        for r, v, i, p, dp, dt in zip(B["R"], B["V"], B["I"], B["P"], B["dP"], B["dT"]):
            say(f"  {r:8.2f} {v:8.4f} {i:9.4f} {p*1000:9.2f} {dp*1000:6.2f} {dt:8.2f}")
        say(f"  V-I line:   E = {B['E_vi']:.4f} ± {B['dE_vi']:.4f} V,  "
            f"R_int = {B['R_int_vi']:.3f} ± {B['dR_int_vi']:.3f} Ω   (R² = {B['r2_vi']:.4f})")
        say(f"  Free fit:   E = {B['E_fit']:.4f} ± {B['dE_fit']:.4f} V,  "
            f"R_int = {B['R_int_fit']:.3f} ± {B['dR_int_fit']:.3f} Ω")
        Pmax = B["E_fit"] ** 2 / (4 * B["R_int_fit"])
        say(f"  P_max (fit) = {Pmax*1000:.1f} mW at R = R_int;  "
            f"largest measured P = {B['P_peak_meas']*1000:.1f} mW at R = {B['R_peak_meas']:.2f} Ω")
        say(f"  S from E/ΔT = {B['E_vi']/B['dT_ref']*1000:.2f} mV/°C (compare with Part A)")
    if A and B:
        E_pred = A["S"] * B["dT_ref"]
        P_pred = p_model(B["R"], E_pred, B["R_int_vi"])
        dev = (B["P"] - P_pred) / P_pred * 100
        say("\nModel vs measurement (zero fitted parameters)")
        say(f"  E predicted = S × ΔT = {E_pred:.4f} V vs {B['E_vi']:.4f} V from V-I line "
            f"({(B['E_vi']-E_pred)/E_pred*100:+.1f}%)")
        say(f"  RMS deviation of measured P from predicted P = {np.sqrt(np.mean(dev**2)):.1f}%")
        say(f"  worst point: {dev[np.argmax(np.abs(dev))]:+.1f}% at R = {B['R'][np.argmax(np.abs(dev))]:.2f} Ω")
    if C:
        say("\nPart C: P_max vs ΔT")
        for target in np.linspace(C["dT"].max(), C["dT"].min(), 5):
            k = np.argmin(np.abs(C["dT"] - target))
            dt, p = C["dT"][k], C["P"][k]
            say(f"  ΔT = {dt:6.2f} °C   P = {p*1000:8.2f} mW   P/ΔT² = {p/dt**2*1e6:.1f} µW/°C²")
        say(f"  log-log slope = {C['slope']:.3f} ± {C['dslope']:.3f}   (theory: 2)")
    if eff:
        say(f"\nEfficiency at matched load (ΔT = {B['dT_ref']:.1f} °C)")
        src = "given --K" if args.K is not None else f"datasheet ΔT_max = {args.dTmax} °C"
        say(f"  Z = {eff['Z']*1000:.2f} ×10⁻³ /K  (ZT ≈ {eff['ZT']:.2f}),  K = {eff['K']:.3f} W/K  [{src}]")
        say(f"  I = {eff['I']:.3f} A,  P = {eff['P']*1000:.1f} mW,  Q_h (model) = {eff['Qh']:.2f} W")
        say(f"  η estimate = P / Q_h = {eff['eta']*100:.2f}%")
        if args.K is None:
            say("  (with K taken from the datasheet Z this equals the ideal limit; pass --K or use"
                " calorimetry for an independent Q_h)")
        if qh_cal:
            say(f"  Q_h (calorimetric) = {qh_cal:.2f} W  ->  η = {eff['P']/qh_cal*100:.2f}%")
        say(f"  η Carnot = {eff['eta_carnot']*100:.1f}%,  ideal TEG at max power = {eff['eta_ideal_mp']*100:.2f}%,"
            f"  ideal TEG max efficiency = {eff['eta_ideal_max']*100:.2f}%")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--a", help="Part A CSV (open circuit, bath cooling)")
    ap.add_argument("--b", help="Part B CSV (load sweep)")
    ap.add_argument("--c", help="Part C CSV (matched load at several dT)")
    ap.add_argument("--demo", action="store_true", help="generate and analyse simulated data")
    ap.add_argument("--outdir", default="teg_results")
    ap.add_argument("--N", type=int, default=127, help="number of p-n couples (TEC1-12706: 127)")
    ap.add_argument("--min-dT", type=float, default=3.0, help="ignore Part A points below this dT")
    ap.add_argument("--settle", type=int, default=10, help="samples skipped after each resistor change")
    ap.add_argument("--no-normalize", action="store_true", help="do not correct Part B for dT drift")
    ap.add_argument("--dV-abs", type=float, default=0.0005, help="voltage uncertainty, absolute (V)")
    ap.add_argument("--dV-rel", type=float, default=0.002, help="voltage uncertainty, relative")
    ap.add_argument("--dR-abs", type=float, default=0.05, help="resistance uncertainty, absolute (ohm)")
    ap.add_argument("--dR-rel", type=float, default=0.01, help="resistance uncertainty, relative")
    ap.add_argument("--dTmax", type=float, default=66.0, help="datasheet dT_max, used for Z")
    ap.add_argument("--K", type=float, default=None, help="module thermal conductance W/K (overrides datasheet Z)")
    ap.add_argument("--bath-mass", type=float, default=0.5, help="hot water mass in kg (calorimetry)")
    ap.add_argument("--baseline-rate", type=float, default=0.0,
                    help="bath cooling rate without the module, K/s, positive number (calorimetry)")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    if args.demo:
        args.a, args.b, args.c = make_demo(args.outdir)
    if not (args.a or args.b):
        ap.error("give --a and/or --b, or --demo")

    A = part_a(load_csv(args.a), args.N, args.min_dT) if args.a else None
    dB = load_csv(args.b) if args.b else None
    B = part_b(dB, args) if args.b else None
    C = part_c(load_csv(args.c), args) if args.c else None

    eff = qh_cal = None
    if A and B:
        Th = float(np.nanmean(B["Th"])) if np.isfinite(B["Th"]).any() else 60.0
        eff = efficiency(A["S"], B["R_int_fit"], B["dT_ref"], Th, args)
        qh_cal = calorimetric_qh(dB, args)

    text = report(A, B, C, eff, qh_cal, args)
    print(text)
    with open(os.path.join(args.outdir, "results.txt"), "w", encoding="utf-8") as f:
        f.write(text + "\n")
    plot_all(A, B, C, args.outdir)
    print(f"\nFigures and results.txt saved in {args.outdir}/")


if __name__ == "__main__":
    main()
