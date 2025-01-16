# from LaflammeV2 import measure, laflamme
from shor import shor, measurement
# from basis import Basis
import numpy as np

# Actually using the code here to make it cleaner

# Shor
for i in range(1):
    bit = np.random.randint(0, 9, size=1) # find a bit for errors

    qc = shor("0", biterrors=None, phaseerrors=None, drawCircuit=True, drawStates=True)
    measurement(qc, measurement_basis="X")

# Laflamme
# for error in [0, 1, 2, 3, 4]:
#     for state in ["0", "1", "+", "-"]:
#         # Measure in both basis
#         d1 = measure(laflamme(state, phaseerror=error, biterror=error), "X")
#         d2 = measure(laflamme(state, phaseerror=error, biterror=error), "Z")
        
#         # Combine the results and print the output of the most measured state
#         result = dict((k, sum(d[k] for d in (d1, d2) if k in d)) for k in (d1 | d2).keys())
#         print(max(result, key=result.get))