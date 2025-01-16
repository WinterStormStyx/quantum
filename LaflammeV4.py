#importing modules, probably way too many, however, im scared to delete any so please feel free to work on it
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import transpile
import qiskit.quantum_info as qi
from qiskit.quantum_info import SparsePauliOp, Statevector, partial_trace
from matplotlib import pyplot as plt
import numpy as np
from qiskit_aer import Aer

#fidelity is a function which has for input i, the index of the element, fidarr, the element at the specified index and inp, the reference input
#what it does is calculating the innerproduct, and compose a string indicating the test variant depending on the index.
#because there are 15 tests + 1 no error, every multiple of 5 until 10 (np.floor(i/5)) represents (bit, phase or flip of both), then the modulus indicates on what bit this flip has been performed
def fidelity(i, fidarr, inp):
    fid = float(np.dot(np.conj(fidarr.data), inp.data))**2
    div = np.floor(i/5)
    modu = np.mod(i, 5)
    st = ""
    if div == 0:
        st = "bit flip on bit " + str(modu)
    elif div == 1:
        st = "phase flip on bit " + str(modu)
    elif div == 2:
        st = "phase and bit flip on bit " + str(modu)
    elif i == 15:
        st = "no error"

    return [st, fid]
#Defining some gates by their matrix representation, theyre supposed to each correct their own type of error, which will be explained in the overleaf
#there are 5 types of error results that can be corrected
err1 = qi.Operator([[0, -1], [1, 0]])
err2 = qi.Operator([[-1, 0], [0, 1]])
err3 = qi.Operator([[1, 0], [0, -1]])
err4 = qi.Operator([[-1, 0], [0, -1]])
err5 = qi.Operator([[0, -1], [-1, 0]])

# Build a quantum circuit
#i need a quantum register of 5 qubits because i am encoding into 5 qubits
#i need a classical register of 4 bits because i need to measure 4 bits for the syndrome 
#encodecircuit
cl = ClassicalRegister(5)
qu = QuantumRegister(5)
qc = QuantumCircuit(qu, cl)
#decodecircuit
cld = ClassicalRegister(5)
qud = QuantumRegister(5)
qcd = QuantumCircuit(qud, cld)

#errorcircuit
cle = ClassicalRegister(5)
que = QuantumRegister(5)
qce = QuantumCircuit(que, cle)


#Visualize the encoding as a state Q encoded into a state abQcd, counting from qubit 0 (a) to qubit 4 (d). Our input state is qubit 2
# inp = Statevector([1/np.sqrt(2), 1/np.sqrt(2)])
inp = Statevector([1/np.sqrt(2), 1/np.sqrt(2)])
print("input: ", inp)
qc.initialize(inp, 2)

qc.initialize("0", 0)
qc.initialize("0", 1)
qc.initialize("0", 3)
qc.initialize("0", 4)


#this is the start of the encoding
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

# the entangled state now gets decoded

qcd.mcry(2*np.pi, [3, 4], 2)
qcd.cx(1, 4)

qcd.cx(3, 2)

qcd.cx(0, [2, 4])

qcd.cx(2, 4)

qcd.x([1, 3])
qcd.mcry(2*np.pi, [1, 2, 3], 4)
qcd.x([1, 3])

qcd.mcry(2*np.pi,[1, 2, 3], 4)

qcd.h([0, 1, 3])

#now, we need to to measure qubits a, b, c and d. This will collapse our state into a'b'Q'c'd'
#a'b'c'd' is our syndrome, and tells us what happened to our decoded state.
qcd.measure([0, 1, 3, 4], range(4))


#you can find a table in laflammes paper what happens for every S, B or BS error, they all produce some kind of flip on Q' which can be corrected
#For this, i compare the syndrome (in binary) to the value which pins down what correcting matrix needs to be applied. Qiskit reads in little endian!
#also, do not mess around with the order of the classical register, the register sets their classical bits to 0 by default, so i read the right binary value now even if i have one bit too much! (reserved for measuring Q)
#error type 1
qcd.unitary(err1, 2).c_if(cld, 11)

#error type 2
qcd.unitary(err2, 2).c_if(cld, 15)

#error type 3
qcd.unitary(err3, 2).c_if(cld, 8)
qcd.unitary(err3, 2).c_if(cld, 5)
qcd.unitary(err3, 2).c_if(cld, 3)
qcd.unitary(err3, 2).c_if(cld, 10)

#error type 4
qcd.unitary(err4, 2).c_if(cld, 12)
qcd.unitary(err4, 2).c_if(cld, 1)
qcd.unitary(err4, 2).c_if(cld, 2)
qcd.unitary(err4, 2).c_if(cld, 4)

#error type 5
qcd.unitary(err5, 2).c_if(cld, 6)
qcd.unitary(err5, 2).c_if(cld, 14)
qcd.unitary(err5, 2).c_if(cld, 13)
qcd.unitary(err5, 2).c_if(cld, 7)
qcd.unitary(err5, 2).c_if(cld, 9)

#building total circuit
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
#the last circuit is the circuit with no error
qctot = QuantumCircuit(5, 5)
qctot.compose(qc, inplace=True)
qctot.compose(qcd, inplace=True)
job_sv = statevector_simulator.run(transpile(qctot, statevector_simulator))
result_sv = job_sv.result()
statevector = partial_trace(result_sv.get_statevector(), [0, 1, 3, 4]).to_statevector()
circarr[-1, :] = statevector 

#generator to have fidelity run on every element of the list
fidarr = [fidelity(i, circarr[i], inp) for i in range(16)]
for i in range(16):
    print(fidarr[i])

#printing the results





# For execution
# job_sv = statevector_simulator.run(transpile(qc, statevector_simulator))
# result_sv = job_sv.result()
# statevector = partial_trace(result_sv.get_statevector(), [0, 1, 3, 4])
# statevector = partial_trace(result_sv.get_statevector(), [0, 1, 3, 4]).to_statevector()
# print(statevector)
