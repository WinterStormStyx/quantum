from qiskit import QuantumCircuit
from basis import Basis
from matplotlib import pyplot as plt
from shor_cnot import shorDecode, shorEncode, applyLogicalCNot, simulate
import numpy as np

# from LaflammeV2 import measure, laflamme
from shor import shor, measurement
# from basis import Basis
import numpy as np

for error in range(9):
    # initialize the two logical qubits
    qc1 = shorEncode("1")
    qc2 = shorEncode("0")

    # build the circuit of two logical qubits
    qc = QuantumCircuit(18, 2)
    qc.compose(qc1, range(9), inplace = True)
    qc.compose(qc2, range(9,18), inplace = True)
    qc.barrier()

    error2 = np.random.randint(9, 18) # errors will occur on this random bit in the second logical qubit
    qc.x(error)
    qc.x(error2)
    
    qc.z(error)
    qc.z(error2)

    applyLogicalCNot(qc)
    qc.barrier()

    qc = shorDecode(qc, 0)  # Decode the first logical qubit
    qc = shorDecode(qc, 9)  # Decode the second logical qubit
    qc.barrier()

    # Draw circuit
    # qc.draw("mpl")
    # plt.title("Logical qubit 18")
    # plt.show()

    print("Error on bits ", error, ", ", error2, " ", simulate(qc, Basis.Z))

# Actually using the code here to make it cleaner

# Shor
# for i in range(1):
#     bit = np.random.randint(0, 9, size=1) # find a bit for errors

#     qc = shor("0", biterrors=None, phaseerrors=None, drawCircuit=True, drawStates=True)
#     measurement(qc, measurement_basis="X")

# Laflamme
# for error in [0, 1, 2, 3, 4]:
#     for state in ["0", "1", "+", "-"]:
#         # Measure in both basis
#         d1 = measure(laflamme(state, phaseerror=error, biterror=error), "X")
#         d2 = measure(laflamme(state, phaseerror=error, biterror=error), "Z")
        
#         # Combine the results and print the output of the most measured state
#         result = dict((k, sum(d[k] for d in (d1, d2) if k in d)) for k in (d1 | d2).keys())
#         print(max(result, key=result.get))
