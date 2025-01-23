# this code works differently and effectively 'cheats' by calculating the remaining statevector
# Because I calculate the statevector from the partial trace of the entire density matrix (5 qubits), 
# I can recover the initial state up to a global phase (this is why the "-"" state seems to have a sign flip, but its just a global phase of e^ipi)

from qiskit import transpile
from qiskit.quantum_info import partial_trace
from qiskit_aer import Aer

from LaflammeV2 import laflamme

qc = laflamme("-")

qc.draw(output="mpl")
plt.show()

statevector_simulator = Aer.get_backend('statevector_simulator')
job_sv = statevector_simulator.run(transpile(qc, statevector_simulator))
result_sv = job_sv.result()
statevector = partial_trace(result_sv.get_statevector(), [0, 1, 3, 4])
statevector = partial_trace(result_sv.get_statevector(), [0, 1, 3, 4]).to_statevector()
print(statevector)
print(np.dot(np.conj(inp.data), statevector.data)**2)