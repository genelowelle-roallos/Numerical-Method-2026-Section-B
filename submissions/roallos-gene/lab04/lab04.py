"""
Lab 04: How Accurate Is Good Enough?
Approximating a Civil Engineering Function Using Infinite Series

y = L * sin(theta)   with L = 20 m

This script produces the exact required deliverables:

  1. Numerical Tables          → tables.png  +  tables_and_recommendation.txt
  2. Convergence Plot          → convergence_plot.png
  3. Function Comparison Plot  → function_comparison_plot.png
  4. Error Comparison Plot     → error_comparison_plot.png
  5. Written Recommendation    → (inside tables_and_recommendation.txt)

All series are implemented with explicit Python loops.
"""

import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ------------------------------------------------------------------
# PART 1 – Geometric Series
# ------------------------------------------------------------------
def geometric_sum(x, N):
    """
    Calculate the partial sum S_N = 1 + x + x^2 + ... + x^N
    using an explicit loop (no closed-form formula).
    """
    total = 0.0
    for k in range(N + 1):
        total += x ** k
    return total


# ------------------------------------------------------------------
# PART 2 – Power Series
# ------------------------------------------------------------------
def power_series(x, coefficients):
    """
    Evaluate the power series P_N(x) = a0 + a1*x + a2*x^2 + ... + aN*x^N
    given a list/tuple of coefficients [a0, a1, ..., aN].
    """
    result = 0.0
    for k, a_k in enumerate(coefficients):
        result += a_k * (x ** k)
    return result


# ------------------------------------------------------------------
# PART 3 – Maclaurin Series for sin(theta)
# ------------------------------------------------------------------
def sin_maclaurin(theta, N):
    """
    Approximate sin(theta) with the first N terms of the Maclaurin series
    using only loops and factorials.
    Do NOT call math.sin inside this function.
    """
    result = 0.0
    for n in range(N):
        sign = (-1) ** n
        factorial = math.factorial(2 * n + 1)
        result += sign * (theta ** (2 * n + 1)) / factorial
    return result


# ------------------------------------------------------------------
# PART 5 – Taylor Series for sin(theta) centered at a
# ------------------------------------------------------------------
def sin_taylor(theta, a, N):
    """
    Approximate sin(theta) with the first N terms of the Taylor series
    centered at expansion point a.
    Derivatives of sin cycle every 4 terms.
    """
    result = 0.0
    sin_a = math.sin(a)
    cos_a = math.cos(a)

    for n in range(N):
        # Derivatives cycle: sin, cos, -sin, -cos, ...
        pattern = n % 4
        if pattern == 0:
            f_deriv = sin_a
        elif pattern == 1:
            f_deriv = cos_a
        elif pattern == 2:
            f_deriv = -sin_a
        else:  # pattern == 3
            f_deriv = -cos_a

        term = f_deriv * ((theta - a) ** n) / math.factorial(n)
        result += term
    return result


# ------------------------------------------------------------------
# Helper utilities
# ------------------------------------------------------------------
def deg2rad(deg):
    return deg * math.pi / 180.0


def percentage_error(approx, exact):
    if exact == 0:
        return 0.0
    return abs(approx - exact) / abs(exact) * 100.0


