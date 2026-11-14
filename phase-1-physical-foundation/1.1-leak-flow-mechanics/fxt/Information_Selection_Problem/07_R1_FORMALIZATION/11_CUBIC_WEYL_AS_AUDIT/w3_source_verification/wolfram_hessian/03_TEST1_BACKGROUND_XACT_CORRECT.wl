(* Load xAct packages in correct order *)

Get["/home/lenovo/.Mathematica/Applications/xAct/xCore/xCore.m"];
Get["/home/lenovo/.Mathematica/Applications/xAct/xPerm/xPerm.m"];
Get["/home/lenovo/.Mathematica/Applications/xAct/xTensor/xTensor.m"];
Get["/home/lenovo/.Mathematica/Applications/xAct/xCoba/xCoba.m"];

Print["xAct packages loaded"];

(* Define S²×S² manifold with proper xAct syntax *)
DefManifold[S2product, 4, {a, b, c, d, e, f, g, h, i, j, k, l, m, n}];
Print["S²×S² manifold defined with indices a, b, c, d, ..."];

(* Define metric using abstract tensor notation *)
(* Euclidean signature (+1) since S²×S² is positive definite *)
DefMetric[1, metric[-a, -b], cd, PrintAs -> "g"];
Print["Metric defined"];

(* Define coordinates *)
DefChart[coords, {theta1, phi1, theta2, phi2}, {a, b, c, d}];
Print["Coordinates defined"];

(* Set metric components using xCoba *)
CTensor[metricArray, {-theta1, -phi1, -theta2, -phi2, -theta1, -phi1, -theta2, -phi2}];

metricArray = {{1, 0, 0, 0}, {0, Sin[theta1]^2, 0, 0}, {0, 0, 1, 0}, {0, 0, 0, Sin[theta2]^2}};

SetMetric[metricArray, metric, coords];
Print["Metric components set"];

(* Compute scalar curvature *)
Rscalar = RicciScalarcd[];
Print["Scalar curvature: ", Rscalar];

(* Compute Ricci tensor *)
Ricci = Riccicd[-a, -b];
Print["Ricci tensor: ", Ricci];

(* Evaluate numerically at a point *)
numericalR = ToNumber[Expand[Rscalar], coords, {theta1 -> Pi/2, phi1 -> 0, theta2 -> Pi/2, phi2 -> 0}];
Print["Scalar curvature (numerical): ", numericalR];

Print["\n=== TEST 1 RESULTS ==="];
If[numericalR == 4,
  Print["✓ TEST 1 PASSED: R = 4 confirmed"],
  Print["✗ TEST 1 FAILED: R ≠ 4 (R = ", numericalR, ")"]
];
