import mttkinter as tkinter # really dirty fix for a RunTime error you get when you add Aer for noise

from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from qiskit_ibm_runtime import EstimatorV2
from qiskit_ibm_runtime.fake_provider import FakeAlmadenV2

from matplotlib import pyplot as plt
import numpy as np

def shorEncoding(initial = "0", biterrors = None, phaseerrors = None, drawCircuit = False, drawStates = False):
    # """Creates the circuit for Shors Code with a given initial state and provided errors

    # Args:
    #     initial (str, optional): The initial state of qubit 0, can be "0" (default), "1", "+", "-", "l", "r".
    #     biterrors (list, optional): A list of qubits that have a bit flip. Defaults to None.
    #     phaseerrors (list, optional): A list of qubits that have a phase flip. Defaults to None.
    #     drawCircuit (bool, optional): If true, will draw the created circuit. Defaults to False.
    #     drawStates (bool, optional): If true, will draw the final states of the qubits on Bloch Spheres. Defaults to False.
    #                                  Note this is the one place where qubit 0 is labeled qubit 8 (reverse order numbering)

    # Returns:
    #     QuantumCircuit: the created quantum circuit
    # """
    # Build a quantum circuit
    qc = QuantumCircuit(9)

    qc.prepare_state(Statevector.from_label(initial + "0"*8), range(9))
 
    qc.cx(0, [3, 6])
    qc.h([0, 3, 6])
    qc.cx([0, 0, 3, 3, 6, 6], [1, 2, 4, 5, 7, 8])

    if drawCircuit: # Return a drawing of the circuit using MatPlotLib
        qc.draw("mpl")
        plt.show()

    if drawStates:
        psi = Statevector(qc)
        psi.draw("bloch")  # psi is a Statevector object
        plt.show()
    return qc

# logical1 = shorEncoding("0", drawCircuit=True)
# logical2 = shorEncoding("0", drawCircuit=True)

# def CNot(qc1,qc2):
#     qc = QuantumCircuit(18)
#     qc.compose(qc1, qubits=range(9), inplace=True)
#     qc.compose(qc2, qubits=range(9, 18), inplace=True)
#     for i in range(9):
#         qc.cz(i, i + 9)
#     qc.draw("mpl")
#     plt.show()
#     return qc
# Circuit = CNot(logical1, logical2)

def Not(qc1):
    qc = QuantumCircuit(9)
    qc.compose(qc1)
    for i in range(9):
        qc.z(i)
    qc.draw("mpl")
    plt.show()
    return qc

# Simple_Not_gate = Not(logical1)

def shorDecoding(qc, logical_qubit=0, drawCircuit=False):
    """
    Decodes a specific logical qubit from a circuit encoded using Shor's code.

    Args:
        qc (QuantumCircuit): The circuit containing one or more logical qubits encoded with Shor's code.
        logical_qubit (int, optional): Index of the logical qubit to decode (0 for the first, 1 for the second). Defaults to 0.
        drawCircuit (bool, optional): If True, draws the decoding circuit. Defaults to False.

    Returns:
        QuantumCircuit: The quantum circuit with decoding applied to the selected logical qubit.
    """
    # if logical_qubit not in [0, 1]:
    #     raise ValueError("logical_qubit must be 0 (first logical qubit) or 1 (second logical qubit).")
    
    # # Define the starting qubit range for decoding
    # start = logical_qubit * 9
    # decoding_circuit = QuantumCircuit((logical_qubit+1)*9)  # Create a circuit for 18 qubits

    # # Decoding steps for the logical qubit
    # decoding_circuit.cx([start, start, start + 3, start + 3, start + 6, start + 6], 
    #                     [start + 1, start + 2, start + 4, start + 5, start + 7, start + 8])
    # decoding_circuit.ccx([start + 1, start + 4,start + 7],[start + 2, start + 5, start + 8],[start, start + 3, start + 6])
    # decoding_circuit.h([start, start + 3, start + 6])
    # decoding_circuit.cx(start, [start + 3, start + 6])
    # decoding_circuit.ccx(start + 3, start + 6, start)

    # # Optionally draw the decoding circuit


    # # Apply decoding to the input circuit
    # qc.compose(decoding_circuit, inplace=True)
    # return qc
    qc = QuantumCircuit(9)
    qc.cx([0, 0, 3, 3, 6, 6], [1, 2, 4, 5, 7, 8])
    qc.ccx([1, 4, 7], [2, 5, 8], [0, 3, 6])
    qc.h([0, 3, 6])
    qc.cx(0, [3, 6])
    qc.ccx(3, 6, 0)

    if drawCircuit:
        qc.draw("mpl")
        plt.show()
    return qc



# decoding = shorDecoding(logical1,logical_qubit= 0, drawCircuit= True)

def measurement(qc, measurement_basis = "Z", num_trials = 10):
    """Runs a quantum circuit using simulation and then measures the output (with noise), showing a plot of it.

    Args:
        qc (QuantumCircuit): The quantum circuit being measured
        measurement_basis (str, optional): The basis in which measurement should occur. Defaults to "Z".
        num_trials (int, optional): How many times the simulation and measurement should be repeated. Defaults to 10.
    """
    # observables_labels = [i*"I" + measurement_basis + (8-i)*"I" for i in range(1)]
    observables_labels = [8*"I" + measurement_basis ]
    observables = [SparsePauliOp(label) for label in observables_labels]
    
    # Set up code to run on simulator 
    backend = FakeAlmadenV2()
    estimator = EstimatorV2(backend)
    
    # Convert to an ISA circuit and draw this
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_circuit = pm.run(qc)
    
    # layout-mapped observables
    mapped_observables = [observable.apply_layout(isa_circuit.layout) for observable in observables]
    
    # Run it
    job = estimator.run([(isa_circuit, mapped_observables)] * num_trials)
    
    values = list(map(lambda pub_result: pub_result.data.evs, job.result()))
    errors = list(map(lambda pub_result: pub_result.data.stds, job.result()))
    
    # plotting graph
    for i in range(num_trials):
        plt.errorbar(observables_labels, values[i], yerr=errors[i], fmt="o", label=i)

    plt.xlabel("Observables")
    plt.ylabel("Values")
    #plt.legend()
    plt.show()
    

# Lets see what happens when we add a bunch of random gates and try to measure

for i in range(1):
    # biterrors = np.random.randint(0, 9, size=np.random.randint(1, 9, size=1))
    # phaseerrors = np.random.randint(0, 9, size=np.random.randint(1, 9, size=1))

    encode = shorEncoding(initial ="0",drawCircuit= True)
    flip = Not(encode)
    qc = shorDecoding(flip, drawCircuit=True)
    measurement(qc, measurement_basis="Z")

