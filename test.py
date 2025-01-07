from qiskit import QuantumCircuit, transpile #execute, Aer
from qiskit.visualization import plot_histogram

from qiskit_ibm_runtime import QiskitRuntimeService

token = open("token.txt", "r").readline()

#QiskitRuntimeService.save_account(
#    token=token,
#    channel="ibm_quantum"  # `channel` distinguishes between different account types
#)

