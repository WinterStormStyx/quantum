from LaflammeV2 import measure, laflamme
from Shor import shor, measurement
from Basis import Basis
import numpy as np

# Actually using the code here to make it cleaner

# Shor
for i in range(4):
    bit = np.random.randint(0, 9, size=1) # find a bit for errors

    qc = shor("0", biterrors=bit, phaseerrors=bit, drawCircuit=True, drawStates=True)
    measurement(qc, measurement_basis="Z")

# Laflamme
for error in [0, 1, 2, 3, 4]:
    for state in ["0", "1", "+", "-"]:
        # Measure in both basis
        d1 = measure(laflamme(state, phaseerror=error, biterror=error), Basis.X)
        d2 = measure(laflamme(state, phaseerror=error, biterror=error), Basis.Z)
        
        # Combine the results and print the output of the most measured state
        result = dict((k, sum(d[k] for d in (d1, d2) if k in d)) for k in (d1 | d2).keys())
        print(max(result, key=result.get))

def applylogicalHadamard(qc):
    qc = Quantum
    qc.ccx([6,7],8)
    for i in range(8)
        qc.x(i)
    qc.z(8)
    qc.h(8)
    qc.ccx([0,1,2,3,4,5,6,7], 8)
    for i in range(8)
        qc.x(i)
    qc.ccx([6,7],8)

def applylogicalTgate(qc):
    qc.cx(0,[1,2])
    qc.ccx([1,2],0)