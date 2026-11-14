# ------- Ansatz used in the paper in Fig. 2 -------


import torchquantum as tq
from torchquantum.measurement import expval_joint_analytical
import pennylane as qml



## The U3CU3 ansatz used in Fig. 2(c)
class QVQEModel(tq.QuantumModule):
    def __init__(self, arch, hamil_info):
        super().__init__()
        self.arch = arch
        self.hamil_info = hamil_info
        self.n_wires = hamil_info["n_wires"]
        self.n_blocks = arch["n_blocks"]
        self.u3_layers = tq.QuantumModuleList()
        self.cu3_layers = tq.QuantumModuleList()
        for _ in range(self.n_blocks):
            self.u3_layers.append(
                tq.Op1QAllLayer(
                    op=tq.U3,
                    n_wires=self.n_wires,
                    has_params=True,
                    trainable=True,
                )
            )
            self.cu3_layers.append(
                tq.Op2QAllLayer(
                    op=tq.CU3,
                    n_wires=self.n_wires,
                    has_params=True,
                    trainable=True,
                    circular=True,
                )
            )

    def forward(self):
        qdev = tq.QuantumDevice(
            n_wires=self.n_wires, bsz=1, device=next(self.parameters()).device
        )

        for k in range(self.n_blocks):
            self.u3_layers[k](qdev)
            self.cu3_layers[k](qdev)

        expval = 0
        for hamil in self.hamil_info["hamil_list"]:
            expval += (
                expval_joint_analytical(qdev, observable=hamil["pauli_string"])
                * hamil["coeff"]
            )

        return expval




## The CZRXRY ansatz used in Fig. 2(d)
def CZRXRYLayer(params, n_qubits):
    for i in range(n_qubits -1):
        qml.CZ(wires = [i, i+1])
    qml.CZ(wires = [n_qubits - 1, 0])

    for i in range(n_qubits):
        qml.RX(params[i, 0], wires = i)
        qml.RY(params[i, 1], wires = i)


## The Strongly Entangling layer in Fig. 2(b) is already implemented in PennyLane, by calling qml.StronglyEntanglingLayers