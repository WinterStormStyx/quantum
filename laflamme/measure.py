from qiskit_aer import AerSimulator
from qiskit import transpile

from qiskit import transpile
from qiskit.quantum_info import partial_trace
from qiskit_aer import Aer

import numpy as np
from enum import Enum

class Basis(Enum):
    """ Helperclass to specify the basis to measure in
        Options are the X, Y, and Z basis
    """
    X = "X"
    Z = "Z"
    Y = "Y"


def measure(qc, basis: Basis, shots=1000):
    """Measure the different states the circuit could be in

    Args:
        qc (QuanutmCircuit): the circuit to be measured
        basis (Basis): the basis in which measurement should happen
        shots (int, optional): How many shots to measure. Defaults to 1000.

    Returns:
        dict: count of how many times different states were measured
              first bit: output state, followed by 4 bits representing the error syndrome
    """
    #now we measure our corrected qubit 2
    if basis == Basis.X:
        qc.h(2)
    qc.measure(2, 4)

    #here comes the tricky part, this simulator works by counting states
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


def statevector(qc, initial = None):
    """Prints the statevector and overlap compared to initial state from the partial trace of 
    the entire density matrix (5 qubits).

    Args:
        qc (_type_): the quantum circuit to make the calculation on
        initial (_type_): the initial state of the circuit (default is None)
    """
    statevector_simulator = Aer.get_backend('statevector_simulator')
    job_sv = statevector_simulator.run(transpile(qc, statevector_simulator))
    result_sv = job_sv.result()
    statevector = partial_trace(result_sv.get_statevector(), [0, 1, 3, 4]).to_statevector()
    print(statevector)
    
    if initial is not None:
        print(np.dot(np.conj(initial.data), statevector.data)**2)


