import mttkinter as tkinter # really dirty fix for a RunTime error you get when you add Aer for noise

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from basis import Basis

def applyLogicalCNot(qc):
    # partial decoding on the first logical qubit
    qc.cx(0,1)
    qc.cx(0,2)
    qc.cx(3,4)
    qc.cx(3,5)
    qc.cx(6,7)
    qc.cx(6,8)
    qc.h(0)
    qc.h(3)
    qc.h(6)

    # actual CNOT
    qc.ccz(0, 3, 9)
    qc.ccz(3, 6, 9)
    qc.ccz(0, 6, 9)
    qc.ccz(0, 3, 12)
    qc.ccz(3, 6, 12)
    qc.ccz(0, 6, 12)
    qc.ccz(0, 3, 15)
    qc.ccz(3, 6, 15)
    qc.ccz(0, 6, 15)

    # reencoding what was decoded
    qc.h(0)
    qc.h(3)
    qc.h(6)
    qc.cx(0,1)
    qc.cx(0,2)
    qc.cx(3,4)
    qc.cx(3,5)
    qc.cx(6,7)
    qc.cx(6,8)
    

def shorEncode(initial = "0"):
    """Creates the encoding part of Shors Code with a given initial state

    Args:
        initial (str, optional): The initial state of qubit 0, can be "0" (default), "1", "+", "-", "l", "r", or 
                                 any other Statevector.

    Returns:
        QuantumCircuit: the created quantum circuit
    """
    # Build a quantum circuit
    qc = QuantumCircuit(9)

    qc.prepare_state(initial, 0)
    qc.prepare_state("0", 1)
    qc.prepare_state("0", 2)
    qc.prepare_state("0", 3)
    qc.prepare_state("0", 4)
    qc.prepare_state("0", 5)
    qc.prepare_state("0", 6)
    qc.prepare_state("0", 7)
    qc.prepare_state("0", 8)

    qc.cx(0, [3, 6])
    qc.h([0, 3, 6])
    qc.cx([0, 0, 3, 3, 6, 6], [1, 2, 4, 5, 7, 8])

    return qc


def shorDecode(qc, base):
    """Creates the decoding part of Shors code

    Args:
        qc (QuantumCircuit): the quantum circuit so far that should now be decoded

    Returns:
        QuantumCircuit: the circuit with the decoding section added
    """
    qc.cx([base, base, base + 3, base + 3, base + 6, base + 6], [base + 1, base + 2, base + 4, base + 5, base + 7, base + 8])
    qc.ccx([base + 1, base + 4, base + 7], [base + 2, base + 5, base + 8], [base, base + 3, base + 6])
    qc.h([base, base + 3, base + 6])
    qc.cx(base, [base +3, base + 6])
    qc.ccx(base + 3, base + 6, base)

    return qc

def simulate(qc, basis: Basis, shots = 1000):
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
        qc.h(9)
    
    qc.measure(0, 1)  # Measure control logical qubit (stored in classical bit 1 because qiskit inverts the results)
    qc.measure(9, 0)  # Measure target logical qubit

    simulator = AerSimulator()
    compiled_circuit = transpile(qc, simulator)
    job = simulator.run(compiled_circuit, shots=shots)
    sim_result = job.result().get_counts()

    if basis == Basis.Z:
        return sim_result

    # if measuring in X basis, make sure the output state is either a "+" or "-"
    d = {}
    for (k, val) in sim_result.items():
            d[k.replace("0", "+") if k[0] == "0" else k.replace("1", "-")] = val
    return d


