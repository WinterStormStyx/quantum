from Shor import shor, measurement, shorEncode, hadamard, shorDecode, simulate
from Basis import Basis

# Actually using the code here to make it cleaner

# Shor

# biterror on 8 does not always work, phaserror on 7 and 8
for state in ["+", "-", "0", "1"]:
    print(state)
    for error in range(9):
        #qc = shor(state, biterrors=error)
        print(simulate(shor(state, biterrors=error, phaseerrors=error), Basis.Z), simulate(shor(state, biterrors=error, phaseerrors=error), Basis.X))
    print("")
