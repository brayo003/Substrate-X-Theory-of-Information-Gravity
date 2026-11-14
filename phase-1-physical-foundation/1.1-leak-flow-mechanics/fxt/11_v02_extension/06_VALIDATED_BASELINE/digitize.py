#!/usr/bin/env python3
"""Reproducibly extract plotted Figure 4/5 points from the supplied vector PDF.

The paper does not provide raw numerical data. These are digitized comparison
coordinates, with the transformation documented in digitized/metadata.md.
"""
from __future__ import annotations

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "digitized"

# Figure 4A: centres of blue vertical error bars, in the PDF plot coordinate
# system.  Values were extracted from the vector paths in page 18. Axes are
# x=[29.214844,129.691406] -> [0,400] ns and y=[147.707031,69.917969] ->
# [0.8,1.0] normalized contrast.
FIG4A_BARS = [
    (29.271484, 70.519531, 94.937500),
    (41.468750, 90.808594, 112.410156),
    (53.722656, 111.523438, 132.902344),
    (65.974609, 118.910156, 140.859375),
    (78.228516, 107.382812, 128.781250),
    (90.480469, 82.289062, 103.855469),
    (102.734375, 81.929688, 103.753906),
    (114.986328, 105.531250, 126.578125),
    (127.240234, 109.601562, 132.527344),
]

# Figure 5: centres and vertical error-bar bounds directly extracted from the
# blue vector paths on page 19. Axes are x=[48.949219,226.65625] -> [0,60] us
# and y=[245.753906,119.074219] -> [-0.25,0.35] normalized contrast.
FIG5_BARS = [
    (81.933594, 124.917969, 146.617188),
    (91.773438, 157.308594, 183.867188),
    (101.609375, 189.566406, 203.484375),
    (108.171875, 209.539062, 223.007812),
    (114.730469, 220.996094, 236.769531),
    (124.570312, 218.640625, 235.203125),
    (134.410156, 177.777344, 197.113281),
    (140.968750, 151.230469, 178.035156),
    (157.367188, 156.441406, 185.839844),
    (173.765625, 187.390625, 220.851562),
    (190.160156, 188.472656, 213.476562),
]


def linear(value, low_coord, high_coord, low_value, high_value):
    return low_value + (value - low_coord) * (high_value - low_value) / (high_coord - low_coord)


def write_rows(path, header, rows):
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    OUT.mkdir(exist_ok=True)
    fig4 = []
    for x, y_top, y_bottom in FIG4A_BARS:
        duration = linear(x, 29.214844, 129.691406, 0.0, 400.0)
        upper = linear(y_top, 147.707031, 69.917969, 0.8, 1.0)
        lower = linear(y_bottom, 147.707031, 69.917969, 0.8, 1.0)
        fig4.append((duration, (upper + lower) / 2, abs(upper - lower) / 2))
    write_rows(OUT / "figure4a_points.csv", ["pulse_duration_ns", "normalized_contrast", "error_bar"], fig4)

    fig5 = []
    for x, y_top, y_bottom in FIG5_BARS:
        tau = linear(x, 48.949219, 226.65625, 0.0, 60.0)
        upper = linear(y_top, 245.753906, 119.074219, -0.25, 0.35)
        lower = linear(y_bottom, 245.753906, 119.074219, -0.25, 0.35)
        fig5.append((tau, (upper + lower) / 2, abs(upper - lower) / 2))
    write_rows(OUT / "figure5_rotating_points.csv", ["spin_echo_time_us", "normalized_contrast", "error_bar"], fig5)
    print(OUT)


if __name__ == "__main__":
    main()

