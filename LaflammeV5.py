#welcome to laflammeV5. This script is stilll being extended. However, not gate and hadamard gate are working now on laflammes code 
import mttkinter as tkinter # really dirty fix for a RunTime error you get when you add Aer for noise

from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from qiskit_ibm_runtime import EstimatorV2
from qiskit_ibm_runtime.fake_provider import FakeAlmadenV2, FakeAlgiers

#importing modules, probably way too many, however, im scared to delete any so please feel free to work on it
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import transpile
import qiskit.quantum_info as qi
from qiskit.quantum_info import SparsePauliOp, Statevector, partial_trace
from matplotlib import pyplot as plt
import numpy as np
from qiskit_aer import Aer


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
qu = QuantumRegister(5)
qc = QuantumCircuit(qu, cl)

#Visualize the encoding as a state Q encoded into a state abQcd, counting from qubit 0 (a) to qubit 4 (d). Our input state is qubit 2
#logical qubit 1
inp1 = Statevector([1, 0])
qc.initialize(inp1, 2)

qc.initialize("0", 0)
qc.initialize("0", 1)
qc.initialize("0", 3)
qc.initialize("0", 4)

# #init ancilla qubit
# qc.initialize("0", 5)

# #logical qubit 2
# inp2 = Statevector([0, 1])
# qc.initialize(inp2, 6)

# qc.initialize("0", 7)
# qc.initialize("0", 8)
# qc.initialize("0", 9)
# qc.initialize("0", 10)

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

#Hadamard
hadgate = QuantumCircuit(5, 0)

hadgate.x([0, 1, 2])
hadgate.ccx(3, 4, 0, ctrl_state='00')
hadgate.ccx(3, 4, 0, ctrl_state='11')

hadgate.ccz(3, 4, 0, ctrl_state='01')
hadgate.ccz(3, 4, 0, ctrl_state='10')

hadgate.h(0) 

HAD = hadgate.to_gate()

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
qc.append(HAD, [0, 1, 2, 3, 4])
qc.append(DEC, [0, 1, 2, 3, 4])

#now, we need to to measure qubits a, b, c and d. This will collapse our state into a'b'Q'c'd'
#a'b'c'd' is our syndrome, and tells us what happened to our decoded state.
#need to change cl to classical register of errorcorrecting code
qc.measure([0, 1, 3, 4], range(4))


#you can find a table in laflammes paper what happens for every S, B or BS error, they all produce some kind of flip on Q' which can be corrected
#For this, i compare the syndrome (in binary) to the value which pins down what correcting matrix needs to be applied. Qiskit reads in little endian!
#also, do not mess around with the order of the classical register, the register sets their classical bits to 0 by default, so i read the right binary value now even if i have one bit too much! (reserved for measuring Q)
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

statevector_simulator = Aer.get_backend('statevector_simulator')
job_sv = statevector_simulator.run(transpile(qc, statevector_simulator))
result_sv = job_sv.result()
statevector = partial_trace(result_sv.get_statevector(), [0, 1, 3, 4])
statevector = partial_trace(result_sv.get_statevector(), [0, 1, 3, 4]).to_statevector()
print(statevector)