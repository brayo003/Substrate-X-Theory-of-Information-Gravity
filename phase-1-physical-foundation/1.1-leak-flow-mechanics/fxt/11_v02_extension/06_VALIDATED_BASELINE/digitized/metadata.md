# Digitization metadata

The supplied PDF contains no raw numeric Figure 4/5 datasets. The files in
this directory are digitized comparison data, not original observations.

`../digitize.py` extracts the centres and limits of the plotted coloured
vertical error bars from the PDF's vector paths after rendering page 18 and 19
with `pdftocairo -svg`. It maps the documented axis endpoints linearly:

- Figure 4A: x `[29.214844, 129.691406]` maps to `[0, 400] ns`; y
  `[147.707031, 69.917969]` maps to `[0.8, 1.0]` contrast.
- Figure 5 rotating: x `[48.949219, 226.65625]` maps to `[0, 60] us`; y
  `[245.753906, 119.074219]` maps to `[-0.25, 0.35]` contrast.

The points are subject to figure rendering/axis calibration uncertainty. A
conservative uncertainty of ±0.2 us (Figure 5 time), ±2 ns (Figure 4 time),
and ±0.005 normalized contrast is recommended in addition to the extracted
plotted error bars. The stationary Figure 5 trace is a grey connected line,
not point data; it is deliberately not treated as a quantitative raw dataset.

