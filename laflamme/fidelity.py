import numpy as np

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit.quantum_info import Statevector, partial_trace
from qiskit_aer import Aer

from code import laflamme

# This code calculates the fidelity for Laflamme's code

def fidelity(i, fidarr, inp):
    """Calculates inner product and composes a string indicating the test variant depending on the index

    Args:
        i (int): index of the element
        fidarr (_type_): the element at the specified index
        inp (_type_): the reference input

    Returns:
        list: description of error and the calculated fidelity
    """
    fid = float(np.dot(np.conj(fidarr.data), inp.data))**2
    div = np.floor(i/5)
    modu = np.mod(i, 5)

    # because there are 15 tests + 1 no error, every multiple of 5 until 10 (np.floor(i/5)) represents (bit, phase or flip of both)
    # then the modulus indicates on what bit this flip has been performed
    if div == 0:
        st = "bit flip on bit " + str(modu)
    elif div == 1:
        st = "phase flip on bit " + str(modu)
    elif div == 2:
        st = "phase and bit flip on bit " + str(modu)
    elif i == 15:
        st = "no error"

    return [st, fid]

# encode circuit
initial = Statevector([1/np.sqrt(2), 1/np.sqrt(2)])
qc = laflamme(initial=initial)
print("input: ", initial)

# decode circuit
cld = ClassicalRegister(5)
qud = QuantumRegister(5)
qcd = QuantumCircuit(qud, cld)

# error circuit
cle = ClassicalRegister(5)
que = QuantumRegister(5)
qce = QuantumCircuit(que, cle)


# building total circuit
circarr = np.zeros((16, 2), dtype=np.complex128)
statevector_simulator = Aer.get_backend('statevector_simulator')

#now im building a circuit for every single error plus no error and store its result in an array together with its test id which i need for a wrapper function which will output some useful text.
#I build the different circuits by having an encoding circuit (qc), an error circuit (qce) and a decoding plus error correction circuit (qcd)
#I need to build the same 3 circuits 5 times with the error happening on a different qubit, instead of storing the circuit, i store statevector which prevents memory from flooding
#it is important that the built circuit which is built on qctot and with the compose function gets reinitialized every times to clear the circuit. Also, qce.data.pop() is used to remove instructions from the error circuit after being used
for i in range(1, 4):
    for j in range(5):
        if i == 1:
            qctot = QuantumCircuit(5, 5)
            qctot.compose(qc, inplace=True)
            qce.x(j)
            qctot.compose(qce, inplace=True)
            qctot.compose(qcd, inplace=True)
            job_sv = statevector_simulator.run(transpile(qctot, statevector_simulator))
            result_sv = job_sv.result()
            statevector = partial_trace(result_sv.get_statevector(), [0, 1, 3, 4]).to_statevector()
            circarr[j, :] = statevector
            qce.data.pop(0)
        elif i == 2:
            qctot = QuantumCircuit(5, 5)
            qctot.compose(qc, inplace=True)
            qce.z(j)
            qctot.compose(qce, inplace=True)
            qctot.compose(qcd, inplace=True)
            job_sv = statevector_simulator.run(transpile(qctot, statevector_simulator))
            result_sv = job_sv.result()
            statevector = partial_trace(result_sv.get_statevector(), [0, 1, 3, 4]).to_statevector()
            circarr[5+j, :] = statevector
            qce.data.pop(0)
        elif i == 3:
            qctot = QuantumCircuit(5, 5)
            qctot.compose(qc, inplace=True)
            qce.x(j)
            qce.z(j)
            qctot.compose(qce, inplace=True)
            qctot.compose(qcd, inplace=True)
            job_sv = statevector_simulator.run(transpile(qctot, statevector_simulator))
            result_sv = job_sv.result()
            statevector = partial_trace(result_sv.get_statevector(), [0, 1, 3, 4]).to_statevector()
            circarr[10+j, :] = statevector
            qce.data.pop(1)
            qce.data.pop(0)

# add the last circuit which has no error
qctot = QuantumCircuit(5, 5)
qctot.compose(qc, inplace=True)
qctot.compose(qcd, inplace=True)
job_sv = statevector_simulator.run(transpile(qctot, statevector_simulator))
result_sv = job_sv.result()
statevector = partial_trace(result_sv.get_statevector(), [0, 1, 3, 4]).to_statevector()
circarr[-1, :] = statevector 

# generator to have fidelity run on every element of the list
fidarr = [fidelity(i, circarr[i], initial) for i in range(16)]
for i in range(16):
    print(fidarr[i])
