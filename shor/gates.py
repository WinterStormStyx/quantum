from qiskit import QuantumCircuit, QuantumRegister

def applyLogicalNot(qc):
    """Applying logical not to a circuit

    Args:
        qc (QuantumCircuit): the circuit to apply the not to
    """
    qc.z(0)
    qc.z(3)
    qc.z(6)
    
def hadamard(qc):
    """Applies a Hadamard gate to the logical qubit

    Args:
        qc (QuantumCircuit): the circuit to apply the hadamard gate to

    Returns:
        QuantumCircuit: the circuit with a hadamard gate
    """
    # Majority vote
    qc.cx([0, 0, 3, 3], [1, 2, 4, 5])
    qc.ccx([1, 4], [2, 5], [0, 3])
    
    # Convert 2-3 and 4-5
    qc.x([0, 3, 6, 7, 8])
    qc.cx(8, [6, 7])
    qc.ch([0, 3], 8)
    qc.cx(8, [6, 7])
    qc.x([0, 6, 7, 8])

    # Convert 0-1 and 6-7
    qc.cx(8, [6, 7])
    qc.ch([0, 3], 8)
    qc.cx(8, [6, 7])
    qc.x(3)
    
    # Undo Majority vote
    qc.ccx([1, 4], [2, 5], [0, 3])
    qc.cx([0, 0, 3, 3], [1, 2, 4, 5])
    
    return qc

def cnot(qc1, cl1, qc2, cl2):
    """Apply a controlled not operation on two logical qubits

    Args:
        qc1 (QuantumCircuit): quantum circuit of control qubit
        cl1 (ClassicalRegister): classical register of control qubit
        qc2 (QuantumCircuit): quantum circuit of target qubit
        cl2 (ClassicalRegister): classical register of target qubit

    Returns:
        QuantumCircuit: the combined circuit of both qubits after a CNOT was applied
    """
    qc = QuantumCircuit(QuantumRegister(18), cl1, cl2)
    qc = qc.compose(qc1, range(0, 9))
    qc = qc.compose(qc2, range(9, 18))
    
    # partial decoding on the first logical qubit
    qc.cx([0, 0, 3, 3, 6, 6], [1, 2, 4, 5, 7, 8])
    qc.h([0, 3, 6])

    # actual CNOT
    qc.ccz([0, 3, 0, 0, 3, 0, 0, 3, 0], [3, 6, 6, 3, 6, 6, 3, 6, 6], [9, 9, 9, 12, 12, 12, 15, 15, 15])

    # reencoding what was decoded
    qc.h([0, 3, 6])
    qc.cx([0, 0, 3, 3, 6, 6], [1, 2, 4, 5, 7, 8])
    
    return qc
