"""2-D electrostatic finite-difference solver for PCB line impedance (quasi-TEM).

Solves div(eps grad V) = 0 on a uniform grid for a top-layer trace over the L2 plane of the
JLC04161H-3313 candidate stack, with optional coplanar ground and solder mask, and derives
Z0 = 1 / (c * sqrt(C * C_air)). Differential pairs are solved in odd mode. This is an independent
cross-check of the first-order values in docs/PCB_STACKUP.md, NOT the factory solver: the order-time
JLCPCB calculator/stack ticket remains the authority (O10).

Stack inputs (docs/PCB_STACKUP.md, JLCPCB pages accessed 2026-09-17): prepreg 3313 pressed
0.0994 mm, Dk 4.1; outer copper 35 um; solder mask 30 um over laminate / 15 um over copper, Dk 3.8.
"""
from __future__ import annotations

import sys

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl

C0 = 299792458.0
E0 = 8.8541878128e-12


def solve(traces, h=0.0994, er=4.1, t=0.035, mask=True, gnd_gap=None, d=0.004, span=1.6, air=0.9,
          er_mask=3.8, mask_lam=0.030, mask_cu=0.015):
    """traces: list of (x_left, width, potential). Returns capacitance matrix row sums per trace (F/m)."""
    nx = int(round(2 * span / d)) + 1
    ny = int(round((h + t + air) / d)) + 1
    xs = (np.arange(nx) * d) - span
    ys = np.arange(ny) * d          # y = 0 is the L2 plane
    jh = int(round(h / d))
    jt = int(round((h + t) / d))

    def run(dielectric: bool):
        eps = np.ones((ny - 1, nx - 1))          # cell permittivity
        if dielectric:
            eps[:jh, :] = er
            if mask:
                eps[jh:jh + int(round(mask_lam / d)), :] = er_mask
        fixed = np.zeros((ny, nx), bool)
        val = np.zeros((ny, nx))
        fixed[0, :] = True                       # L2 ground plane
        fixed[-1, :] = True
        fixed[:, 0] = True
        fixed[:, -1] = True                      # far walls grounded
        cond = []
        for (x0, w, v) in traces:
            i0, i1 = int(round((x0 + span) / d)), int(round((x0 + w + span) / d))
            fixed[jh:jt + 1, i0:i1 + 1] = True
            val[jh:jt + 1, i0:i1 + 1] = v
            cond.append((i0, i1))
            if dielectric and mask:
                k = int(round(mask_cu / d))
                eps[jt:jt + k, max(i0 - k, 0):i1 + k] = er_mask
                eps[jh:jt, max(i0 - k, 0):i0] = er_mask
                eps[jh:jt, i1:i1 + k] = er_mask
        if gnd_gap is not None:                  # coplanar ground pour on both outer sides
            lo = min(x0 for x0, _, _ in traces) - gnd_gap
            hi = max(x0 + w for x0, w, _ in traces) + gnd_gap
            il, ih = int(round((lo + span) / d)), int(round((hi + span) / d))
            fixed[jh:jt + 1, :il + 1] = True
            fixed[jh:jt + 1, ih:] = True
        # node-centred finite volume: edge permittivity = mean of the two adjacent cells
        ex = np.zeros((ny, nx - 1))              # horizontal edges
        ex[1:-1, :] = 0.5 * (eps[:-1, :] + eps[1:, :])
        ex[0, :] = eps[0, :]
        ex[-1, :] = eps[-1, :]
        ey = np.zeros((ny - 1, nx))              # vertical edges
        ey[:, 1:-1] = 0.5 * (eps[:, :-1] + eps[:, 1:])
        ey[:, 0] = eps[:, 0]
        ey[:, -1] = eps[:, -1]
        idx = -np.ones((ny, nx), int)
        free = ~fixed
        idx[free] = np.arange(free.sum())
        rows, cols, data = [], [], []
        b = np.zeros(free.sum())
        diag = np.zeros((ny, nx))
        for (dj, di, w_) in ((0, 1, ex), (1, 0, ey)):
            a = np.s_[: ny - dj, : nx - di]
            c = np.s_[dj:, di:]
            wgt = w_
            diag[a] += wgt
            diag[c] += wgt
            ia, ic = idx[a], idx[c]
            both = (ia >= 0) & (ic >= 0)
            rows += [ia[both], ic[both]]
            cols += [ic[both], ia[both]]
            data += [-wgt[both], -wgt[both]]
            m = (ia >= 0) & (ic < 0)
            np.add.at(b, ia[m], wgt[m] * val[c][m])
            m = (ic >= 0) & (ia < 0)
            np.add.at(b, ic[m], wgt[m] * val[a][m])
        rows.append(idx[free])
        cols.append(idx[free])
        data.append(diag[free])
        A = sp.csr_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(len(b), len(b)))
        v = val.copy()
        v[free] = spl.spsolve(A, b)
        # charge on each conductor = sum over its boundary edges of eps * dV
        q = []
        for (i0, i1) in cond:
            tot = 0.0
            m = np.zeros((ny, nx), bool)
            m[jh:jt + 1, i0:i1 + 1] = True
            tot += (ex * (v[:, :-1] - v[:, 1:]) * (m[:, :-1] & ~m[:, 1:])).sum()
            tot += (ex * (v[:, 1:] - v[:, :-1]) * (m[:, 1:] & ~m[:, :-1])).sum()
            tot += (ey * (v[:-1, :] - v[1:, :]) * (m[:-1, :] & ~m[1:, :])).sum()
            tot += (ey * (v[1:, :] - v[:-1, :]) * (m[1:, :] & ~m[:-1, :])).sum()
            q.append(tot * E0)
        return q
    return run(True), run(False)


