from qiskit import QuantumCircuit
from basis import Basis
from matplotlib import pyplot as plt
from shor_cnot import shorDecode, shorEncode, applyLogicalCNot, simulate

# initialize the two logical qubits
qc1 = shorEncode("1")
qc2 = shorEncode("1")

# build the circuit of two logical qubits
qc = QuantumCircuit(18, 2)
qc.compose(qc1, range(9), inplace = True)
qc.compose(qc2, range(9,18), inplace = True)
qc.barrier()

applyLogicalCNot(qc)
qc.barrier()

qc = shorDecode(qc, 0)  # Decode the first logical qubit
qc = shorDecode(qc, 9)  # Decode the second logical qubit
qc.barrier()

qc.draw("mpl")
plt.title("Logical qubit 18")
plt.show()

print(simulate(qc, Basis.Z))
