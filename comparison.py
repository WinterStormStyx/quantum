from laflamme.measure import measure as lmeasure
from laflamme.code import laflamme

from shor.measure import measure as smeasure
from shor.code import shor

import random
from enum import Enum
from matplotlib import pyplot as plt

class Basis(Enum):
    """ Helperclass to specify the basis to measure in
        Options are the X, Y, and Z basis
    """
    X = "X"
    Z = "Z"
    Y = "Y"

def randomError(num_qubits, prob):
    """Add random error to a circuit

    Args:
        num_qubits (int): number of qubits in the circuit
        prob (float): probability of an error to occur

    Returns:
        list: a list of zero or one affected qubits
    """
    if(random.random() <= prob):
        return [random.randint(0, num_qubits-1)]
    return []

counts = {"5":[], "9":[]}
error_rate = [0.5, 0.1]# [0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005]

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
                d1 = lmeasure(laflamme("+", biterror=biterror, phaseerror=phaseerror), Basis.Z)
                d2 = lmeasure(laflamme("+", biterror=biterror, phaseerror=phaseerror), Basis.X)
            else:
                d1 = smeasure(shor("+", biterror=biterror, phaseerror=phaseerror), Basis.Z)
                d2 = smeasure(shor("+", biterror=biterror, phaseerror=phaseerror), Basis.X)
            
            result = dict((k, sum(d[k] for d in (d1, d2) if k in d)) for k in (d1 | d2).keys())
            count += int(max(result, key=result.get)[0] == "+")
        print(prob, qubits, count/iteration)
        counts[str(qubits)].append(count / iteration)
 
       
plt.scatter(error_rate, counts["5"], label="Laflamme's Code")
plt.scatter(error_rate, counts["9"], label="Shor's Code")

plt.title("Likelihood for Correct Output depending on Probability of Error for Shor's and Laflamme's Code on + State")
plt.xlabel("Probability for error to occur")
plt.ylabel("Probability state is correct")

plt.legend()
plt.show()