def z_single(w, **kw):
    (q,), (qa,) = solve([(-w / 2, w, 1.0)], **kw)
    return 1 / (C0 * np.sqrt(q * qa)), q / qa


def z_diff(w, s, **kw):
    tr = [(-s / 2 - w, w, 1.0), (s / 2, w, -1.0)]
    q, qa = solve(tr, **kw)
    zodd = 1 / (C0 * np.sqrt(q[0] * qa[0]))
    return 2 * zodd


if __name__ == "__main__":
    print("validation: air-free check W/h=1 er=1 (expect ~126 ohm microstrip in air, t->0):",
          round(z_single(0.1, h=0.1, er=1.0, t=0.004, mask=False)[0], 1))
    print("\n50-ohm single-ended, L1 over L2 (h 0.0994 mm, Dk 4.1, 35 um Cu, mask on):")
    for w in (0.12, 0.13, 0.14, 0.15, 0.16, 0.18, 0.20, 0.25):
        z, ee = z_single(w)
        zc = z_single(w, gnd_gap=0.20)[0]
        zc3 = z_single(w, gnd_gap=0.30)[0]
        print(f"  W {w:.2f} mm  microstrip {z:5.1f} ohm (eeff {ee:.2f})   coplanar gap 0.20: {zc:5.1f}   gap 0.30: {zc3:5.1f}")
    print("\n90-ohm differential (edge-coupled microstrip, mask on):")
    for w, s in ((0.13, 0.15), (0.14, 0.15), (0.15, 0.15), (0.15, 0.20), (0.16, 0.20), (0.16, 0.33), (0.18, 0.25)):
        print(f"  W {w:.2f} S {s:.2f}: Zdiff {z_diff(w, s):5.1f} ohm")
    print("\npad parasitics to L2 (parallel plate, Dk 4.1, 0.0994 mm): 0402 pad 0.56x0.62 mm ->",
          round(E0 * 4.1 * 0.56e-3 * 0.62e-3 / 0.0994e-3 * 1e12, 3), "pF; U.FL centre pad 1.05x1.0 ->",
          round(E0 * 4.1 * 1.05e-3 * 1.0e-3 / 0.0994e-3 * 1e12, 3), "pF")
