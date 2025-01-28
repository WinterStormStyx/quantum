from laflamme.measure import measure as lmeasure
from laflamme.measure import Basis as LBasis
from laflamme.code import laflamme

from shor.measure import measure as smeasure
from shor.measure import Basis as SBasis
from shor.code import shor

import random
from matplotlib import pyplot as plt

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
                d1 = lmeasure(qc=laflamme("+", biterror=biterror, phaseerror=phaseerror), basis=LBasis.Z)
                d2 = lmeasure(qc=laflamme("+", biterror=biterror, phaseerror=phaseerror), basis=LBasis.X)
            else:
                d1 = smeasure(qc=shor("+", biterror=biterror, phaseerror=phaseerror), basis=SBasis.Z)
                d2 = smeasure(qc=shor("+", biterror=biterror, phaseerror=phaseerror), basis=SBasis.X)
            result = dict((k, sum(d[k] for d in (d1, d2) if k in d)) for k in (d1 | d2).keys())
            count += int(max(result, key=result.get)[0] == "+")
        counts[str(qubits)].append(count / iteration)
 
       
plt.scatter(error_rate, counts["5"], label="Laflamme's Code")
plt.scatter(error_rate, counts["9"], label="Shor's Code")

plt.title("Likelihood for Correct Output depending on Probability of Error for Shor's and Laflamme's Code on + State")
plt.xlabel("Probability for error to occur")
plt.ylabel("Probability state is correct")

plt.legend()
plt.show()
