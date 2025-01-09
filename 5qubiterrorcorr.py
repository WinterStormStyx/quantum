#this file isnt really important, mainly to verify and check if ideas work, not

from matplotlib import pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.visualization import plot_bloch_vector
from qiskit_ibm_runtime import EstimatorV2
from qiskit_ibm_runtime.fake_provider import FakeAlmadenV2
# Build a quantum circuit

state = "+"

qc = QuantumCircuit(1)

qc.prepare_state(state, 0)

qc.p(np.pi, 0)



# Simulate using StatevectorSimulator to extract the statevector
simulator = Aer.get_backend('statevector_simulator')
new_circuit = transpile(qc, simulator)
job = simulator.run(new_circuit)
statevector_result = job.result()
statevector = statevector_result.get_statevector()

# Print the statevector
print("Statevector:", statevector)

# Plot Bloch sphere representation of the statevector
psi = Statevector(statevector)
psi.draw('bloch')
plt.show()












# Return a drawing of the circuit using MatPlotLib
qc.draw("mpl")
plt.show()

psi = Statevector(qc)
psi.draw("bloch")  # psi is a Statevector object
plt.show()
 
# DensityMatrix(psi).draw("qsphere")  # convert to a DensityMatrix and draw
# plt.show()

# Set up six different observables.
observables_labels = ["Z", "X"]
observables = [SparsePauliOp(label) for label in observables_labels]

# Set up code to run on simulator 
backend = FakeAlmadenV2()
estimator = EstimatorV2(backend)
 
# Convert to an ISA circuit and draw this
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
isa_circuit = pm.run(qc)

# isa_circuit.draw("mpl", idle_wires=False)
# plt.show()

# layout-mapped observables
mapped_observables = [
    observable.apply_layout(isa_circuit.layout) for observable in observables
]

# Run it
job = estimator.run([(isa_circuit, mapped_observables)])
 
# This is the result of the entire submission. There is one pub, so this contains one inner result (with some metadata)
pub_result = job.result()[0]
result = job.result()
# statevector = result.get_statevector()

values = pub_result.data.evs 
errors = pub_result.data.stds

#plotting graph
plt.plot(observables_labels, values, "-o")
plt.errorbar(observables_labels, values, yerr=errors, fmt="o")
plt.xlabel("Observables")
plt.ylabel("Values")
plt.show()

# bloch_vector = [2*np.real(a*np.conjugate(b)), 2*np.imag(b*np.conjugate(a)), a*np.conjugate(a)-b*np.conjugate(b)]
# plot_bloch_vector(bloch_vector).show()