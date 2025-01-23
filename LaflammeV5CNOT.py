#importing modules, probably way too many, however, im scared to delete any so please feel free to work on it
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import transpile
from qiskit.providers.basic_provider import BasicSimulator
import qiskit.quantum_info as qi
from qiskit.quantum_info import SparsePauliOp, Statevector
from matplotlib import pyplot as plt
import numpy as np
from qiskit_aer import AerSimulator


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
#i added an extra qubit for the hadamard gate.
cl = ClassicalRegister(4)
cl1 = ClassicalRegister(4)
res = ClassicalRegister(2)
anc = ClassicalRegister(1)
qu = QuantumRegister(11)
qc = QuantumCircuit(qu, cl, cl1, res, anc)

#Visualize the encoding as a state Q encoded into a state abQcd, counting from qubit 0 (a) to qubit 4 (d). Our input state is qubit 2
#logical qubit 1
inp1 = Statevector([1/np.sqrt(2),1/np.sqrt(2)])
qc.initialize(inp1, 2)

qc.initialize("0", 0)
qc.initialize("0", 1)
qc.initialize("0", 3)
qc.initialize("0", 4)

#init ancilla qubit
qc.initialize("0", 5)

#logical qubit 2
inp2 = Statevector([1, 0])
qc.initialize(inp2, 8)

qc.initialize("0", 6)
qc.initialize("0", 7)
qc.initialize("0", 9)
qc.initialize("0", 10)

#this is the start of the encoding

enc = QuantumCircuit(5,0)

enc.h([0, 1, 3])
enc.mcry(2*np.pi,[1, 2, 3], 4)
enc.x([1, 3])
enc.mcry(2*np.pi, [1, 2, 3], 4)
enc.x([1, 3])
enc.cx(2, 4)
enc.cx(0, [2, 4])
enc.cx(3, 2)
enc.cx(1, 4)
enc.mcry(2*np.pi, [3, 4], 2)

ENC = enc.to_gate()

#NOT gate build
notgate = QuantumCircuit(5, 0)
notgate.x(0)
notgate.z(0)
notgate.x(0)
notgate.x([3, 4])
NOT = notgate.to_gate()
CNOT = NOT.control(1)

#CNOT
cnotx = QuantumCircuit(11)
cnotx.mcx([0, 1, 2, 3, 4], 5, ctrl_state='11000')
cnotx.mcx([0, 1, 2, 3, 4], 5, ctrl_state='11111')
cnotx.mcx([0, 1, 2, 3, 4], 5, ctrl_state='00001')
cnotx.mcx([0, 1, 2, 3, 4], 5, ctrl_state='00110')
cnotx.mcx([0, 1, 2, 3, 4], 5, ctrl_state='01010')
cnotx.mcx([0, 1, 2, 3, 4], 5, ctrl_state='01101')
cnotx.mcx([0, 1, 2, 3, 4], 5, ctrl_state='10011')
cnotx.mcx([0, 1, 2, 3, 4], 5, ctrl_state='10100')
cnotx.append(CNOT, [5, 6, 7, 8, 9, 10])

CNOTX = cnotx.to_gate()




# the entangled state now gets decoded

dec = QuantumCircuit(5, 0)
dec.mcry(2*np.pi, [3, 4], 2)
dec.cx(1, 4)
dec.cx(3, 2)
dec.cx(0, [2, 4])
dec.cx(2, 4)
dec.x([1, 3])
dec.mcry(2*np.pi, [1, 2, 3], 4)
dec.x([1, 3])
dec.mcry(2*np.pi,[1, 2, 3], 4)
dec.h([0, 1, 3])

DEC = dec.to_gate()

#Circuit building
qc.append(ENC, [0, 1, 2, 3, 4])
qc.append(ENC, [6, 7, 8, 9, 10])

qc.append(CNOTX, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])


qc.append(DEC, [0, 1, 2, 3, 4])
qc.append(DEC, [6, 7, 8, 9, 10])

#now, we need to to measure qubits a, b, c and d. This will collapse our state into a'b'Q'c'd'
#a'b'c'd' is our syndrome, and tells us what happened to our decoded state.
#need to change cl to classical register of errorcorrecting code
qc.measure([0, 1, 3, 4], cl)
qc.measure([6, 7, 9, 10], cl1)

#you can find a table in laflammes paper what happens for every S, B or BS error, they all produce some kind of flip on Q' which can be corrected
#For this, i compare the syndrome (in binary) to the value which pins down what correcting matrix needs to be applied. Qiskit reads in little endian!
#also, do not mess around with the order of the classical register, the register sets their classical bits to 0 by default, so i read the right binary value now even if i have one bit too much! (reserved for measuring Q)
#error correciom logical qubit 1
#error type 1
qc.unitary(err1, 2).c_if(cl, 11)

#error type 2
qc.unitary(err2, 2).c_if(cl, 15)

#error type 3
qc.unitary(err3, 2).c_if(cl, 8)
qc.unitary(err3, 2).c_if(cl, 5)
qc.unitary(err3, 2).c_if(cl, 3)
qc.unitary(err3, 2).c_if(cl, 10)

#error type 4
qc.unitary(err4, 2).c_if(cl, 12)
qc.unitary(err4, 2).c_if(cl, 1)
qc.unitary(err4, 2).c_if(cl, 2)
qc.unitary(err4, 2).c_if(cl, 4)

#error type 5
qc.unitary(err5, 2).c_if(cl, 6)
qc.unitary(err5, 2).c_if(cl, 14)
qc.unitary(err5, 2).c_if(cl, 13)
qc.unitary(err5, 2).c_if(cl, 7)
qc.unitary(err5, 2).c_if(cl, 9)

#-----------------------------

#error correciom logical qubit 1
#error type 1
qc.unitary(err1, 8).c_if(cl1, 11)

#error type 2
qc.unitary(err2, 8).c_if(cl1, 15)

#error type 3
qc.unitary(err3, 8).c_if(cl1, 8)
qc.unitary(err3, 8).c_if(cl1, 5)
qc.unitary(err3, 8).c_if(cl1, 3)
qc.unitary(err3, 8).c_if(cl1, 10)

#error type 4
qc.unitary(err4, 8).c_if(cl1, 12)
qc.unitary(err4, 8).c_if(cl1, 1)
qc.unitary(err4, 8).c_if(cl1, 2)
qc.unitary(err4, 8).c_if(cl1, 4)

#error type 5
qc.unitary(err5, 8).c_if(cl1, 6)
qc.unitary(err5, 8).c_if(cl1, 14)
qc.unitary(err5, 8).c_if(cl1, 13)
qc.unitary(err5, 8).c_if(cl1, 7)
qc.unitary(err5, 8).c_if(cl1, 9)

qc.measure([2, 8], res)
qc.measure(5, anc)

# For execution
simulator = AerSimulator()
compiled_circuit = transpile(qc, simulator)



job = simulator.run(compiled_circuit, shots=10000)
sim_result = job.result()
counts = sim_result.get_counts()
print("ancilla register - L2L1 - syndrome 2 reverse - syndrome 1 reverse")
print(counts)

