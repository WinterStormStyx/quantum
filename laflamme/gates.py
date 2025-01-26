from qiskit import QuantumCircuit, QuantumRegister
import numpy as np


def hadamard(qc):
    """Hadamard gate on Laflamme encoded circuit

    Args:
        qc (QuantumCircuit): the circuit to apply the gate to

    Returns:
        QuantumCircuit: the circuit with an added hadamard gate
    """
    qc.x([0, 1, 2])
    qc.ccx(3, 4, 0, ctrl_state='00')
    qc.ccx(3, 4, 0, ctrl_state='11')

    qc.ccz(3, 4, 0, ctrl_state='01')
    qc.ccz(3, 4, 0, ctrl_state='10')

    qc.h(0) 
    
    return qc

def cnot(qc1, cl1, qc2, cl2, res, anc):
    """Applying a CNOT gate to two logical qubits

    Args:
        qc1 (QuantumCircuit): quantum circuit of control qubit
        cl1 (ClassicalRegister): classical register of control qubit
        qc2 (QuantumCircuit): quantum circuit of target qubit
        cl2 (ClassicalRegister): classical register of target qubit
        res (ClassicalRegister): classical register of result 
        anc (ClassicalRegister): classical register of ancilla qubit

    Returns:
        QunatumCircuit: the resulting quantum circuit
    """
    qc = QuantumCircuit(QuantumRegister(11), cl1, cl2, res, anc)
    
    qc.initialize("0", 5)
    qc = qc.compose(qc1, [0, 1, 2, 3, 4])
    qc = qc.compose(qc2, [6, 7, 8, 9, 10])
    
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
    
    qc.append(CNOTX, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    
    return qc
    
def t(qc):
    """Applying a T rotation gate to a logical qubit

    Args:
        qc (QunatumCircuit): the circuit of the logical qubit

    Returns:
        QuantumCircuit: the resulting circuit after the T gate was applied
    """
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
    
    qc.append(T, [0, 1, 2, 3, 4])
    
    return qc

