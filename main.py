from Shor import shor, measurement, shorEncode, hadamard, shorDecode, simulate
from LaflammeV2 import laflamme
from Basis import Basis
import random
import numpy as np
from matplotlib import pyplot as plt

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
