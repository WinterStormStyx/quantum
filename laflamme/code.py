from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
import qiskit.quantum_info as qi
import numpy as np

#Defining some gates by their matrix representation, they're supposed to each correct their own type of error
#there are 5 types of error results that can be corrected
err1 = qi.Operator([[0, -1], [1, 0]])
err2 = qi.Operator([[-1, 0], [0, 1]])
err3 = qi.Operator([[1, 0], [0, -1]])
err4 = qi.Operator([[-1, 0], [0, -1]])
err5 = qi.Operator([[0, -1], [-1, 0]])

def laflamme(initial, biterror=None, phaseerror=None):
    """Make the laflamme circuit

    Args:
        initial (Statevector or str): the input of the qubit. Can be "0", "1", "+", "-" or any Statevector object.
        biterror (int, optional): qubit to apply bit error to. Defaults to None.
        phaseerror (int, optional): qubit to apply phase error to. Defaults to None.

    Returns:
        QuantumCircuit: the built circuit
    """
    # construct the quantum and classical registers for the circuit
    cl = ClassicalRegister(5)
    qu = QuantumRegister(5)
    qc = QuantumCircuit(qu, cl)
    
    qc = encode(qc, initial=initial)

    # error can occur here
    if biterror is not None:
        qc.x(biterror)
    if phaseerror is not None:
        qc.z(phaseerror)
    # --------------------

    qc = decode(qc, cl)

    return qc

def encode(qc, initial):
    """Creates the encoding part of Laflamme's Code with a given initial state

    Args:
        qc (QuantumCircuit): the quantum circuit so far that should now be encoded
        initial (str, optional): The initial state of qubit 0, can be "0" (default), "1", "+", "-", "l", "r", or 
                                 any other Statevector.

    Returns:
        QuantumCircuit: the created quantum circuit
    """

    # Visualize the encoding as a state Q encoded into a state abQcd, counting from qubit 0 (a) to qubit 4 (d). 
    qc.initialize(initial, 2)
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
    
    return qc

def decode(qc, cl, base=0):
    """Creates the decoding part of Laflamme's code

    Args:
        qc (QuantumCircuit): the quantum circuit so far that should now be decoded
        cl (ClassicalRegister): the register of classical qubits to measure to
        base (int): the index of the first physical qubit in the logical qubit (defaul 0)

    Returns:
        QuantumCircuit: the circuit with the decoding section added
    """
    
    # decoding
    qc.mcry(2*np.pi, [base+3, base+4], base+2)
    qc.cx([base+1, base+3, base+0, base+0, base+2], [base+4, base+2, base+2, base+4, base+4])
    qc.x([base+1, base+3])
    qc.mcry(2*np.pi, [base+1, base+2, base+3], base+4)
    qc.x([base+1, base+3])
    qc.mcry(2*np.pi,[base+1, base+2, base+3], base+4)
    qc.h([base+0, base+1, base+3])

    #now, we need to to measure qubits a, b, c and d. This will collapse our state into a'b'Q'c'd'
    #a'b'c'd' is our syndrome, and tells us what happened to our decoded state.
    qc.measure([base+0, base+1, base+3, base+4], range(4))


    #you can find a table in laflammes paper what happens for every S, B or BS error, they all produce some kind of flip on Q' which can be corrected
    #For this, I compare the syndrome (in binary) to the value which pins down what correcting matrix needs to be applied. Qiskit reads in little endian!
    #also, do not mess around with the order of the classical register, the register sets their classical bits to 0 by default, so i read the right binary value now even if i have one bit too much! (reserved for measuring Q)
    #error type 1
    qc.unitary(err1, base+2).c_if(cl, 11)

    #error type 2
    qc.unitary(err2, base+2).c_if(cl, 15)

    #error type 3
    qc.unitary(err3, base+2).c_if(cl, 8)
    qc.unitary(err3, base+2).c_if(cl, 5)
    qc.unitary(err3, base+2).c_if(cl, 3)
    qc.unitary(err3, base+2).c_if(cl, 10)

    #error type 4
    qc.unitary(err4, base+2).c_if(cl, 12)
    qc.unitary(err4, base+2).c_if(cl, 1)
    qc.unitary(err4, base+2).c_if(cl, 2)
    qc.unitary(err4, base+2).c_if(cl, 4)

    #error type 5
    qc.unitary(err5, base+2).c_if(cl, 6)
    qc.unitary(err5, base+2).c_if(cl, 14)
    qc.unitary(err5, base+2).c_if(cl, 13)
    qc.unitary(err5, base+2).c_if(cl, 7)
    qc.unitary(err5, base+2).c_if(cl, 9)
    
    return qc
