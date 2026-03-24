import random 
from collections import defaultdict
from ansatz import QVQEModel, CZRXRYLayer
import pennylane as qml
import torch 
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
from tqdm import tqdm
import numpy as np









#--------------- Data Sampling for Random Heisenberg XYZ Model ---------------#
def get_coupling_const(n_coupling=3):
    coupling_const = []
    for i in range(n_coupling):
        j = np.random.choice(np.arange(-3.0, 3.1, 0.1))
        coupling_const.append(j)
    return np.array(coupling_const)



def process_heisenberg_xyz(key, n_qubits, J, n_layers=2, n_steps = 2000, lr = 1e-3,): 
    n_cells = [n_qubits]
    heisenberg_xyz_h = qml.spin.heisenberg('chain', n_cells, coupling=J)

    dev = qml.device('lightning.qubit', wires = n_qubits)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


    @qml.qnode(dev, interface='torch', diff_method='adjoint')
    def vqe_circuit(h, params, n_qubits, n_layers):
        for i in range(n_layers):
            CZRXRYLayer(params[i], n_qubits)
        return qml.expval(h)
    
    params = torch.randn((n_layers, n_qubits, 2), requires_grad=True, device=device)

  

    optimizer = torch.optim.Adam([params], lr=lr)


    loss_history = np.zeros(n_steps)
    for i in tqdm(range(n_steps), desc=f'Optimizing Heisenberg XYZ model {key}'):
        optimizer.zero_grad()
        loss = vqe_circuit(heisenberg_xyz_h, params, n_qubits, n_layers)
        loss.backward()
        optimizer.step()
        loss_history[i] = loss.item()

    best_params = params.cpu().detach().numpy()
    params = best_params.reshape((1, 2, n_qubits))
    return key, n_qubits, J, loss_history, best_params









#-------------------Data Sampling for Fermi-Hubbard Model---------------#
def get_t_U(t_max= 5.0, U_max=5.0):
    t = np.random.choice(np.arange(0, t_max+0.1, 0.1))
    U = np.random.choice(np.arange(0, U_max+0.1, 0.1))
    t = np.round(t, 2)
    U = np.round(U, 2)
    return t, U


