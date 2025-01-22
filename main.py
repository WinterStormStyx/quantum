from qiskit import QuantumCircuit
from basis import Basis
from matplotlib import pyplot as plt
from shor_cnot import shorDecode, shorEncode, applyLogicalCNot, simulate
import numpy as np

for error in range(9):
    # initialize the two logical qubits
    qc1 = shorEncode("1")
    qc2 = shorEncode("0")

    # build the circuit of two logical qubits
    qc = QuantumCircuit(18, 2)
    qc.compose(qc1, range(9), inplace = True)
    qc.compose(qc2, range(9,18), inplace = True)
    qc.barrier()

    error2 = np.random.randint(9, 18) # errors will occur on this random bit in the second logical qubit
    qc.x(error)
    qc.x(error2)
    
    qc.z(error)
    qc.z(error2)

    applyLogicalCNot(qc)
    qc.barrier()

    qc = shorDecode(qc, 0)  # Decode the first logical qubit
    qc = shorDecode(qc, 9)  # Decode the second logical qubit
    qc.barrier()

    # Draw circuit
    # qc.draw("mpl")
    # plt.title("Logical qubit 18")
    # plt.show()

    print("Error on bits ", error, ", ", error2, " ", simulate(qc, Basis.Z))
