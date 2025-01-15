from LaflammeV2 import measure, laflamme
from basis import Basis

for error in [0, 1, 2, 3, 4]:
    for state in ["0", "1", "+", "-"]:
        # Measure in both basis
        d1 = measure(laflamme(state, phaseerror=error, biterror=error), Basis.X)
        d2 = measure(laflamme(state, phaseerror=error, biterror=error), Basis.Z)
        
        # Combine the results and print the output of the most measured state
        result = dict((k, sum(d[k] for d in (d1, d2) if k in d)) for k in (d1 | d2).keys())
        print(max(result, key=result.get))