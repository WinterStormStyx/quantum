from Shor import shor, measurement, shorEncode, hadamard, shorDecode, simulate
from Basis import Basis

# Actually using the code here to make it cleaner

# Shor

# biterror on 8 does not always work, phaserror on 7 and 8
for state in ["+", "-"]:
    for error in range(6):
        qc = shor(state, biterrors=error, phaseerrors=error)

        print(simulate(qc, Basis.Z))
