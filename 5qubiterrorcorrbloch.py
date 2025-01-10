
#Hey Em, ive taken your code and tried to implement the 5 qubit error correction, the trouble im having is the inbuilt noise model that seems to be messing with the decoding.
#Right now im trying to see if adding waiting gates for unused qubits offers fidelity increase
import mttkinter as tkinter # really dirty fix for a RunTime error you get when you add Aer for noise
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from qiskit_ibm_runtime import EstimatorV2
from qiskit_ibm_runtime.fake_provider import FakeQuebec

from matplotlib import pyplot as plt
import numpy as np


def Laflamme(initial = "0", biterrors = None, phaseerrors = None, drawCircuit = False, drawStates = False):
    """Creates the circuit for Shors Code with a given initial state and provided errors

    Args:
        initial (str, optional): The initial state of qubit 0, can be "0" (default), "1", "+", "-", "l", "r".
        biterrors (list, optional): A list of qubits that have a bit flip. Defaults to None.
        phaseerrors (list, optional): A list of qubits that have a phase flip. Defaults to None.
        drawCircuit (bool, optional): If true, will draw the created circuit. Defaults to False.
        drawStates (bool, optional): If true, will draw the final states of the qubits on Bloch Spheres. Defaults to False.
                                     Note this is the one place where qubit 0 is labeled qubit 8 (reverse order numbering)

    Returns:
        QuantumCircuit: the created quantum circuit
    """
    # Build a quantum circuit
    qc = QuantumCircuit(5)

    qc.prepare_state(initial, 2)
    qc.prepare_state("0", 0)
    qc.prepare_state("0", 1)
    qc.prepare_state("0", 3)
    qc.prepare_state("0", 4)
    
    qc.h([0, 1, 3])

    qc.id([2, 4])

    qc.mcp(np.pi,[1, 2, 3], 4)

    qc.id(0)

    qc.x([1, 3])
    qc.mcp(np.pi, [1, 2, 3], 4)
    qc.x([1, 3])

    qc.cx(2, 4)

    qc.cx(0, [2, 4])

    qc.cx(3, 2)

    qc.cx(1, 4)
    qc.mcp(np.pi, [3, 4], 2)

    # ERROR CAN OCCUR HERE
    if biterrors is not None:
        qc.x(biterrors)
    if phaseerrors is not None:
        qc.z(phaseerrors)
    # --------------------

    #decoding
    qc.mcp(np.pi, [3, 4], 2)
    qc.cx(1, 4)

    qc.cx(3, 2)

    qc.cx(0, [2, 4])

    qc.cx(2, 4)

    qc.x([1, 3])
    qc.mcp(np.pi, [1, 2, 3], 4)
    qc.x([1, 3])

    qc.mcp(np.pi,[1, 2, 3], 4)

    qc.h([0, 1, 3])
    
    qc.swap(2, 4)

    if drawCircuit: # Return a drawing of the circuit using MatPlotLib
        qc.draw("mpl")
        plt.show()
        
    if drawStates:
        psi = Statevector(qc)
        psi.draw("bloch")  # psi is a Statevector object
        plt.show()
    
    return qc


def measurement(qc, measurement_basis = "Z", num_trials = 1):
    """Runs a quantum circuit using simulation and then measures the output (with noise), showing a plot of it.

    Args:
        qc (QuantumCircuit): The quantum circuit being measured
        measurement_basis (str, optional): The basis in which measurement should occur. Defaults to "Z".
        num_trials (int, optional): How many times the simulation and measurement should be repeated. Defaults to 10.
    """
    observables_labels = [i*"I" + measurement_basis + (4-i)*"I" for i in range(5)]
    observables = [SparsePauliOp(label) for label in observables_labels]
    
    # Set up code to run on simulator 
    backend = FakeQuebec()
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
    plt.legend()
    plt.show()

    # simulator = Aer.get_backend('statevector_simulator')
    # new_circuit = transpile(qc, simulator)
    # job = simulator.run(new_circuit)
    # statevector_result = job.result()
    # statevector = statevector_result.get_statevector()

    # Print the statevector
    # print("Statevector:", statevector)

    # Plot Bloch sphere representation of the statevector
    # psi = Statevector(statevector)
    # psi.draw('bloch')
    # plt.show()
    

# Lets see what happens when we add a bunch of random gates and try to measure

for i in range(1):
    biterrors = [2] # np.random.randint(0, 5, size=np.random.randint(1, 5, size=1))
    phaseerrors = None #np.random.randint(0, 5, size=np.random.randint(1, 5, size=1))
    
    qc = Laflamme(initial = "1", biterrors=biterrors, phaseerrors=phaseerrors, drawStates=True, drawCircuit=True)
    measurement(qc, measurement_basis="Z")
    