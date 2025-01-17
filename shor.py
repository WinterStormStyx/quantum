import mttkinter as tkinter # really dirty fix for a RunTime error you get when you add Aer for noise

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from qiskit_ibm_runtime import EstimatorV2
from qiskit_ibm_runtime.fake_provider import FakeAlmadenV2

from qiskit_aer import AerSimulator
from Basis import Basis

from matplotlib import pyplot as plt

def shor(initial = "0", biterrors = None, phaseerrors = None, drawCircuit = False, drawStates = False):
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
    
    qc = shorEncode(initial)
    
    # ERROR CAN OCCUR HERE
    if biterrors is not None:
        qc.x(biterrors)
    if phaseerrors is not None:
        qc.z(phaseerrors)
    # --------------------
    
    qc = hadamard(qc)
    qc = shorDecode(qc)
    
    if drawCircuit: # Return a drawing of the circuit using MatPlotLib
        qc.draw("mpl")
        plt.show()

    if drawStates:
        psi = Statevector(qc)
        psi.draw("bloch")  # psi is a Statevector object
        plt.show()
    
    return qc
    

def shorEncode(initial = "0"):
    """Creates the encoding part of Shors Code with a given initial state

    Args:
        initial (str, optional): The initial state of qubit 0, can be "0" (default), "1", "+", "-", "l", "r", or 
                                 any other Statevector.

    Returns:
        QuantumCircuit: the created quantum circuit
    """
    # Build a quantum circuit with 9 qubits and 9 classical bits
    qc = QuantumCircuit(9, 9)

    qc.prepare_state(initial, 0)
    qc.prepare_state("0", 1)
    qc.prepare_state("0", 2)
    qc.prepare_state("0", 3)
    qc.prepare_state("0", 4)
    qc.prepare_state("0", 5)
    qc.prepare_state("0", 6)
    qc.prepare_state("0", 7)
    qc.prepare_state("0", 8)
 
    qc.cx(0, [3, 6])
    qc.h([0, 3, 6])
    qc.cx([0, 0, 3, 3, 6, 6], [1, 2, 4, 5, 7, 8])
    
    return qc


def shorDecode(qc):
    """Creates the decoding part of Shors code

    Args:
        qc (QuantumCircuit): the quantum circuit so far that should now be decoded

    Returns:
        QuantumCircuit: the circuit with the decoding section added
    """
    qc.cx([0, 0, 3, 3, 6, 6], [1, 2, 4, 5, 7, 8])
    qc.ccx([1, 4, 7], [2, 5, 8], [0, 3, 6])
    qc.h([0, 3, 6])
    qc.cx(0, [3, 6])
    qc.ccx(3, 6, 0)
    
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


def hadamard(qc):
    """Applies a Hadamard gate to the logical qubit

    Args:
        qc (QuantumCircuit): the circuit to apply the hadamard gate to

    Returns:
        QuantumCircuit: the circuit with a hadamard gate
    """
    # Majority vote
    qc.cx([0, 0, 3, 3], [1, 2, 4, 5])
    qc.ccx([1, 4], [2, 5], [0, 3])
    
    # Convert 2-3 and 4-5
    qc.x([0, 3, 6, 7, 8])
    qc.cx(8, [6, 7])
    qc.ch([0, 3], 8)
    qc.cx(8, [6, 7])
    qc.x([0, 6, 7, 8])

    # Convert 0-1 and 6-7
    qc.cx(8, [6, 7])
    qc.ch([0, 3], 8)
    qc.cx(8, [6, 7])
    qc.x(3)
    
    # Undo Majority vote
    qc.ccx([1, 4], [2, 5], [0, 3])
    qc.cx([0, 0, 3, 3], [1, 2, 4, 5])
    
    return qc

def simulate(qc, basis: Basis, shots = 1000):
    """Find the number of times a certain state is measured for a circuit in a given basis.
    
    Args:
        qc (QuantumCircuit): The circuit to be measured.
        basis (Basis): The basis in which it should be measured.
        shots (int, optional): The number of measurements to take. Defaults to 1000.

    Returns:
        dict: A count of how many times different states were measured
    """
    if basis == Basis.X:
        qc.h(0)
    
    qc.measure(range(9), [8, 7, 6, 5, 4, 3, 2, 1, 0])

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
