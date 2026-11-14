(* TEST 1: S²×S² Background Construction *)

(* Load xAct packages *)
<< xAct`xTensor`
<< xAct`xCoba`
<< xAct`xPert`

(* Define coordinates *)
DefManifold[S2product, {theta1, phi1, theta2, phi2}];

(* Define metric for S²(r1) x S²(r2) with r1 = r2 = 1 *)
metric = {{1, 0, 0, 0}, {0, Sin[theta1]^2, 0, 0}, {0, 0, 1, 0}, {0, 0, 0, Sin[theta2]^2}};

(* Set the metric *)
DefMetric[S2product, metric];

(* Compute Christoffel symbols *)
Gamma = Christoffel[S2product];

(* Compute Riemann tensor *)
Riemann = RiemannTensor[S2product];

(* Compute Ricci tensor *)
Ricci = RicciTensor[Same, S2product];

(* Compute scalar curvature *)
Rscalar = R[S2product];

(* Print results *)
Print["Metric: ", metric];
Print["Christoffel symbols: ", Gamma];
Print["Riemann tensor components: ", Riemann];
Print["Ricci tensor: ", Ricci];
Print["Scalar curvature: ", Rscalar];

(* Verify Einstein manifold property: R_{μν} = g_{μν} *)
Print["Checking R_{μν} = g_{μν} condition..."];
Print["R_{μν} - g_{μν}: ", Table[Ricci[[i,j]] - metric[[i,j]], {i, 4}, {j, 4}]];
