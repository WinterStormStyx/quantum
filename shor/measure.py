from qiskit_aer import AerSimulator
from qiskit import transpile

from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from qiskit_ibm_runtime import EstimatorV2
from qiskit_ibm_runtime.fake_provider import FakeAlgiers

from matplotlib import pyplot as plt
from enum import Enum

class Basis(Enum):
    """ Helperclass to specify the basis to measure in
        Options are the X, Y, and Z basis
    """
    X = "X"
    Z = "Z"
    Y = "Y"

def measure(qc, basis: Basis, shots = 1000):
    """Find the number of times a certain state is measured for a circuit in a given basis.
    
    Args:
        qc (QuantumCircuit): The circuit to be measured.
        basis (Basis): The basis in which it should be measured.
        shots (int, optional): The number of measurements to take. Defaults to 1000.

    Returns:
        dict: A count of how many times different states were measured
    """
    if basis == Basis.X:
        qc.h(0)
    
    qc.measure(range(9), [8, 7, 6, 5, 4, 3, 2, 1, 0])

    simulator = AerSimulator()
    compiled_circuit = transpile(qc, simulator)
    job = simulator.run(compiled_circuit, shots=shots)
    sim_result = job.result().get_counts()
    
    if basis == Basis.Z:
        return sim_result

    # if measuring in X basis, make sure the output state is either a "+" or "-"
    d = {}
    for (k, val) in sim_result.items():
            d[k.replace("0", "+", 1) if k[0] == "0" else k.replace("1", "-", 1)] = val
    return d

def project(qc, measurement_basis = Basis.Z, num_trials = 10):
    """Runs a quantum circuit using simulation and then measures the output (with noise), showing a plot of it.

    Args:
        qc (QuantumCircuit): The quantum circuit being measured
        measurement_basis (Basis, optional): The basis in which measurement should occur. Defaults to "Z".
        num_trials (int, optional): How many times the simulation and measurement should be repeated. Defaults to 10.
    """
    observables_labels = [i*"I" + measurement_basis + (8-i)*"I" for i in range(9)]
    observables = [SparsePauliOp(label) for label in observables_labels]
    
    # Set up code to run on simulator 
    backend = FakeAlgiers()
    estimator = EstimatorV2(backend)
    
    # Convert to an ISA circuit and draw this
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_circuit = pm.run(qc)
    
    # layout-mapped observables
    mapped_observables = [observable.apply_layout(isa_circuit.layout) for observable in observables]
    
    # Run it
    job = estimator.run([(isa_circuit, mapped_observables)] * num_trials)
    
    values = list(map(lambda pub_result: pub_result.data.evs, job.result()))
    errors = list(map(lambda pub_result: pub_result.data.stds, job.result()))
    
    # plotting graph
    for i in range(num_trials):
        plt.errorbar(observables_labels, values[i], yerr=errors[i], fmt="o", label=i)

    plt.xlabel("Observables")
    plt.ylabel("Values")
    plt.legend()
    
    plt.show()