def absolute_error(approx, exact):
    return abs(approx - exact)


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main():
    L = 20.0  # metres
    angles_deg = [1, 2, 5, 10, 15, 20, 30]
    terms_list = [1, 2, 3, 4]
    a_deg = 10.0
    a_rad = deg2rad(a_deg)

    print("=" * 80)
    print("LAB 04 – HOW ACCURATE IS GOOD ENOUGH?")
    print("Approximating y = L * sin(theta) with L = 20 m")
    print("=" * 80)

    # --------------------------------------------------------------
    # PART 1 demonstration – Geometric series
    # --------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PART 1: GEOMETRIC SERIES")
    print("=" * 80)
    for x in [0.5, 0.8, 0.9]:
        exact = 1.0 / (1.0 - x) if abs(x) < 1 else float("inf")
        print(f"\nx = {x}   (exact sum = {exact:.10f})")
        for N in [5, 10, 20, 50]:
            approx = geometric_sum(x, N)
            err = abs(approx - exact) if exact != float("inf") else float("nan")
            print(f"  N = {N:2d}: S_N = {approx:.10f}   |error| = {err:.2e}")

    # --------------------------------------------------------------
    # PART 3 quick check – Maclaurin at 10 degrees
    # --------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PART 3: MACLAURIN SERIES – quick check at theta = 10 deg")
    print("=" * 80)
    theta10 = deg2rad(10)
    exact_sin10 = math.sin(theta10)
    print(f"Exact sin(10°) = {exact_sin10:.12f}")
    for N in terms_list:
        approx = sin_maclaurin(theta10, N)
        abs_err = absolute_error(approx, exact_sin10)
        pct_err = percentage_error(approx, exact_sin10)
        print(f"  N = {N}: approx = {approx:.12f}  abs_err = {abs_err:.2e}  pct_err = {pct_err:.6f} %")

    # --------------------------------------------------------------
    # Collect all table data
    # --------------------------------------------------------------
    all_rows = []

    for series_name, approx_func in [
        ("Maclaurin", lambda th, N: sin_maclaurin(th, N)),
        ("Taylor (a=10°)", lambda th, N: sin_taylor(th, a_rad, N))
    ]:
        for N in terms_list:
            for ang in angles_deg:
                theta = deg2rad(ang)
                exact_y = L * math.sin(theta)
                approx_y = L * approx_func(theta, N)
                abs_err = absolute_error(approx_y, exact_y)
                pct_err = percentage_error(approx_y, exact_y)
                all_rows.append({
                    "Series": series_name,
                    "N": N,
                    "Angle (deg)": ang,
                    "Exact y (m)": exact_y,
                    "Approx y (m)": approx_y,
                    "Abs Error (m)": abs_err,
                    "Pct Error (%)": pct_err
                })

    df = pd.DataFrame(all_rows)

    # Print tables to console
    print("\n" + "=" * 80)
    print("PART 4 & 5: ENGINEERING TABLES  (y = L * sin(theta))")
    print("=" * 80)

    for series_name in ["Maclaurin", "Taylor (a=10°)"]:
        for N in terms_list:
            print(f"\n----- {series_name}  |  N = {N} term(s) -----")
            sub = df[(df["Series"] == series_name) & (df["N"] == N)].copy()
            sub = sub[["Angle (deg)", "Exact y (m)", "Approx y (m)", "Abs Error (m)", "Pct Error (%)"]]
            print(sub.to_string(index=False, float_format=lambda x: f"{x:12.8f}"))

    # --------------------------------------------------------------
    # PART 6 – Minimum terms for < 0.1 % error
    # --------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PART 6: MINIMUM NUMBER OF TERMS FOR < 0.1 % ERROR")
    print("=" * 80)

    tolerance = 0.1
    max_N_search = 15
    min_terms = []

    for ang in angles_deg:
        theta = deg2rad(ang)
        exact_y = L * math.sin(theta)

        # Maclaurin
        mac_N = None
        for N in range(1, max_N_search + 1):
            if percentage_error(L * sin_maclaurin(theta, N), exact_y) < tolerance:
                mac_N = N
                break
        if mac_N is None:
            mac_N = f"> {max_N_search}"

        # Taylor
        tay_N = None
        for N in range(1, max_N_search + 1):
            if percentage_error(L * sin_taylor(theta, a_rad, N), exact_y) < tolerance:
                tay_N = N
                break
        if tay_N is None:
            tay_N = f"> {max_N_search}"

        min_terms.append({"Angle (deg)": ang, "Maclaurin terms": mac_N, "Taylor terms": tay_N})

    df_min = pd.DataFrame(min_terms)
    print("\nMinimum terms required to achieve < 0.1 % error:")
    print(df_min.to_string(index=False))

    # Small-angle approximation
    print("\n--- Small-angle approximation  sin(theta) ≈ theta  (1-term Maclaurin) ---")
    print(f"{'Angle (deg)':>12}  {'Exact y':>12}  {'Approx y':>12}  {'Pct Error (%)':>14}")
    critical_angle = None
    for ang in np.arange(1, 31, 0.5):
        theta = deg2rad(ang)
        exact_y = L * math.sin(theta)
        approx_y = L * theta
        pct = percentage_error(approx_y, exact_y)
        if ang in [1, 2, 5, 10, 15, 20, 25, 30] or (pct >= 0.1 and critical_angle is None):
            print(f"{ang:12.1f}  {exact_y:12.8f}  {approx_y:12.8f}  {pct:14.6f}")
        if pct >= 0.1 and critical_angle is None:
            critical_angle = ang

    print(f"\nCritical angle where 1-term approximation exceeds 0.1 % error ≈ {critical_angle:.1f}°")

    # --------------------------------------------------------------
    # DELIVERABLE 5 + TABLES → TXT file
    # --------------------------------------------------------------
    txt_path = "tables_and_recommendation.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("LAB 04 – HOW ACCURATE IS GOOD ENOUGH?\n")
        f.write("Approximating y = L * sin(theta)  with L = 20 m\n")
        f.write("=" * 80 + "\n\n")

        f.write("DELIVERABLE 1: NUMERICAL TABLES\n")
        f.write("-" * 80 + "\n\n")

        for series_name in ["Maclaurin", "Taylor (a=10°)"]:
            for N in terms_list:
                f.write(f"\n----- {series_name}  |  N = {N} term(s) -----\n")
                sub = df[(df["Series"] == series_name) & (df["N"] == N)].copy()
                sub = sub[["Angle (deg)", "Exact y (m)", "Approx y (m)", "Abs Error (m)", "Pct Error (%)"]]
                f.write(sub.to_string(index=False, float_format=lambda x: f"{x:12.8f}"))
                f.write("\n")

        f.write("\n\n" + "=" * 80 + "\n")
        f.write("MINIMUM TERMS REQUIRED FOR < 0.1 % ERROR\n")
        f.write("=" * 80 + "\n")
        f.write(df_min.to_string(index=False))
        f.write(f"\n\nCritical angle where sin(theta) ≈ theta exceeds 0.1 % error ≈ {critical_angle:.1f}°\n")

        f.write("\n\n" + "=" * 80 + "\n")
        f.write("DELIVERABLE 5: WRITTEN ENGINEERING RECOMMENDATION\n")
        f.write("=" * 80 + "\n\n")

        recommendation = f"""ENGINEERING DECISION – How accurate is good enough?

Requirement: relative error must be strictly less than 0.1 %.

1. Number of terms required (from the numerical search)
   - Maclaurin series:
        • 1 term is enough for 1° and 2°
        • 2 terms are enough for all angles from 5° to 30°
   - Taylor series centered at 10°:
        • 1 term is exact at 10°
        • 3–4 terms are needed for the other angles in the set
   - Classic small-angle approximation (sin θ ≈ θ) stays under 0.1 % error
     only up to approximately {critical_angle:.1f}°.

2. Percentage error achieved
   - With only 2 Maclaurin terms the percentage error is already < 0.07 %
     even at 30°.
   - With 4 Maclaurin terms the error drops below 0.000002 % at 30°.
   - The Taylor series is essentially perfect at the expansion point (10°)
     and still meets the tolerance with 4 terms everywhere in 1°–30°.

3. Convergence behaviour
   - Both series converge rapidly for the modest angles typical in civil-
     engineering geometry problems.
   - Convergence is slower when the evaluation point is far from the
     expansion point; therefore the expansion point should be chosen close
     to the region of interest when a series is used.

4. Computational simplicity vs. accuracy tradeoff
   - The pure Maclaurin series is the simplest to code (only multiplications
     and a factorial).
   - A Taylor series about a non-zero point requires one evaluation of
     sin(a) and cos(a), then the same arithmetic; the extra cost is negligible.
   - In modern computers the exact library function math.sin is both faster
     and more accurate than any truncated series we would write ourselves.

5. Valid angle range for the chosen solution
   - If a pure series implementation is required:
        • Use the 1-term Maclaurin (sin θ ≈ θ) for θ ≤ 4°.
        • Use a 2-term Maclaurin series for all angles up to 30°
          (already satisfies the 0.1 % tolerance).
        • Alternatively use a 4-term Taylor series centered near the
          angles of interest.
   - Outside that range, or whenever a reliable library routine is available,
     the exact sine function should be preferred.

RECOMMENDATION
--------------
For the great majority of civil-engineering calculations involving angles up
to 30°, the practical and safest choice is to use the exact sine function
provided by the language library (math.sin).

If a series approximation is required (educational purposes, hand calculation,
or analytic derivation), then:

  • A 2-term Maclaurin series is already sufficient to meet the 0.1 %
    tolerance for every angle examined in this laboratory, or
  • A Taylor series centered close to the angles of interest can be used
    when even higher local accuracy is desired.

The numerical evidence produced by this program confirms that both series
converge quickly and that the 0.1 % engineering tolerance is easily satisfied
with a very modest number of terms.
"""
        f.write(recommendation)

    print(f"\nSaved: {txt_path}")

    # --------------------------------------------------------------
    # DELIVERABLE 1 (visual) – tables.png
    # --------------------------------------------------------------
    fig_t, axes_t = plt.subplots(2, 1, figsize=(12, 10))

    mac = df[df["Series"] == "Maclaurin"]
    pivot_mac = mac.pivot(index="Angle (deg)", columns="N", values="Pct Error (%)")
    axes_t[0].axis("off")
    axes_t[0].set_title("Maclaurin Series – Percentage Error (%) for N = 1,2,3,4", fontsize=12, pad=10)
    tbl1 = axes_t[0].table(
        cellText=np.round(pivot_mac.values, 6),
        rowLabels=pivot_mac.index,
        colLabels=[f"N={c}" for c in pivot_mac.columns],
        loc="center",
        cellLoc="center"
    )
    tbl1.auto_set_font_size(False)
    tbl1.set_fontsize(9)
    tbl1.scale(1.2, 1.4)

    tay = df[df["Series"] == "Taylor (a=10°)"]
    pivot_tay = tay.pivot(index="Angle (deg)", columns="N", values="Pct Error (%)")
    axes_t[1].axis("off")
    axes_t[1].set_title("Taylor Series (centered at 10°) – Percentage Error (%) for N = 1,2,3,4", fontsize=12, pad=10)
    tbl2 = axes_t[1].table(
        cellText=np.round(pivot_tay.values, 6),
        rowLabels=pivot_tay.index,
        colLabels=[f"N={c}" for c in pivot_tay.columns],
        loc="center",
        cellLoc="center"
    )
    tbl2.auto_set_font_size(False)
    tbl2.set_fontsize(9)
    tbl2.scale(1.2, 1.4)

    fig_t.suptitle("Numerical Tables – Percentage Errors (y = 20·sin(θ))", fontsize=14, y=0.98)
    fig_t.tight_layout(rect=[0, 0, 1, 0.96])
    fig_t.savefig("tables.png", dpi=150, bbox_inches="tight")
    print("Saved: tables.png")

    # --------------------------------------------------------------
    # DELIVERABLE 2 – Convergence Plot
    # --------------------------------------------------------------
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    for ang in [5, 10, 20, 30]:
        pct_mac, pct_tay = [], []
        Ns = list(range(1, 9))
        theta = deg2rad(ang)
        exact_y = L * math.sin(theta)
        for N in Ns:
            pct_mac.append(percentage_error(L * sin_maclaurin(theta, N), exact_y))
            pct_tay.append(percentage_error(L * sin_taylor(theta, a_rad, N), exact_y))
        ax1.semilogy(Ns, pct_mac, "o-", label=f"Maclaurin {ang}°")
        ax1.semilogy(Ns, pct_tay, "s--", label=f"Taylor {ang}°")
    ax1.axhline(0.1, color="red", linestyle=":", linewidth=1.5, label="0.1 % tolerance")
    ax1.set_xlabel("Number of terms N")
    ax1.set_ylabel("Percentage error (%)")
    ax1.set_title("Convergence: Percentage Error vs Number of Terms")
    ax1.legend(loc="upper right", fontsize=8)
    ax1.grid(True, which="both", ls="--", alpha=0.5)
    fig1.tight_layout()
    fig1.savefig("convergence_plot.png", dpi=150)
    print("Saved: convergence_plot.png")

    # --------------------------------------------------------------
    # DELIVERABLE 3 – Function Comparison Plot
    # --------------------------------------------------------------
    fig2, axes = plt.subplots(1, 2, figsize=(14, 5))
    theta_fine = np.linspace(0, deg2rad(35), 400)
    exact_sin = np.sin(theta_fine)

    ax = axes[0]
    ax.plot(np.degrees(theta_fine), exact_sin, "k-", linewidth=2, label="Exact sin(θ)")
    for N, style in zip([1, 2, 3, 4], ["--", "-.", ":", "-"]):
        approx = [sin_maclaurin(t, N) for t in theta_fine]
        ax.plot(np.degrees(theta_fine), approx, style, label=f"Maclaurin N={N}")
    ax.set_xlabel("θ (degrees)")
    ax.set_ylabel("sin(θ)")
    ax.set_title("Maclaurin Series Approximations")
    ax.legend()
    ax.grid(True, alpha=0.4)
    ax.set_xlim(0, 35)

    ax = axes[1]
    ax.plot(np.degrees(theta_fine), exact_sin, "k-", linewidth=2, label="Exact sin(θ)")
    for N, style in zip([1, 2, 3, 4], ["--", "-.", ":", "-"]):
        approx = [sin_taylor(t, a_rad, N) for t in theta_fine]
        ax.plot(np.degrees(theta_fine), approx, style, label=f"Taylor N={N}")
    ax.axvline(10, color="gray", linestyle=":", alpha=0.7, label="Expansion point 10°")
    ax.set_xlabel("θ (degrees)")
    ax.set_ylabel("sin(θ)")
    ax.set_title("Taylor Series (centered at 10°)")
    ax.legend()
    ax.grid(True, alpha=0.4)
    ax.set_xlim(0, 35)

    fig2.suptitle("Function Comparison: Exact vs Series Approximations", fontsize=14)
    fig2.tight_layout()
    fig2.savefig("function_comparison_plot.png", dpi=150)
    print("Saved: function_comparison_plot.png")

    # --------------------------------------------------------------
    # DELIVERABLE 4 – Error Comparison Plot
    # --------------------------------------------------------------
    fig3, axes = plt.subplots(1, 2, figsize=(14, 5))
    N_plot = 4
    mac_abs, tay_abs, mac_pct, tay_pct = [], [], [], []
    for ang in angles_deg:
        theta = deg2rad(ang)
        exact_y = L * math.sin(theta)
        m = L * sin_maclaurin(theta, N_plot)
        t = L * sin_taylor(theta, a_rad, N_plot)
        mac_abs.append(absolute_error(m, exact_y))
        tay_abs.append(absolute_error(t, exact_y))
        mac_pct.append(percentage_error(m, exact_y))
        tay_pct.append(percentage_error(t, exact_y))

    x = np.arange(len(angles_deg))
    width = 0.35

    ax = axes[0]
    ax.bar(x - width/2, mac_abs, width, label="Maclaurin N=4")
    ax.bar(x + width/2, tay_abs, width, label="Taylor N=4")
    ax.set_xticks(x)
    ax.set_xticklabels(angles_deg)
    ax.set_xlabel("Angle (degrees)")
    ax.set_ylabel("Absolute error (m)")
    ax.set_title("Absolute Error Comparison (N = 4)")
    ax.legend()
    ax.set_yscale("log")
    ax.grid(True, axis="y", alpha=0.4)

    ax = axes[1]
    ax.bar(x - width/2, mac_pct, width, label="Maclaurin N=4")
    ax.bar(x + width/2, tay_pct, width, label="Taylor N=4")
    ax.set_xticks(x)
    ax.set_xticklabels(angles_deg)
    ax.set_xlabel("Angle (degrees)")
    ax.set_ylabel("Percentage error (%)")
    ax.set_title("Percentage Error Comparison (N = 4)")
    ax.legend()
    ax.set_yscale("log")
    ax.axhline(0.1, color="red", linestyle=":", label="0.1 % tolerance")
    ax.grid(True, axis="y", alpha=0.4)

    fig3.suptitle("Error Comparison: Maclaurin vs Taylor (N = 4 terms)", fontsize=14)
    fig3.tight_layout()
    fig3.savefig("error_comparison_plot.png", dpi=150)
    print("Saved: error_comparison_plot.png")

    # --------------------------------------------------------------
    # Console recommendation
    # --------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PART 7: FINAL ENGINEERING RECOMMENDATION")
    print("=" * 80)
    print(recommendation)

    print("\n" + "=" * 80)
    print("All required deliverables have been generated:")
    print("  1. tables.png                     (visual numerical tables)")
    print("  2. convergence_plot.png")
    print("  3. function_comparison_plot.png")
    print("  4. error_comparison_plot.png")
    print("  5. tables_and_recommendation.txt  (tables + written recommendation)")
    print("=" * 80)


if __name__ == "__main__":
    main()