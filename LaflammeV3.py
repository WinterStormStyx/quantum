from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import transpile
from qiskit.providers.basic_provider import BasicSimulator
import qiskit.quantum_info as qi
from qiskit.quantum_info import SparsePauliOp, Statevector
from matplotlib import pyplot as plt
import numpy as np
from qiskit_aer import AerSimulator

qc = QuantumCircuit(9, 9)

qc.initialize("1"+"0"*8, range(9))

qc.cx(0, [3, 6])
qc.h([0, 3, 6])
qc.cx([0, 0, 3, 3, 6, 6], [1, 2, 4, 5, 7, 8])

# qc.x(2)


# qc.cx([0, 0, 3, 3, 6, 6], [1, 2, 4, 5, 7, 8])
# qc.ccx([1, 4, 7], [2, 5, 8], [0, 3, 6])
# qc.h([0, 3, 6])
# qc.cx(0, [3, 6])
# qc.ccx(3, 6, 0)



qc.measure(range(9), range(9))

qc.draw(output="mpl")
plt.show()


simulator = AerSimulator()
compiled_circuit = transpile(qc, simulator)
job = simulator.run(compiled_circuit)
sim_result = job.result()
counts = sim_result.get_counts()
print(counts)