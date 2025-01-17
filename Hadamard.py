import mttkinter as tkinter # really dirty fix for a RunTime error you get when you add Aer for noise

from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from qiskit_ibm_runtime import EstimatorV2
from qiskit_ibm_runtime.fake_provider import FakeAlmadenV2

from matplotlib import pyplot as plt
import numpy as np
from shor import shor, measurement,shorEncode

def applylogicalHadamard(qc):

    qc = QuantumCircuit(9)
 
    qc.ccx(6,7,8)
    for i in range(8):
        qc.x(i)
    qc.z(8)
    qc.h(8)
    qc.cx([0,1,2,3,4,5,6,7], 8)
    for i in range(8):
        qc.x(i)
    qc.ccx(6,7,8)
    qc.draw("mpl")
    plt.show()

applylogicalHadamard(shorEncode("0"))