(* Load xAct packages in correct order *)

Get["/home/lenovo/.Mathematica/Applications/xAct/xCore/xCore.m"];
Print["xCore loaded"];

Get["/home/lenovo/.Mathematica/Applications/xAct/xPerm/xPerm.m"];
Print["xPerm loaded"];

Get["/home/lenovo/.Mathematica/Applications/xAct/xTensor/xTensor.m"];
Print["xTensor loaded"];

(* Test basic functionality *)
Print["Testing xTensor basic functionality..."];

(* Define a simple manifold *)
DefManifold[M, {t, x, y, z}];
Print["Manifold M defined"];

(* Define a simple metric *)
metric = {{-1, 0, 0, 0}, {0, 1, 0, 0}, {0, 0, 1, 0}, {0, 0, 0, 1}};
DefMetric[M, metric, Signature[-1, 3]];
Print["Metric defined for M"];

Print["xTensor basic test successful"];
