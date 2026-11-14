(* Load xAct packages in correct order *)

Get["/home/lenovo/.Mathematica/Applications/xAct/xCore/xCore.m"];
Get["/home/lenovo/.Mathematica/Applications/xAct/xPerm/xPerm.m"];
Get["/home/lenovo/.Mathematica/Applications/xAct/xTensor/xTensor.m"];
Get["/home/lenovo/.Mathematica/Applications/xAct/xCoba/xCoba.m"];

Print["xAct packages loaded"];

(* Define S²×S² manifold *)
DefManifold[S2product, {theta1, phi1, theta2, phi2}];
Print["S²×S² manifold defined with coordinates (theta1, phi1, theta2, phi2)"];

(* Define metric using xAct syntax *)
(* First define the metric as a tensor expression *)
CTensor[metricS2xS2, S2product, {-theta1, -phi1, -theta2, -phi2, -theta1, -phi1, -theta2, -phi2}];

(* Set components manually *)
SetMetric[metricS2xS2, {
  {1, 0, 0, 0},
  {0, Sin[theta1]^2, 0, 0},
  {0, 0, 1, 0},
  {0, 0, 0, Sin[theta2]^2}
}];

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
Print["Scalar curvature R: ", Rscalar];

(* Get component values *)
RicciComponents = ToValues[ComponentArray[Ricci]];
Print["Ricci tensor components: ", MatrixForm[RicciComponents]];

(* Check equality with metric *)
einsteinCheck = Simplify[RicciComponents - metricS2xS2];
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
