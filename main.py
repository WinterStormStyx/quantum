from Shor import shor, measurement, shorEncode, hadamard, shorDecode, simulate
from LaflammeV2 import laflamme
from Basis import Basis
import random

from qiskit import QuantumCircuit
from basis import Basis
from matplotlib import pyplot as plt
from shor_cnot import shorDecode, shorEncode, applyLogicalCNot, simulate

import numpy as np
from matplotlib import pyplot as plt

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
def randomError(num_qubits, prob):
    if(random.random() <= prob):
        return [random.randint(0, num_qubits-1)]
    return []

counts = {"5":[], "9":[]}
error_rate = [0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005]

for qubits in [5, 9]:
    for prob in error_rate:
        count = 0
        iteration = 500
        for error in range(iteration):
            phaseerror = []
            biterror = []
            for i in range(random.randint(0, 5 * qubits)):
                phaseerror = phaseerror + randomError(qubits, prob)
            for i in range(random.randint(0, 5 * qubits)):
                biterror = biterror + randomError(qubits, prob)

            phaseerror = phaseerror if len(phaseerror) != 0 else None
            biterror = biterror if len(biterror) != 0 else None

            if(qubits == 5):
                d1 = simulate(laflamme("+", biterrors=biterror, phaseerrors=phaseerror), Basis.Z, num_qubits=qubits)
                d2 = simulate(laflamme("+", biterrors=biterror, phaseerrors=phaseerror), Basis.X, num_qubits=qubits)
            else:
                d1 = simulate(shor("+", biterrors=biterror, phaseerrors=phaseerror), Basis.Z, num_qubits=qubits)
                d2 = simulate(shor("+", biterrors=biterror, phaseerrors=phaseerror), Basis.X, num_qubits=qubits)
            
            result = dict((k, sum(d[k] for d in (d1, d2) if k in d)) for k in (d1 | d2).keys())
            count += int(max(result, key=result.get)[0] == "+")
        print(prob, qubits, count/iteration)
        counts[str(qubits)].append(count / iteration)
 
       
plt.scatter(error_rate, counts["5"], label="Laflamme's Code")
plt.scatter(error_rate, counts["9"], label="Shor's Code")
#plt.scatter(error_rate, counts["0"], label="0")
#plt.scatter(error_rate, counts["1"], label="1")

plt.title("Likelihood for Correct Output depending on Probability of Error for Shor's and Laflamme's Code on + State")
plt.xlabel("Probability for error to occur")
plt.ylabel("Probability state is correct")

plt.legend()
plt.show()

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
