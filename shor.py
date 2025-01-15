import mttkinter as tkinter # really dirty fix for a RunTime error you get when you add Aer for noise

from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from qiskit_ibm_runtime import EstimatorV2
from qiskit_ibm_runtime.fake_provider import FakeAlmadenV2

from matplotlib import pyplot as plt
import numpy as np


def shorCode(initial = "0", biterrors = None, phaseerrors = None, drawCircuit = False, drawStates = False):
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
    qc = QuantumCircuit(9)

    qc.prepare_state(Statevector.from_label(initial + "0"*8), range(9))
 
    qc.cx(0, [3, 6])
    qc.h([0, 3, 6])
    qc.cx([0, 0, 3, 3, 6, 6], [1, 2, 4, 5, 7, 8])

    # ERROR CAN OCCUR HERE
    if biterrors is not None:
        qc.x(biterrors)
    if phaseerrors is not None:
        qc.z(phaseerrors)
    # --------------------

    qc.cx([0, 0, 3, 3, 6, 6], [1, 2, 4, 5, 7, 8])
    qc.ccx([1, 4, 7], [2, 5, 8], [0, 3, 6])
    qc.h([0, 3, 6])
    qc.cx(0, [3, 6])
    qc.ccx(3, 6, 0)

    if drawCircuit: # Return a drawing of the circuit using MatPlotLib
        qc.draw("mpl")
        plt.show()

    if drawStates:
        psi = Statevector(qc)
        psi.draw("bloch")  # psi is a Statevector object
        plt.show()
    
    return qc


def measurement(qc, measurement_basis = "Z", num_trials = 10):
    """Runs a quantum circuit using simulation and then measures the output (with noise), showing a plot of it.

    Args:
        qc (QuantumCircuit): The quantum circuit being measured
        measurement_basis (str, optional): The basis in which measurement should occur. Defaults to "Z".
        num_trials (int, optional): How many times the simulation and measurement should be repeated. Defaults to 10.
    """
    observables_labels = [i*"I" + measurement_basis + (8-i)*"I" for i in range(9)]
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
    

for i in range(4):
    bit = np.random.randint(0, 9, size=1) # find a bit for errors

    qc = shorCode("0", biterrors=bit, phaseerrors=bit, drawCircuit=True, drawStates=True)
    measurement(qc, measurement_basis="Z")

