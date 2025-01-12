from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import transpile
from qiskit.providers.basic_provider import BasicSimulator
import qiskit.quantum_info as qi
from qiskit.quantum_info import SparsePauliOp, Statevector
from matplotlib import pyplot as plt
import numpy as np
from qiskit_aer import AerSimulator

simulator_basic = BasicSimulator()

err1 = qi.Operator([[0, -1], [1, 0]])
err2 = qi.Operator([[-1, 0], [0, 1]])
err3 = qi.Operator([[1, 0], [0, -1]])
err4 = qi.Operator([[-1, 0], [0, -1]])
err5 = qi.Operator([[0, -1], [-1, 0]])

# Build a quantum circuit
cl = ClassicalRegister(5)
qu = QuantumRegister(5)
qc = QuantumCircuit(qu, cl)

#input state
qc.initialize("+", 2)

qc.initialize("0", 0)
qc.initialize("0", 1)
qc.initialize("0", 3)
qc.initialize("0", 4)

qc.h([0, 1, 3])



qc.mcry(2*np.pi,[1, 2, 3], 4)


qc.x([1, 3])
qc.mcry(2*np.pi, [1, 2, 3], 4)
qc.x([1, 3])

qc.cx(2, 4)

qc.cx(0, [2, 4])

qc.cx(3, 2)

qc.cx(1, 4)
qc.mcry(2*np.pi, [3, 4], 2)

#flipping
qc.z(2)
# decoding
qc.mcry(2*np.pi, [3, 4], 2)
qc.cx(1, 4)

qc.cx(3, 2)

qc.cx(0, [2, 4])

qc.cx(2, 4)

qc.x([1, 3])
qc.mcry(2*np.pi, [1, 2, 3], 4)
qc.x([1, 3])

qc.mcry(2*np.pi,[1, 2, 3], 4)

qc.h([0, 1, 3])
qc.measure([0, 1, 3, 4], range(4))

#  #measuring and storing syndrome
# qc.measure([0, 1, 3, 4], range(4))

#error type 1
qc.unitary(err1, 2).c_if(cl, 13)

#error type 2
qc.unitary(err2, 2).c_if(cl, 15)

#error type 3
qc.unitary(err3, 2).c_if(cl, 1)
qc.unitary(err3, 2).c_if(cl, 10)
qc.unitary(err3, 2).c_if(cl, 12)
qc.unitary(err3, 2).c_if(cl, 5)

#error type 4
qc.unitary(err4, 2).c_if(cl, 3)
qc.unitary(err4, 2).c_if(cl, 8)
qc.unitary(err4, 2).c_if(cl, 4)
qc.unitary(err4, 2).c_if(cl, 2)

#error type 5
qc.unitary(err5, 2).c_if(cl, 6)
qc.unitary(err5, 2).c_if(cl, 7)
qc.unitary(err5, 2).c_if(cl, 11)
qc.unitary(err5, 2).c_if(cl, 14)
qc.unitary(err5, 2).c_if(cl, 9)

qc.measure(2, 4)





# For execution
simulator = AerSimulator()
compiled_circuit = transpile(qc, simulator)
job = simulator.run(compiled_circuit)
sim_result = job.result()
counts = sim_result.get_counts()
print(counts)

