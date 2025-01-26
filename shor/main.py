from code import shor, encode, decode
from gates import hadamard, cnot
from measure import Basis, measure, project

import numpy as np

# Shor's code implemented with some errors

for i in range(9):
     qc = shor("+", biterror=i, phaseerror=i, drawCircuit=False, drawStates=False)
     measure(qc, basis=Basis.X)


# Hadamard gate

for state in ["+", "-", "0", "1"]:
    qc, cl = encode(state)
    qc = hadamard(qc)
    qc = decode(qc)
    print(measure(qc, basis=Basis.Z))
    
    qc, cl = encode(state)
    qc = hadamard(qc)
    qc = decode(qc)
    print(measure(qc, basis=Basis.X))


# CNOT gate with errors

for error in range(9):
    # initialize the two logical qubits
    qc1, cl1 = encode("1")
    qc2, cl2 = encode("0")

    # build the circuit of two logical qubits

    error2 = np.random.randint(0, 9) # errors will occur on this random bit in the second logical qubit
    qc2.x(error)
    qc2.x(error2)
    
    qc2.z(error)
    qc2.z(error2)

    qc = cnot(qc1, cl1, qc2, cl2)

    qc = decode(qc, 0)  # Decode the first logical qubit
    qc = decode(qc, 9)  # Decode the second logical qubit

    print("Error on bits ", error, ", ", error2, " ", measure(qc, Basis.Z))
