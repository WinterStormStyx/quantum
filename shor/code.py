from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.quantum_info import Statevector

from matplotlib import pyplot as plt


def shor(initial = "0", biterror = None, phaseerror = None, drawCircuit = False, drawStates = False):
    """Creates the circuit for Shor's Code with a given initial state and provided errors

    Args:
        initial (str, optional): The initial state of qubit 0, can be "0" (default), "1", "+", "-", "l", "r".
        biterror (list, optional): A list of qubits that have a bit flip. Defaults to None.
        phaseerror (list, optional): A list of qubits that have a phase flip. Defaults to None.
        drawCircuit (bool, optional): If true, will draw the created circuit. Defaults to False.
        drawStates (bool, optional): If true, will draw the final states of the qubits on Bloch Spheres. Defaults to False.
                                     Note this is the one place where qubit 0 is labeled qubit 8 (reverse order numbering)

    Returns:
        QuantumCircuit: the created quantum circuit
    """
    qc, cl = encode(initial)
    
    # ERROR CAN OCCUR HERE
    if biterror is not None:
        qc.x(biterror)
    if phaseerror is not None:
        qc.z(phaseerror)
    # --------------------

    qc = decode(qc)
    
    if drawCircuit: # Return a drawing of the circuit using MatPlotLib
        qc.draw("mpl")
        plt.show()

    if drawStates:
        psi = Statevector(qc)
        print(psi)
        psi.draw("bloch")  # psi is a Statevector object
        plt.show()

    return qc
    

def encode(initial = "0"):
    """Creates the encoding part of Shor's Code with a given initial state

    Args:
        initial (str, optional): The initial state of qubit 0, can be "0" (default), "1", "+", "-", "l", "r", or 
                                 any other Statevector.

    Returns:
        QuantumCircuit: the created quantum circuit
    """
    # Build a quantum circuit with 9 qubits and 9 classical bits
    cl = ClassicalRegister(9)
    qc = QuantumCircuit(QuantumRegister(9), cl)

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
    
    return qc, cl


def decode(qc, base=0):
    """Creates the decoding part of Shor's code

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
