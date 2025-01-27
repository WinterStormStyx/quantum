from gates import hadamard, cnot, t
from code import laflamme, encode, decode
from measure import measure, statevector, Basis

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.quantum_info import Statevector
import numpy as np

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


# Correcting an error

qc = laflamme("0", biterror=2, phaseerror=2)
print("first bit: output, other 4 bits: error syndrome")
print(measure(qc, basis=Basis.Z))


# Hadamard gate

cl = ClassicalRegister(5)
qu = QuantumRegister(5)
qc = QuantumCircuit(qu, cl)

qc = encode(qc, "0")
qc = hadamard(qc)
qc = decode(qc, cl)

statevector(qc, Statevector.from_label("0"))


# CNOT gate

cl1 = ClassicalRegister(4)
qc1 = QuantumCircuit(QuantumRegister(5), cl1)
qc1 = encode(qc1, Statevector([1/np.sqrt(2),1/np.sqrt(2)]))

cl2 = ClassicalRegister(4)
qc2 = QuantumCircuit(QuantumRegister(5), cl2)
qc2 = encode(qc2, Statevector([1, 0]))

res = ClassicalRegister(2)
anc = ClassicalRegister(1)

qc = cnot(qc1, cl1, qc2, cl2, res, anc)

qc = decode(qc, cl1)
qc = decode(qc, cl2, base=6)

qc.measure([2, 8], res)
qc.measure(5, anc)

print(measure(qc, Basis.Z))


# T gate -- apply 4 rotations to get from "+" to "-" state

cl = ClassicalRegister(5)
qu = QuantumRegister(5)
qc = QuantumCircuit(qu, cl)

qc = encode(qc, "+")
qc = t(qc)
qc = t(qc)
qc = t(qc)
qc = t(qc)
qc = decode(qc, cl)

print(measure(qc, basis=Basis.X))


