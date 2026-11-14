(* Load xAct packages in correct order *)

Get["/home/lenovo/.Mathematica/Applications/xAct/xCore/xCore.m"];
Get["/home/lenovo/.Mathematica/Applications/xAct/xPerm/xPerm.m"];
Get["/home/lenovo/.Mathematica/Applications/xAct/xTensor/xTensor.m"];
Get["/home/lenovo/.Mathematica/Applications/xAct/xCoba/xCoba.m"];

Print["xAct packages loaded"];

(* Define S²×S² manifold *)
DefManifold[S2product, {theta1, phi1, theta2, phi2}];
Print["S²×S² manifold defined with coordinates (theta1, phi1, theta2, phi2)"];

(* Define metric for S²(r1) x S²(r2) with r1 = r2 = 1 *)
metric = {{1, 0, 0, 0}, {0, Sin[theta1]^2, 0, 0}, {0, 0, 1, 0}, {0, 0, 0, Sin[theta2]^2}};

(* Set the metric *)
DefMetric[S2product, metric];
Print["Metric defined for S²×S²"];

(* Compute Christoffel symbols *)
Gamma = Christoffel[S2product];
Print["Christoffel symbols computed"];

(* Compute Riemann tensor *)
Riemann = RiemannTensor[S2product];
Print["Riemann tensor computed"];

(* Compute Ricci tensor *)
Ricci = RicciTensor[Same, S2product];
Print["Ricci tensor computed"];

(* Compute scalar curvature *)
Rscalar = R[S2product];
Print["Scalar curvature computed"];

(* Print results *)
Print["\n=== TEST 1 RESULTS ==="];
Print["Metric: ", MatrixForm[metric]];
Print["Scalar curvature R: ", Rscalar];

(* Verify Einstein manifold property: R_{μν} = g_{μν} *)
Print["\n=== EINSTEIN MANIFOLD CHECK ==="];
Print["Checking R_{μν} = g_{μν} condition..."];

(* Get component values *)
RicciComponents = ToValues[ComponentArray[Ricci]];
MetricComponents = metric;

Print["Ricci tensor components: ", MatrixForm[RicciComponents]];
Print["Metric components: ", MatrixForm[MetricComponents]];

(* Check equality *)
einsteinCheck = Simplify[RicciComponents - MetricComponents];
Print["R_{μν} - g_{μν}: ", MatrixForm[einsteinCheck]];

If[MatrixQ[einsteinCheck, # == 0 &],
  Print["✓ TEST 1 PASSED: R_{μν} = g_{μν} confirmed"],
  Print["✗ TEST 1 FAILED: R_{μν} ≠ g_{μν}"]
];

(* Check scalar curvature = 4 *)
Print["\n=== SCALAR CURVATURE CHECK ==="];
If[Simplify[Rscalar - 4] == 0,
  Print["✓ TEST 1 PASSED: R = 4 confirmed"],
  Print["✗ TEST 1 FAILED: R ≠ 4 (R = ", Rscalar, ")"]
];
