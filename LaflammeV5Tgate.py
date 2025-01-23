#importing modules, probably way too many, however, im scared to delete any so please feel free to work on it
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import transpile
from qiskit.providers.basic_provider import BasicSimulator
import qiskit.quantum_info as qi
from qiskit.quantum_info import SparsePauliOp, Statevector
from matplotlib import pyplot as plt
import numpy as np
from qiskit_aer import AerSimulator


#tgate
Tgate = QuantumCircuit(5, 0)

Tgate.mcp(np.pi/4, [0, 1, 3, 4], 2, ctrl_state="1111")
Tgate.mcp(np.pi/4, [0, 1, 3, 4], 2, ctrl_state="0010")
Tgate.mcp(np.pi/4, [0, 1, 3, 4], 2, ctrl_state="1000")
Tgate.mcp(np.pi/4, [0, 1, 3, 4], 2, ctrl_state="0101")

Tgate.x(2)
Tgate.mcp(np.pi/4, [0, 1, 3, 4], 2, ctrl_state="0110")
Tgate.mcp(np.pi/4, [0, 1, 3, 4], 2, ctrl_state="1011")
Tgate.mcp(np.pi/4, [0, 1, 3, 4], 2, ctrl_state="0001")
Tgate.mcp(np.pi/4, [0, 1, 3, 4], 2, ctrl_state="1100")
Tgate.x(2)

T = Tgate.to_gate()


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
cl = ClassicalRegister(5)
qu = QuantumRegister(5)
qc = QuantumCircuit(qu, cl)

#Visualize the encoding as a state Q encoded into a state abQcd, counting from qubit 0 (a) to qubit 4 (d). Our input state is qubit 2
inp = [1/np.sqrt(2), 1/np.sqrt(2)]
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

#Tgate happens twice



qc.append(T, [0, 1, 2, 3, 4])
qc.append(T, [0, 1, 2, 3, 4])




# qc.measure(range(5), range(5))
# the entangled state now gets decoded

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







#now, we need to to measure qubits a, b, c and d. This will collapse our state into a'b'Q'c'd'
#a'b'c'd' is our syndrome, and tells us what happened to our decoded state.
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

#now we measure our corrected qubit 2
qc.sdg(2)
qc.h(2)
qc.measure(2, 4)

#here comes the tricky part, this simulator works by counting states, it runs the circuit 10000 times. I now implemented input states : 0, 1, + and -, more will come later

# For execution
simulator = AerSimulator()
compiled_circuit = transpile(qc, simulator)



job = simulator.run(compiled_circuit, shots=10000)
sim_result = job.result()
counts = sim_result.get_counts()
print("Printed State : 0/1|syndrome in reverse order")
print(counts)

