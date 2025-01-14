
#Hey Em, ive taken your code and tried to implement the 5 qubit error correction, the trouble im having is the inbuilt noise model that seems to be messing with the decoding.
#Right now im trying to see if adding waiting gates for unused qubits offers fidelity increase
import mttkinter as tkinter # really dirty fix for a RunTime error you get when you add Aer for noise
from qiskit import QuantumCircuit, transpile, ClassicalRegister, QuantumRegister
#from qiskit_aer import Aer

from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import qiskit.quantum_info as qi
from qiskit_ibm_runtime import EstimatorV2
from qiskit_ibm_runtime.fake_provider import FakeAlmadenV2

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
    err1 = qi.Operator([[0, -1], [1, 0]])
    err2 = qi.Operator([[-1, 0], [0, 1]])
    err3 = qi.Operator([[1, 0], [0, -1]])
    err4 = qi.Operator([[-1, 0], [0, -1]])
    err5 = qi.Operator([[0, -1], [-1, 0]])

    # Build a quantum circuit
    cl = ClassicalRegister(4)
    qu = QuantumRegister(5)
    qc = QuantumCircuit(qu, cl)

    qc.prepare_state(initial, 2)
    qc.prepare_state("0", 0)
    qc.prepare_state("0", 1)
    qc.prepare_state("0", 3)
    qc.prepare_state("0", 4)
    
    qc.h([0, 1, 3])

    qc.id([2, 4])

    qc.mcry(2*np.pi,[1, 2, 3], 4)

    qc.id(0)

    qc.x([1, 3])
    qc.mcry(2*np.pi, [1, 2, 3], [4])
    qc.x([1, 3])

    qc.cx(2, 4)

    qc.cx(0, [2, 4])

    qc.cx(3, 2)

    qc.cx(1, 4)
    qc.mcry(2*np.pi, [3, 4], [2])
    #flipping
    
    # ERROR CAN OCCUR HERE
    if biterrors is not None:
        qc.x(biterrors)
    if phaseerrors is not None:
        qc.z(phaseerrors)
    # --------------------

    #decoding
    qc.mcry(2*np.pi, [3, 4], [2])
    qc.cx(1, 4)

    qc.cx(3, 2)

    qc.cx(0, [2, 4])

    qc.cx(2, 4)

    qc.x([1, 3])
    qc.mcry(2*np.pi, [1, 2, 3], [4])
    qc.x([1, 3])

    qc.mcry(2*np.pi,[1, 2, 3], [4])

    qc.h([0, 1, 3])

    # #measuring and storing syndrome
    qc.measure([0, 1, 3, 4], range(4))
    
    #error type 1
    qc.unitary(err1, 2).c_if(cl, 13)

    #error type 2
    qc.unitary(err2, 2).c_if(cl, 15)

    #error type 3
    qc.unitary(err3, 2).c_if(cl, 1)
    qc.unitary(err3, 2).c_if(cl, 10)
    qc.unitary(err3, 2).c_if(cl, 12)
    qc.unitary(err3, 2).c_if(cl, 5)

    #error type 4
    qc.unitary(err4, 2).c_if(cl, 3)
    qc.unitary(err4, 2).c_if(cl, 8)
    qc.unitary(err4, 2).c_if(cl, 4)
    qc.unitary(err4, 2).c_if(cl, 2)

    #error type 5
    qc.unitary(err5, 2).c_if(cl, 6)
    qc.unitary(err5, 2).c_if(cl, 7)
    qc.unitary(err5, 2).c_if(cl, 11)
    qc.unitary(err5, 2).c_if(cl, 14)
    qc.unitary(err5, 2).c_if(cl, 9)

    


    # ERROR CAN OCCUR HERE
    if biterrors is not None:
        qc.x(biterrors)
    if phaseerrors is not None:
        qc.z(phaseerrors)
    # --------------------

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
    # observables_labels = [i*"I" + measurement_basis + (4-i)*"I" for i in range(5)]
    observables_labels = ["IIZII", "IIXII"]
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
biterrors = np.random.randint(0, 9, size=np.random.randint(1, 9, size=1))
phaseerrors = np.random.randint(0, 9, size=np.random.randint(1, 9, size=1))

qc = Laflamme(initial = "0", biterrors=None, phaseerrors=None, drawStates=True, drawCircuit=True)
measurement(qc, measurement_basis="Z")

