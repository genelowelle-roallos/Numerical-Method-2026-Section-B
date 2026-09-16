"""
Lab 04 – Series
Master script that generates ALL deliverables:
  • Exercise1.png / Exercise2.png / Exercise3.png
  • Lab04_Series_Dashboard.html
  • Lab04_Series_Presentation.pptx
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import os
import subprocess
import textwrap

OUT_DIR = os.path.dirname(os.path.abspath(__file__)) or "."
os.chdir(OUT_DIR)
print(f"Working directory: {OUT_DIR}\n")

# ============================================================
# 1. NUMERICAL COMPUTATIONS + FIGURES
# ============================================================
print("=" * 65)
print("EXERCISE 1: Continuous compounding  (1 + 1/n)^n → e")
print("=" * 65)

periods = {
    "yearly":            1,
    "twice a year":      2,
    "quarterly":         4,
    "monthly":           12,
    "weekly":            52,
    "daily":             365,
    "hourly":            365 * 24,
    "every minute":      365 * 24 * 60,
    "every second":      365 * 24 * 60 * 60,
    "every millisecond": 365 * 24 * 60 * 60 * 1000,
    "every microsecond": 365 * 24 * 60 * 60 * 1_000_000,
    "every nanosecond":  365 * 24 * 60 * 60 * 1_000_000_000,
}
labels = list(periods.keys())
ns     = list(periods.values())

def stable_compound(n):
    return np.exp(n * np.log1p(1.0 / n))

values  = [stable_compound(n) for n in ns]
e       = np.e
errors1 = [abs(v - e) for v in values]

print(f"{'How often':<18} {'n':>18} {'(1+1/n)^n':>14} {'|error|':>12}")
print("-" * 65)
for lab, n, v, err in zip(labels, ns, values, errors1):
    print(f"{lab:<18} {n:>18,} {v:>14.8f} {err:>12.2e}")
print(f"\nTrue e ≈ {e:.12f}")

fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5))
fig1.suptitle("Exercise 1: Convergence of (1 + 1/n)^n to e", fontsize=14, fontweight="bold")
ax1.bar(range(len(values)), values, color="steelblue", edgecolor="black")
ax1.axhline(e, color="red", linestyle="--", linewidth=2, label=f"e = {e:.8f}")
ax1.set_xticks(range(len(labels)))
ax1.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
ax1.set_ylabel(r"$(1 + 1/n)^n$")
ax1.set_title("Value per compounding period")
ax1.set_ylim(1.95, 2.85)
ax1.legend(loc="lower right")
ax1.grid(axis="y", alpha=0.3)
ax2.bar(range(len(errors1)), errors1, color="orange", edgecolor="black")
ax2.set_yscale("log")
ax2.set_xticks(range(len(labels)))
ax2.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
ax2.set_ylabel(r"$|(1+1/n)^n - e|$ (log scale)")
ax2.set_title("Error shrinks like e/(2n)")
ax2.grid(axis="y", alpha=0.3, which="both")
fig1.tight_layout()
fig1.savefig("Exercise1.png", dpi=150, bbox_inches="tight")
print("→ Saved Exercise1.png")
plt.close(fig1)

# ---------- Exercise 2 ----------
print("\n" + "=" * 65)
print("EXERCISE 2:  (a^h − 1)/h  →  ln(a)")
print("=" * 65)

hs          = [0.1, 0.01, 0.001, 0.0001, 1e-5, 1e-6, 1e-7]
bases       = [2.0, np.e, 3.0]
base_labels = ["a = 2", "a = e", "a = 3"]
limits      = [np.log(2), 1.0, np.log(3)]
colors      = ["#1f77b4", "#2ca02c", "#d62728"]
results     = [[(a**h - 1)/h for h in hs] for a in bases]

print(f"{'h':>10}", end="")
for lab in base_labels:
    print(f"{lab:>14}", end="")
print()
print("-" * 52)
for i, h in enumerate(hs):
    print(f"{h:10.0e}", end="")
    for j in range(3):
        print(f"{results[j][i]:14.6f}", end="")
    print()
print(f"{'settles at':>10}", end="")
for lim in limits:
    print(f"{lim:14.6f}", end="")
print("\n(Tolerance ~ 1e-6)")

fig2, ax = plt.subplots(figsize=(12, 6))
fig2.suptitle("Exercise 2: (a^h − 1)/h settling to ln(a)\n"
              "Bars: difference quotient per h.  Dashed lines: the limit ln(a).",
              fontsize=13, fontweight="bold")
x = np.arange(len(hs))
width = 0.25
for i, (lab, color, lim, vals) in enumerate(zip(base_labels, colors, limits, results)):
    ax.bar(x + i*width, vals, width, label=f"{lab}  (ln a = {lim:.5f})",
           color=color, edgecolor="black")
    ax.axhline(lim, color=color, linestyle="--", linewidth=1.8, alpha=0.85)
ax.set_xticks(x + width)
ax.set_xticklabels([f"h = {h:g}" for h in hs])
ax.set_ylabel(r"$(a^h - 1)/h$")
ax.set_ylim(0.60, 1.22)
ax.legend(loc="upper right")
ax.grid(axis="y", alpha=0.3)
fig2.tight_layout()
fig2.savefig("Exercise2.png", dpi=150, bbox_inches="tight")
print("→ Saved Exercise2.png")
plt.close(fig2)

# ---------- Exercise 3 ----------
print("\n" + "=" * 65)
print("EXERCISE 3:  e^x = Σ x^n / n!   (x = 1)  up to N = 10 000")
print("=" * 65)

x = 1.0
N_max = 10000
true_e = np.e
partial_sums = np.empty(N_max + 1)
term = 1.0
s = term
partial_sums[0] = s
for n in range(1, N_max + 1):
    term *= x / n
    s += term
    partial_sums[n] = s
errors = np.abs(partial_sums - true_e)

print(f"N =  5  →  {partial_sums[5]:.15f}")
print(f"N = 10  →  {partial_sums[10]:.15f}")
print(f"N = 15  →  {partial_sums[15]:.15f}")
print(f"N = 20  →  {partial_sums[20]:.15f}")
print(f"True e  →  {true_e:.15f}")
print(f"Error after N=20     : {errors[20]:.2e}")
print(f"Error after N=10000  : {errors[-1]:.2e}")

fig3, (ax3, ax4) = plt.subplots(1, 2, figsize=(15.5, 6.2))
fig3.suptitle(r"Exercise 3: $e^x = \sum x^n / n!$  (x = 1), summation up to N = 10,000 terms",
              fontsize=13, fontweight="bold")

selected_N = [1, 2, 3, 5, 10, 15, 20, 30, 50, 100, 1000, 10000]
selected_sums = [partial_sums[n] for n in selected_N]
ax3.bar(range(len(selected_N)), selected_sums, color="#7b2cbf", edgecolor="black", width=0.72)
ax3.axhline(true_e, color="red", linestyle="--", linewidth=2.0, label=f"e = {true_e:.6f}")
ax3.set_xticks(range(len(selected_N)))
ax3.set_xticklabels([str(n) for n in selected_N])
ax3.set_xlabel("number of terms N in the summation")
ax3.set_ylabel(r"$S_N = \sum_{n=0}^{N} x^n / n!$")
ax3.set_title("Histogram of the partial sums")
ax3.set_ylim(0.90, 3.10)
ax3.legend(loc="lower right", fontsize=9)
ax3.grid(axis="y", alpha=0.3)
for i, s_val in enumerate(selected_sums):
    ax3.text(i, s_val + 0.035, f"{s_val:.6f}", ha="center", va="bottom",
             fontsize=7.5, rotation=90)

Ns = np.arange(1, N_max + 1)
ax4.plot(Ns, errors[1:], color="black", linewidth=1.8, zorder=2)
key_points = [
    (1,  "red",    "0 digits",               (6, 12)),
    (2,  "red",    "0 digits",               (6, 12)),
    (3,  "red",    "0 digits",               (6, 12)),
    (5,  "orange", "3 digits",               (10, 8)),
    (10, "green",  "6 digits",               (8, -18)),
    (15, "green",  "12 digits",              (8, -20)),
    (20, "blue",   "15 digits from here on", (14, 12)),
]
for n, col, lab, offset in key_points:
    ax4.scatter(n, errors[n], color=col, s=95, zorder=5, edgecolor="black", linewidth=0.7)
    ax4.annotate(lab, (n, errors[n]), textcoords="offset points", xytext=offset,
                 fontsize=9, color=col, fontweight="bold")
for n, col, _, _ in key_points:
    ax4.axvline(n, color=col, linestyle="-", alpha=0.40, linewidth=1.1)
ax4.axhspan(1e-16, 5e-15, color="lightblue", alpha=0.55, zorder=0)
ax4.text(30, 2.5e-16,
         "machine precision zone: from N = 20 on,\nadding terms cannot improve a float sum",
         fontsize=8.5, color="navy", va="center")
ax4.set_xscale("log")
ax4.set_yscale("log")
ax4.set_xlabel("number of terms N in the summation (log scale)")
ax4.set_ylabel(r"$|S_N - e|$  (log scale)")
ax4.set_title("How many correct digits each N buys (log-log)")
ax4.set_xlim(0.8, 1.2e4)
ax4.set_ylim(5e-17, 3)
ax4.grid(True, which="both", alpha=0.35)
legend_elements = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor="red",    markersize=9, label="rough (error > 1e-2)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="orange", markersize=9, label="engineering (1e-6 to 1e-2)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="green",  markersize=9, label="high precision (< 1e-6)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="blue",   markersize=9, label="machine precision (~2e-16)"),
]
ax4.legend(handles=legend_elements, title="accuracy band", loc="upper right", fontsize=8, title_fontsize=9)
ax4b = ax4.twinx()
ax4b.set_ylabel("correct decimal digits", color="gray")
ax4b.set_ylim(0, 17)
ax4b.tick_params(axis="y", labelcolor="gray")
fig3.tight_layout()
fig3.savefig("Exercise3.png", dpi=150, bbox_inches="tight")
print("→ Saved Exercise3.png")
plt.close(fig3)

print("\n✓ All three figures generated.\n")

# ============================================================
# 2. HTML DASHBOARD
# ============================================================
print("Writing HTML dashboard...")

html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lab 04 · Series</title>
<style>
  :root { --bg:#f5f2e8; --panel:#fffdf7; --ink:#17231d; --dim:#65736b;
    --line:#d9dfd5; --blue:#176b57; --orange:#b7791f; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--ink);
    font:15px/1.62 "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif; }
  .navbar { max-width:1120px; margin:0 auto; padding:34px 26px 16px;
    border-bottom:2px solid var(--ink); }
  .navbar-brand { display:block; color:var(--orange) !important; font:600 11px/1 ui-sans-serif,system-ui,sans-serif;
    letter-spacing:.16em; text-transform:uppercase; }
  .navbar .small { display:block; color:var(--ink) !important; font:31px/1.2 Georgia,serif; margin-top:10px; }
  .facts { display:flex; flex-wrap:wrap; gap:0 30px; margin-top:14px;
    font:12.5px/1.5 ui-sans-serif,system-ui,sans-serif; color:var(--dim); }
  .facts b { color:var(--ink); font-weight:600; }
  .container-fluid { max-width:1120px; margin:0 auto; padding:22px 26px 90px; }
  .nav-tabs { display:flex; flex-wrap:wrap; gap:7px; margin:0 0 20px; padding:0;
    border-bottom:2px solid var(--orange); list-style:none; }
  .nav-item { list-style:none; }
  .nav-link { appearance:none; background:#e6ebe3; color:#405047; border:1px solid #cbd6ca;
    border-bottom:0; border-radius:7px 7px 0 0; padding:12px 22px; cursor:pointer;
    font:600 14px ui-sans-serif,system-ui,sans-serif; }
  .nav-link:hover { background:#f8f6ee; color:var(--ink); }
  .nav-link.active { background:var(--orange); color:#fff; border-color:var(--orange); }
  .tab-pane { display:none; }
  .tab-pane.active { display:block; }
  .card { background:var(--panel); border:1px solid var(--line); border-radius:5px; margin-bottom:20px; }
  .card-header { background:transparent; border-bottom:0; padding:20px 22px 2px; font-size:19px; font-weight:600; }
  .card-body { padding:0 22px 20px; }
  .stage-log { margin-bottom:22px; }
  .lede { color:var(--dim); margin:0 0 10px; font-size:14px; }
  .headline { display:grid; grid-template-columns:repeat(auto-fit,minmax(145px,1fr)); gap:0;
    border:1px solid var(--line); border-radius:5px; overflow:hidden; background:var(--panel); margin:18px 0 22px; }
  .hl { padding:13px 16px; border-right:1px solid var(--line); }
  .hl:last-child { border-right:0; }
  .hlv { font:700 25px/1.1 "SFMono-Regular",Consolas,monospace; color:var(--blue); }
  .hll { font:11.5px/1.35 ui-sans-serif,system-ui,sans-serif; color:var(--dim); margin-top:4px; }
  .tabhint { font:600 10.5px ui-sans-serif,system-ui,sans-serif; letter-spacing:.11em;
    text-transform:uppercase; color:var(--dim); margin:30px 0 7px; }
  .sentence { background:#fff8e7; border-left:3px solid var(--orange); padding:12px 16px; margin:16px 0; }
  .defense { background:#edf7f1; border-left:3px solid var(--blue); padding:12px 16px; margin:16px 0; }
  table.table { width:100%; border-collapse:collapse; margin:10px 0 4px; }
  table.table td, table.table th { text-align:left; padding:7px 10px; border-bottom:1px solid var(--line); font-size:.92rem; }
  table.table th { color:var(--dim); font:600 11px ui-sans-serif,system-ui,sans-serif; text-transform:uppercase; }
  code { background:#18352b; color:#f4f0e5; border-radius:4px; padding:2px 5px; }
  footer { color:var(--dim); font-size:12.5px; border-top:1px solid var(--line); padding-top:14px; margin-top:26px; }
  img.fig { max-width:100%; height:auto; border:1px solid var(--line); border-radius:4px; margin:12px 0; }
</style>
</head>
<body>
<nav class="navbar">
  <div class="container-fluid">
    <span class="navbar-brand">Numerical Methods · Laboratory Activity 04</span>
    <span class="small">Series – Limits, Difference Quotients &amp; Taylor Expansion</span>
    <span style="display:block;color:#6c7280;font-size:15px;">(1+1/n)<sup>n</sup> → e &nbsp;·&nbsp; (a<sup>h</sup>−1)/h → ln a &nbsp;·&nbsp; Σ x<sup>n</sup>/n! = e<sup>x</sup></span>
    <div class="facts">
      <span>Student <b>Roallos, Gene Lowelle A.</b></span>
      <span>Section <b>BSCE-3H</b></span>
      <span>Lab <b>#04 – Series</b></span>
      <span>Figures <b>3</b></span>
    </div>
  </div>
</nav>

<div class="container-fluid">
  <div class="card stage-log">
    <div class="card-header">Stage log</div>
    <div class="card-body">
      <p class="lede">Three independent numerical experiments that illustrate the limiting behaviour of classic series and difference quotients.</p>
      <div class="headline">
        <div class="hl"><div class="hlv">e ≈ 2.71828</div><div class="hll">limit of (1+1/n)<sup>n</sup></div></div>
        <div class="hl"><div class="hlv">ln 2 ≈ 0.6931</div><div class="hll">limit of (2<sup>h</sup>−1)/h</div></div>
        <div class="hl"><div class="hlv">N ≈ 20</div><div class="hll">terms to machine precision</div></div>
        <div class="hl"><div class="hlv">10 000</div><div class="hll">maximum terms computed</div></div>
      </div>
    </div>
  </div>

  <ul class="nav-tabs" id="labTabs">
    <li class="nav-item"><button class="nav-link active" data-bs-target="#ex1">Exercise 1</button></li>
    <li class="nav-item"><button class="nav-link" data-bs-target="#ex2">Exercise 2</button></li>
    <li class="nav-item"><button class="nav-link" data-bs-target="#ex3">Exercise 3</button></li>
  </ul>

  <div id="labTabContent">
    <!-- Exercise 1 -->
    <div class="tab-pane active" id="ex1">
      <div class="card">
        <div class="card-header">Exercise 1 · Continuous compounding</div>
        <div class="card-body">
          <p class="lede">Compute <code>(1 + 1/n)<sup>n</sup></code> for compounding frequencies from yearly to nanosecond and observe the convergence to <em>e</em>.</p>
          <div class="sentence">Numerically stable evaluation uses <code>np.exp(n * np.log1p(1/n))</code> so that the result remains accurate even when <em>n</em> exceeds 10<sup>15</sup>.</div>
          <table class="table">
            <thead><tr><th>How often</th><th>n</th><th>(1+1/n)<sup>n</sup></th><th>|error|</th></tr></thead>
            <tbody>
              <tr><td>yearly</td><td>1</td><td>2.00000000</td><td>7.18e-01</td></tr>
              <tr><td>twice a year</td><td>2</td><td>2.25000000</td><td>4.68e-01</td></tr>
              <tr><td>quarterly</td><td>4</td><td>2.44140625</td><td>2.77e-01</td></tr>
              <tr><td>monthly</td><td>12</td><td>2.61303529</td><td>1.05e-01</td></tr>
              <tr><td>weekly</td><td>52</td><td>2.69259695</td><td>2.57e-02</td></tr>
              <tr><td>daily</td><td>365</td><td>2.71456748</td><td>3.71e-03</td></tr>
              <tr><td>hourly</td><td>8 760</td><td>2.71812669</td><td>1.55e-04</td></tr>
              <tr><td>every minute</td><td>525 600</td><td>2.71827924</td><td>2.59e-06</td></tr>
              <tr><td>every second</td><td>31 536 000</td><td>2.71828179</td><td>4.31e-08</td></tr>
              <tr><td>every millisecond</td><td>3.15×10<sup>10</sup></td><td>2.71828183</td><td>4.31e-11</td></tr>
              <tr><td>every microsecond</td><td>3.15×10<sup>13</sup></td><td>2.71828183</td><td>~4e-14</td></tr>
              <tr><td>every nanosecond</td><td>3.15×10<sup>16</sup></td><td>2.71828183</td><td>~0</td></tr>
            </tbody>
          </table>
          <p class="tabhint">Figure</p>
          <img class="fig" src="Exercise1.png" alt="Exercise 1">
          <div class="defense">The left panel shows the values approaching the red dashed line at <em>e</em>. The right panel (log scale) confirms that the absolute error decreases roughly as <em>e</em>/(2<em>n</em>).</div>
        </div>
      </div>
    </div>

    <!-- Exercise 2 -->
    <div class="tab-pane" id="ex2">
      <div class="card">
        <div class="card-header">Exercise 2 · Difference quotient → natural logarithm</div>
        <div class="card-body">
          <p class="lede">Evaluate the difference quotient <code>(a<sup>h</sup> − 1)/h</code> for three bases as <em>h</em> shrinks from 0.1 down to 10<sup>−7</sup>.</p>
          <div class="sentence">The expression is the definition of the derivative of <em>a<sup>x</sup></em> at <em>x</em> = 0, which equals <em>ln a</em>.</div>
          <table class="table">
            <thead><tr><th>h</th><th>a = 2</th><th>a = e</th><th>a = 3</th></tr></thead>
            <tbody>
              <tr><td>0.1</td><td>0.717735</td><td>1.051709</td><td>1.161232</td></tr>
              <tr><td>0.01</td><td>0.695555</td><td>1.005017</td><td>1.104669</td></tr>
              <tr><td>0.001</td><td>0.693387</td><td>1.000500</td><td>1.099216</td></tr>
              <tr><td>0.0001</td><td>0.693171</td><td>1.000050</td><td>1.098673</td></tr>
              <tr><td>1e-5</td><td>0.693150</td><td>1.000005</td><td>1.098618</td></tr>
              <tr><td>1e-6</td><td>0.693147</td><td>1.000000</td><td>1.098613</td></tr>
              <tr><td>1e-7</td><td>0.693147</td><td>1.000000</td><td>1.098612</td></tr>
              <tr><td><b>settles at</b></td><td><b>0.693147</b></td><td><b>1.000000</b></td><td><b>1.098612</b></td></tr>
            </tbody>
          </table>
          <p class="tabhint">Figure</p>
          <img class="fig" src="Exercise2.png" alt="Exercise 2">
          <div class="defense">The three families of bars settle onto the dashed horizontal lines that mark the true values of ln 2, ln e and ln 3. Tolerance of order 10<sup>−6</sup> is reached once <em>h</em> ≤ 10<sup>−6</sup>.</div>
        </div>
      </div>
    </div>

    <!-- Exercise 3 -->
    <div class="tab-pane" id="ex3">
      <div class="card">
        <div class="card-header">Exercise 3 · Taylor series for e<sup>x</sup></div>
        <div class="card-body">
          <p class="lede">Partial sums of the series <code>Σ<sub>n=0</sub><sup>N</sup> x<sup>n</sup>/n!</code> with <em>x</em> = 1, carried out to 10 000 terms.</p>
          <div class="sentence">After only about 20 terms the partial sum has already reached full double-precision accuracy (~15–16 correct decimal digits). Further terms cannot improve a float64 result.</div>
          <table class="table">
            <thead><tr><th>N</th><th>Partial sum S<sub>N</sub></th><th>|S<sub>N</sub> − e|</th><th>≈ digits</th></tr></thead>
            <tbody>
              <tr><td>1</td><td>2.000000000000000</td><td>7.18e-01</td><td>0</td></tr>
              <tr><td>2</td><td>2.500000000000000</td><td>2.18e-01</td><td>0</td></tr>
              <tr><td>3</td><td>2.666666666666667</td><td>5.16e-02</td><td>1</td></tr>
              <tr><td>5</td><td>2.716666666666666</td><td>1.62e-03</td><td>3</td></tr>
              <tr><td>10</td><td>2.718281801146385</td><td>2.73e-08</td><td>7–8</td></tr>
              <tr><td>15</td><td>2.718281828458995</td><td>5.02e-14</td><td>13</td></tr>
              <tr><td>20</td><td>2.718281828459046</td><td>4.44e-16</td><td>15–16</td></tr>
              <tr><td>10 000</td><td>2.718281828459046</td><td>4.44e-16</td><td>15–16</td></tr>
            </tbody>
          </table>
          <p class="tabhint">Figure</p>
          <img class="fig" src="Exercise3.png" alt="Exercise 3">
          <div class="defense">Left panel: successive partial sums rapidly approach the red dashed line at <em>e</em>. Right panel: absolute error on a log-log scale; coloured markers indicate the number of correct decimal digits attained. The light-blue band marks the machine-precision floor.</div>
        </div>
      </div>
    </div>
  </div>

  <footer class="text-center">
    Generated for Laboratory Exercise 04 · Series · All computations performed in double precision (float64)
  </footer>
</div>

<script>
  document.querySelectorAll('#labTabs .nav-link').forEach(function (button) {
    button.addEventListener('click', function () {
      document.querySelectorAll('#labTabs .nav-link').forEach(function (item) { item.classList.remove('active'); });
      document.querySelectorAll('#labTabContent .tab-pane').forEach(function (panel) { panel.classList.remove('active'); });
      button.classList.add('active');
      document.querySelector(button.dataset.bsTarget).classList.add('active');
    });
  });
</script>
</body>
</html>
'''

with open("Lab04_Series_Dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
print("→ Saved Lab04_Series_Dashboard.html")

# ============================================================
# 3. PPTX PRESENTATION (via Node / PptxGenJS)
# ============================================================
print("\nWriting and running presentation script...")

pptx_js = r'''
const pptxgen = require("pptxgenjs");
let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "Roallos, Gene Lowelle A.";
pres.title = "Lab 04 – Series";

const C = { bg:"F5F2E8", panel:"FFFDF7", ink:"17231D", dim:"65736B", blue:"176B57", orange:"B7791F" };

// Slide 1 – Title
{
  let s = pres.addSlide(); s.background = { color: C.bg };
  s.addText("NUMERICAL METHODS · LABORATORY ACTIVITY 04", { x:0.6, y:1.6, w:8.5, h:0.35, fontSize:12, fontFace:"Arial", color:C.orange, bold:true, letterSpacing:3 });
  s.addText("Series", { x:0.6, y:2.15, w:8.5, h:0.7, fontSize:42, fontFace:"Georgia", color:C.ink, bold:true });
  s.addText("(1 + 1/n)ⁿ → e   ·   (aʰ − 1)/h → ln a   ·   Σ xⁿ/n! = eˣ", { x:0.6, y:2.95, w:8.5, h:0.4, fontSize:16, fontFace:"Georgia", color:C.dim, italic:true });
  s.addShape(pres.shapes.RECTANGLE, { x:0.6, y:3.55, w:1.8, h:0.06, fill:{ color:C.orange } });
  s.addText("Roallos, Gene Lowelle A.  ·  BSCE-3H", { x:0.6, y:4.0, w:8.5, h:0.35, fontSize:14, fontFace:"Arial", color:C.dim });
}

// Slide 2 – Objectives
{
  let s = pres.addSlide(); s.background = { color: C.bg };
  s.addText("OBJECTIVES", { x:0.6, y:0.4, w:8.5, h:0.3, fontSize:11, fontFace:"Arial", color:C.orange, bold:true, letterSpacing:2 });
  s.addText("What this laboratory demonstrates", { x:0.6, y:0.75, w:8.5, h:0.45, fontSize:26, fontFace:"Georgia", color:C.ink, bold:true });
  const objs = [
    { num:"01", title:"Continuous compounding", desc:"Show that (1 + 1/n)ⁿ converges to e as the compounding frequency increases from yearly to nanosecond." },
    { num:"02", title:"Difference quotient", desc:"Recover the natural logarithm as the limit of (aʰ − 1)/h when h → 0 for bases 2, e and 3." },
    { num:"03", title:"Taylor series", desc:"Observe how many terms of Σ xⁿ/n! are required to reach full double-precision accuracy for eˣ." }
  ];
  objs.forEach((o,i) => {
    const y = 1.5 + i*1.25;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:0.6, y:y, w:8.8, h:1.1, fill:{ color:C.panel }, rectRadius:0.08 });
    s.addText(o.num, { x:0.85, y:y+0.25, w:0.7, h:0.5, fontSize:22, fontFace:"Georgia", color:C.blue, bold:true });
    s.addText(o.title, { x:1.7, y:y+0.2, w:7.3, h:0.35, fontSize:16, fontFace:"Arial", color:C.ink, bold:true });
    s.addText(o.desc, { x:1.7, y:y+0.55, w:7.3, h:0.4, fontSize:13, fontFace:"Arial", color:C.dim });
  });
}

// Slide 3 – Exercise 1
{
  let s = pres.addSlide(); s.background = { color: C.bg };
  s.addText("EXERCISE 1", { x:0.5, y:0.3, w:9, h:0.25, fontSize:11, fontFace:"Arial", color:C.orange, bold:true, letterSpacing:2 });
  s.addText("Continuous compounding  (1 + 1/n)ⁿ → e", { x:0.5, y:0.55, w:9, h:0.4, fontSize:22, fontFace:"Georgia", color:C.ink, bold:true });
  const boxes = [ {label:"Limit", value:"e ≈ 2.71828"}, {label:"At n = 1 s", value:"2.71828179"}, {label:"At nanosecond", value:"exact e"} ];
  boxes.forEach((b,i) => {
    const x = 0.5 + i*3.1;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:x, y:1.15, w:2.9, h:0.95, fill:{ color:C.panel }, rectRadius:0.06 });
    s.addText(b.label, { x:x+0.15, y:1.25, w:2.6, h:0.25, fontSize:11, fontFace:"Arial", color:C.dim });
    s.addText(b.value, { x:x+0.15, y:1.55, w:2.6, h:0.4, fontSize:18, fontFace:"Georgia", color:C.blue, bold:true });
  });
  s.addText("A naïve power (1+1/n)**n loses all accuracy for large n. The stable form exp(n·log1p(1/n)) remains correct to the nanosecond frequency.", { x:0.5, y:2.4, w:9, h:0.55, fontSize:14, fontFace:"Arial", color:C.dim });
  s.addImage({ path:"Exercise1.png", x:0.5, y:3.1, w:9.0, h:2.2 });
}

// Slide 4 – Exercise 2
{
  let s = pres.addSlide(); s.background = { color: C.bg };
  s.addText("EXERCISE 2", { x:0.5, y:0.3, w:9, h:0.25, fontSize:11, fontFace:"Arial", color:C.orange, bold:true, letterSpacing:2 });
  s.addText("Difference quotient  (aʰ − 1)/h → ln a", { x:0.5, y:0.55, w:9, h:0.4, fontSize:22, fontFace:"Georgia", color:C.ink, bold:true });
  const lims = [ {a:"a = 2", lim:"0.693147", name:"ln 2"}, {a:"a = e", lim:"1.000000", name:"ln e"}, {a:"a = 3", lim:"1.098612", name:"ln 3"} ];
  lims.forEach((L,i) => {
    const x = 0.5 + i*3.1;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:x, y:1.15, w:2.9, h:1.15, fill:{ color:C.panel }, rectRadius:0.06 });
    s.addText(L.a, { x:x+0.15, y:1.25, w:2.6, h:0.25, fontSize:13, fontFace:"Arial", color:C.dim });
    s.addText(L.lim, { x:x+0.15, y:1.55, w:2.6, h:0.4, fontSize:22, fontFace:"Georgia", color:C.blue, bold:true });
    s.addText(L.name, { x:x+0.15, y:1.95, w:2.6, h:0.25, fontSize:12, fontFace:"Arial", color:C.ink });
  });
  s.addText("As h shrinks from 0.1 → 10⁻⁷ the bars settle onto the dashed lines that mark the true natural logarithms.", { x:0.5, y:2.5, w:9, h:0.45, fontSize:14, fontFace:"Arial", color:C.dim });
  s.addImage({ path:"Exercise2.png", x:0.8, y:3.1, w:8.4, h:2.3 });
}

// Slide 5 – Exercise 3
{
  let s = pres.addSlide(); s.background = { color: C.bg };
  s.addText("EXERCISE 3", { x:0.5, y:0.25, w:9, h:0.25, fontSize:11, fontFace:"Arial", color:C.orange, bold:true, letterSpacing:2 });
  s.addText("Taylor series  eˣ = Σ xⁿ / n!   (x = 1)", { x:0.5, y:0.5, w:9, h:0.4, fontSize:22, fontFace:"Georgia", color:C.ink, bold:true });
  const miles = [ {n:"N = 5", dig:"~3 digits"}, {n:"N = 10", dig:"~7–8 digits"}, {n:"N = 15", dig:"~13 digits"}, {n:"N = 20", dig:"15–16 digits"} ];
  miles.forEach((m,i) => {
    const x = 0.5 + i*2.35;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:x, y:1.05, w:2.2, h:0.85, fill:{ color:C.panel }, rectRadius:0.06 });
    s.addText(m.n, { x:x+0.1, y:1.15, w:2.0, h:0.25, fontSize:12, fontFace:"Arial", color:C.dim });
    s.addText(m.dig, { x:x+0.1, y:1.45, w:2.0, h:0.3, fontSize:15, fontFace:"Georgia", color:C.blue, bold:true });
  });
  s.addText("After ≈20 terms the partial sum reaches full double-precision accuracy. Further terms cannot improve a float64 result.", { x:0.5, y:2.1, w:9, h:0.45, fontSize:13, fontFace:"Arial", color:C.dim });
  s.addImage({ path:"Exercise3.png", x:0.4, y:2.65, w:9.2, h:2.6 });
}

// Slide 6 – Conclusions
{
  let s = pres.addSlide(); s.background = { color: C.bg };
  s.addText("CONCLUSIONS", { x:0.6, y:0.4, w:8.5, h:0.3, fontSize:11, fontFace:"Arial", color:C.orange, bold:true, letterSpacing:2 });
  s.addText("What the three experiments show", { x:0.6, y:0.75, w:8.5, h:0.45, fontSize:24, fontFace:"Georgia", color:C.ink, bold:true });
  const cons = [
    { t:"Stability matters", d:"The naïve expression (1+1/n)ⁿ collapses for large n; the rewritten form using log1p remains accurate to nanosecond frequencies." },
    { t:"Definition of the logarithm", d:"The difference quotient (aʰ−1)/h recovers ln a to six or more decimals once h ≤ 10⁻⁶." },
    { t:"Taylor truncation", d:"Only ~20 terms of the exponential series are required to exhaust the precision of IEEE-754 double arithmetic." }
  ];
  cons.forEach((c,i) => {
    const y = 1.5 + i*1.2;
    s.addShape(pres.shapes.RECTANGLE, { x:0.6, y:y, w:0.08, h:0.95, fill:{ color:C.orange } });
    s.addText(c.t, { x:0.9, y:y, w:8.3, h:0.35, fontSize:16, fontFace:"Arial", color:C.ink, bold:true });
    s.addText(c.d, { x:0.9, y:y+0.4, w:8.3, h:0.5, fontSize:14, fontFace:"Arial", color:C.dim });
  });
}

// Slide 7 – End
{
  let s = pres.addSlide(); s.background = { color: C.bg };
  s.addText("END OF LABORATORY 04", { x:0.6, y:2.3, w:8.8, h:0.5, fontSize:28, fontFace:"Georgia", color:C.ink, bold:true, align:"center" });
  s.addText("Series · Limits · Difference Quotients · Taylor Expansion", { x:0.6, y:2.95, w:8.8, h:0.35, fontSize:14, fontFace:"Arial", color:C.dim, align:"center" });
  s.addShape(pres.shapes.RECTANGLE, { x:4.1, y:3.5, w:1.8, h:0.05, fill:{ color:C.orange } });
}

pres.writeFile({ fileName: "Lab04_Series_Presentation.pptx" })
  .then(() => console.log("→ Saved Lab04_Series_Presentation.pptx"))
  .catch(err => console.error(err));
'''

with open("Lab04_Series_Presentation.js", "w", encoding="utf-8") as f:
    f.write(pptx_js)

# Run the Node script
try:
    subprocess.run(["node", "Lab04_Series_Presentation.js"], check=True)
except FileNotFoundError:
    print("⚠  Node.js not found – PPTX was not generated.  Run the .js file manually with:  node Lab04_Series_Presentation.js")
except subprocess.CalledProcessError as e:
    print("⚠  Error while generating PPTX:", e)

print("\n" + "=" * 65)
print("ALL DELIVERABLES GENERATED")
print("=" * 65)
print("  • Exercise1.png")
print("  • Exercise2.png")
print("  • Exercise3.png")
print("  • Lab04_Series_Dashboard.html")
print("  • Lab04_Series_Presentation.pptx")
print("=" * 65)