# This version works with counting states -- it should be functional!

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import transpile
import qiskit.quantum_info as qi
import numpy as np
from qiskit_aer import AerSimulator

from Basis import Basis

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

#Defining some gates by their matrix representation, they're supposed to each correct their own type of error
#there are 5 types of error results that can be corrected
err1 = qi.Operator([[0, -1], [1, 0]])
err2 = qi.Operator([[-1, 0], [0, 1]])
err3 = qi.Operator([[1, 0], [0, -1]])
err4 = qi.Operator([[-1, 0], [0, -1]])
err5 = qi.Operator([[0, -1], [-1, 0]])


def laflamme(inp, biterror=None, phaseerror=None):
    """Make the laflamme circuit

    Args:
        inp (Statevector or str): the input of the qubit. Can be "0", "1", "+", "-" or any Statevector object.
        biterror (int, optional): qubit to apply bit error to. Defaults to None.
        phaseerror (int, optional): qubit to apply phase error to. Defaults to None.

    Returns:
        QuantumCircuit: the built circuit
    """
    # Build a quantum circuit
    #I need a quantum register of 5 qubits because I am encoding into 5 qubits
    #I need a classical register of 4 bits because I need to measure 4 bits for the syndrome 
    cl = ClassicalRegister(5)
    qu = QuantumRegister(5)
    qc = QuantumCircuit(qu, cl)

    #Visualize the encoding as a state Q encoded into a state abQcd, counting from qubit 0 (a) to qubit 4 (d). Our input state is qubit 2
    qc.initialize(inp, 2)
    qc.initialize("0", 0)
    qc.initialize("0", 1)
    qc.initialize("0", 3)
    qc.initialize("0", 4)


    # encoding
    qc.h([0, 1, 3])
    qc.mcry(2*np.pi,[1, 2, 3], 4)
    qc.x([1, 3])
    qc.mcry(2*np.pi, [1, 2, 3], 4)
    qc.x([1, 3])
    qc.cx([2, 0, 0, 3, 1], [4, 2, 4, 2, 4])
    qc.mcry(2*np.pi, [3, 4], 2)

    # error can occur here
    if biterror is not None:
        qc.x(biterror)
    if phaseerror is not None:
        qc.z(phaseerror)
    # --------------------

    # decoding
    qc.mcry(2*np.pi, [3, 4], 2)
    qc.cx([1, 3, 0, 0, 2], [4, 2, 2, 4, 4])
    qc.x([1, 3])
    qc.mcry(2*np.pi, [1, 2, 3], 4)
    qc.x([1, 3])
    qc.mcry(2*np.pi,[1, 2, 3], 4)
    qc.h([0, 1, 3])

    #now, we need to to measure qubits a, b, c and d. This will collapse our state into a'b'Q'c'd'
    #a'b'c'd' is our syndrome, and tells us what happened to our decoded state.
    qc.measure([0, 1, 3, 4], range(4))


    #you can find a table in laflammes paper what happens for every S, B or BS error, they all produce some kind of flip on Q' which can be corrected
    #For this, I compare the syndrome (in binary) to the value which pins down what correcting matrix needs to be applied. Qiskit reads in little endian!
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
    
    return qc

def measure(qc, basis: Basis, shots=1000):
    """Measure the different states the circuit could be in

    Args:
        qc (QuanutmCircuit): the circuit to be measured
        basis (Basis): the basis in which measurement should happen
        shots (int, optional): How many shots to measure. Defaults to 1000.

    Returns:
        dict: count of how many times different states were measured
    """
    #now we measure our corrected qubit 2
    if basis == Basis.X:
        qc.h(2)
    qc.measure(2, 4)

    #here comes the tricky part, this simulator works by counting states
    simulator = AerSimulator()
    compiled_circuit = transpile(qc, simulator)
    job = simulator.run(compiled_circuit, shots=shots)
    sim_result = job.result().get_counts()
    
    if basis == Basis.Z:
        return sim_result

    # if measuring in X basis, make sure the output state is either a "+" or "-"
    d = {}
    for (k, val) in sim_result.items():
            d[k.replace("0", "+", 1) if k[0] == "0" else k.replace("1", "-", 1)] = val
    return d
