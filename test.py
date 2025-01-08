"""
Hello world code from https://docs.quantum.ibm.com/guides/hello-world
"""

from matplotlib import pyplot as plt

from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector, DensityMatrix
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from qiskit_ibm_runtime import EstimatorV2
from qiskit_ibm_runtime.fake_provider import FakeAlmadenV2

# Build a quantum circuit
qc = QuantumCircuit(2)

qc.prepare_state(Statevector.from_label("00"), [0, 1])

qc.x(1)
qc.h(0)
qc.h(1)
qc.cx(0, 1)
 
# Return a drawing of the circuit using MatPlotLib
qc.draw("mpl")
plt.show()

psi = Statevector(qc)
psi.draw("bloch")  # psi is a Statevector object
plt.show()
 
DensityMatrix(psi).draw("qsphere")  # convert to a DensityMatrix and draw
plt.show()

# Set up six different observables.
observables_labels = ["IZ", "IX", "ZI", "XI", "ZZ", "XX"]
observables = [SparsePauliOp(label) for label in observables_labels]

# Set up code to run on simulator 
backend = FakeAlmadenV2()
estimator = EstimatorV2(backend)
 
# Convert to an ISA circuit and draw this
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
isa_circuit = pm.run(qc)

isa_circuit.draw("mpl", idle_wires=False)
plt.show()

# layout-mapped observables
mapped_observables = [
    observable.apply_layout(isa_circuit.layout) for observable in observables
]

# Run it
job = estimator.run([(isa_circuit, mapped_observables)])
 
# This is the result of the entire submission. There is one pub, so this contains one inner result (with some metadata)
pub_result = job.result()[0]

values = pub_result.data.evs 
errors = pub_result.data.stds

# plotting graph
plt.plot(observables_labels, values, "-o")
plt.errorbar(observables_labels, values, yerr=errors, fmt="o")
plt.xlabel("Observables")
plt.ylabel("Values")
plt.show()
