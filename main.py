from LaflammeV2 import measure, laflamme
from Shor import shor, measurement, shorEncode, hadamard, shorDecode
from Basis import Basis
import numpy as np

from qiskit import transpile
from qiskit_aer import AerSimulator

# Actually using the code here to make it cleaner

# Shor


#qc = shor("0", drawCircuit=True, drawStates=True)

qc = shorEncode("-")
qc = hadamard(qc)
qc = shorDecode(qc)

#if True:
#    qc.h(0)

qc.measure(range(9), [8, 7, 6, 5, 4, 3, 2, 1, 0])

simulator = AerSimulator()
compiled_circuit = transpile(qc, simulator)
job = simulator.run(compiled_circuit, shots=1000)
sim_result = job.result().get_counts()
print(sim_result)

#for i in range(4):
#    bit = np.random.randint(0, 9, size=1) # find a bit for errors

#    qc = shor("0", biterrors=bit, phaseerrors=bit, drawCircuit=True, drawStates=True)
#    measurement(qc, measurement_basis="Z")

# Laflamme
#for error in [0, 1, 2, 3, 4]:
#    for state in ["0", "1", "+", "-"]:
#        # Measure in both basis
#        d1 = measure(laflamme(state, phaseerror=error, biterror=error), Basis.X)
#        d2 = measure(laflamme(state, phaseerror=error, biterror=error), Basis.Z)
#        
#        # Combine the results and print the output of the most measured state
#        result = dict((k, sum(d[k] for d in (d1, d2) if k in d)) for k in (d1 | d2).keys())
#        print(max(result, key=result.get))