def process_fermi_hubbard(key, t, U, n_layers = 2, n_qubits = 8, n_steps = 2000,  lr = 1e-3):
    n_cells = [n_qubits//2]

    fermi_hubbard_h = qml.spin.fermi_hubbard('chain', n_cells, hopping=t, coulomb=U, mapping='jordan_wigner')

    dev = qml.device('lightning.qubit', wires=n_qubits)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @qml.qnode(dev, interface='torch', diff_method='adjoint')
    def vqe_circuit(h, params, n_qubits, n_layers):
        for i in range(n_layers):
            CZRXRYLayer(params[i], n_qubits)
        return qml.expval(h)
    params = torch.randn((n_layers, n_qubits, 2), device=device, requires_grad=True)

    optimizer = torch.optim.Adam([params], lr=lr)

    loss_history = np.zeros(n_steps) 

    for i in tqdm(range(n_steps), desc=f'Optimizing Fermi Hubbard {key}'):
        optimizer.zero_grad()
        loss = vqe_circuit(fermi_hubbard_h, params, n_qubits, n_layers)
        loss.backward()
        optimizer.step()
        loss_history[i] = loss.item()


    best_params = params.detach().cpu().numpy()
    best_params = best_params.reshape((1, 2, n_qubits))
    return key, n_qubits, t, U , loss_history, best_params





#----------------Data Sampling for Random TFIM Model ---------------#
def get_j_h(t_max= 5.0, U_max=5.0):
    j = np.random.choice(np.arange(0, t_max+0.1, 0.1))
    h = np.random.choice(np.arange(0, U_max+0.1, 0.1))
    j = np.round(j, 2)
    h = np.round(h, 2)
    return j, h


def process_transverse_ising(key, j, h, cell_wid = 2, cell_len = 4, n_layers = 2, n_steps = 2000,  lr = 1e-3):
    n_cells = [cell_len, cell_wid]
    n_qubits = cell_wid * cell_len
    ti_h = qml.spin.transverse_ising('rectangle', n_cells, coupling = j, h = h)

    dev = qml.device('lightning.qubit', wires=n_qubits)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @qml.qnode(dev, interface='torch', diff_method='adjoint')
    def vqe_circuit(h, params, n_qubits, n_layers):
        for i in range(n_layers):
            CZRXRYLayer(params[i], n_qubits)
        return qml.expval(h)
    params = torch.randn((n_layers, n_qubits, 2), device=device, requires_grad=True)

    optimizer = torch.optim.Adam([params], lr=lr)

    loss_history = np.zeros(n_steps) 

    for i in tqdm(range(n_steps), desc=f'Optimizing Fermi Hubbard {key}'):
        optimizer.zero_grad()
        loss = vqe_circuit(ti_h, params, n_qubits, n_layers)
        loss.backward()
        optimizer.step()
        loss_history[i] = loss.item()


    best_params = params.detach().cpu().numpy()
    best_params = best_params.reshape((1, 2, n_qubits))
    n_cells = np.array(n_cells)
    return key, j, h , n_cells, n_qubits,  loss_history, best_params



#--------------- Data Sampling for Quantum Chemistry Applications ---------------#

def generate_hehp_hamiltonian(bond_length):
    symbols = ['He', 'H']
        
        
    coordinates =  np.array([[bond_length / 3, 0.0, 0.0], [-2 * bond_length / 3, 0.0, 0.0]])  # linear

    H, qubits = qml.qchem.molecular_hamiltonian(
        symbols, coordinates,
        charge=1, 
        mult=1, 
        basis="sto-3g"
    )

    return H, qubits, coordinates



def generate_h2_hamiltonian(bond_length):
    # Atomic symbols for H2 molecule
    symbols = ["H", "H"]

    # Hydrogen atoms along the x-axis at ± bond_length/2
    coordinates = np.array([
        [-bond_length / 2, 0.0, 0.0],  # Hydrogen 1
        [bond_length / 2, 0.0, 0.0]    # Hydrogen 2
    ])

    # Generate the Hamiltonian using PennyLane's quantum chemistry module
    H, qubits = qml.qchem.molecular_hamiltonian(
        symbols, coordinates,
        charge=0, 
        mult=1, 
        basis="sto-3g"
    )

    return H, qubits, coordinates

def generate_nh3_hamiltonian(bond_length):

    # Atomic symbols
    symbols = ["N", "H", "H", "H"]
    
    # Define the trigonal pyramidal structure of NH3
    coordinates = np.array([
        [0.0, 0.0, 0.1],                    # Nitrogen atom
        [bond_length, 0.0, -0.3],           # Hydrogen 1
        [-bond_length / 2, bond_length, -0.3],  # Hydrogen 2
        [-bond_length / 2, -bond_length, -0.3]  # Hydrogen 3
    ])
    H, qubits = qml.qchem.molecular_hamiltonian(
        symbols, coordinates,
        charge=0, 
        mult=1, 
        basis="sto-3g"
    )
    return H, qubits, coordinates






def process_molecular_hamiltonian(key, bond_length, molecule = 'nh3', n_layers=8, n_steps = 2000, lr = 1e-3, init_params = 'random'):
    if molecule == 'nh3':
        h, n_qubits, coordinates = generate_nh3_hamiltonian(bond_length)
        h, n_qubits, coordinates = generate_be_h2_hamiltonian(bond_length)
    elif molecule == 'h2':
        h, n_qubits, coordinates = generate_h2_hamiltonian(bond_length)
    elif molecule == 'hehp':
        h, n_qubits, coordinates = generate_hehp_hamiltonian(bond_length)
    else:
        raise ValueError('Molecule not supported')
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    dev = qml.device('lightning.qubit', wires = n_qubits)
    shape = qml.StronglyEntanglingLayers.shape(n_layers=n_layers, n_wires=n_qubits)
    if init_params == 'random':
        params = torch.randn(shape, requires_grad=True, device=device)
    elif init_params == 'zero':
        params = torch.zeros(shape, requires_grad=True, device=device)
    elif init_params == 'pi':
        params = torch.full(shape, np.pi, requires_grad=True, device=device)
    else:
        params = torch.tensor(init_params, requires_grad=True, device=device)

    @qml.qnode(dev, interface='torch', diff_method='adjoint')
    def hamiltonian_exp_val(h, params):
        qml.StronglyEntanglingLayers(params, wires=range(n_qubits))
        return qml.expval(h)
    
    optimizer = torch.optim.Adam([params], lr=lr)


    loss_history = np.zeros(n_steps)
    for i in tqdm(range(n_steps), desc=f'Optimizing {molecule} hamiltonian {key}'):
        optimizer.zero_grad()
        loss = hamiltonian_exp_val(h, params)

        loss.backward()
        optimizer.step()
        loss_history[i] = loss.item()    


    best_params = params.permute(2, 0, 1)


    return key, n_qubits, bond_length, loss_history, best_params.detach().cpu().numpy()
    


#--------------- Data Sampling for Random VQE Application ---------------#
class VQE():
    def __init__(self,num_qubit, num_coeffs=10, z_prob=0.3, coeff_dtype = 'int'):

        self.num_qubit = num_qubit
        self.circuit = None
        self.hamiltonian_info = {'n_wires': num_qubit, 'hamil_list': []}
        self.num_coeffs = num_coeffs
        self.z_prob = z_prob
        self.coeff_dtype = coeff_dtype

    def generate_random_hamiltonian_info(self):
        if self.coeff_dtype == 'float':
            weights = [random.uniform(0, 5) for _ in range(self.num_coeffs)]

        elif self.coeff_dtype == 'int':
            weights = [random.randint(0, 5) for _ in range(self.num_coeffs)]
        unique_pauli_strings = set()
        term_dict = defaultdict(float)

        # Generate unique Pauli strings
        while len(unique_pauli_strings) < self.num_coeffs:
            pauli_string = "".join(self.z_or_i() for _ in range(self.num_qubit))
            if pauli_string not in unique_pauli_strings:
                unique_pauli_strings.add(pauli_string)

        # Pair unique Pauli strings with weights
        pauli_strings = list(zip(weights, unique_pauli_strings))
        for weight, pauli_string in pauli_strings:
            term_dict[pauli_string] += float(weight)

        # Populate the Hamiltonian information
        if self.coeff_dtype == 'float':
            self.hamiltonian_info['hamil_list'] = [
                {'pauli_string': term, 'coeff': round(coeff * 0.5, 4)}
                for term, coeff in term_dict.items()
            ]
        elif self.coeff_dtype == 'int':
            self.hamiltonian_info['hamil_list'] = [
                {'pauli_string': term, 'coeff': coeff*0.5}
                for term, coeff in term_dict.items()
            ]
        # Build the Hamiltonian string
        self.hamil_string = "+".join(
            f"{entry['coeff']}*{entry['pauli_string']}" for entry in self.hamiltonian_info['hamil_list']
        )



    def z_or_i(self):
        if random.random() > self.z_prob:
            return "Z"
        else:
            return "I"
        

def train(model, optimizer, scheduler, n_epoch = 5, n_step=1):
    loss_history = np.zeros((n_epoch*n_step, 2))
    for epoch in tqdm(range(n_epoch)):
        # print(f"Epoch {epoch+1}, LR: {optimizer.param_groups[0]['lr']}")

        for step in range(n_step):
            loss_index = epoch*n_step + step
            loss = model()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            loss_history[loss_index, 0] = loss_index + 1
            loss_history[loss_index, 1] = loss.item()
        # print(f"Expectation of energy: {loss.item()} at epoch {epoch+1}")
        scheduler.step()

    return loss_history


def valid_test(model):
    with torch.no_grad():
        loss = model()



def process_vqe(num_qubit, arch, param_dict_encoder, param_tensor_encoder, n_epoch, n_step,num_coeffs = 3, coeff_dtype = 'int'):
    vqe = VQE(num_qubit=num_qubit, num_coeffs=num_coeffs, coeff_dtype=coeff_dtype)
    vqe.generate_random_hamiltonian_info()
    hamil_info = vqe.hamiltonian_info
    hamil_string = vqe.hamil_string

    # print(type(hamil_info))
    # print(hamil_info)
    hamil_info_json = json.dumps(hamil_info)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = QVQEModel(arch=arch, hamil_info=hamil_info)

    model.to(device)




    optimizer = optim.Adam(model.parameters(), lr=5e-3, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=n_epoch)



    loss_history = train(model, optimizer, scheduler, n_epoch=n_epoch, n_step=n_step)
    valid_test(model)

    param_dict = param_dict_encoder(model)
    param_tensor = param_tensor_encoder(param_dict)
    param_np_array = param_tensor.cpu().numpy()

    result = {'num_qubit': num_qubit, 'hamil_string': hamil_string, 'loss_history': loss_history, 'model_param': param_np_array, 'hamil_info': hamil_info_json}
    return result