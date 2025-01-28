# Quantum Group Project

Welcome to the code repository for our end of the quantum minor group project! In this project, we wanted to explore the difference between the Shor code and the Laflamme code. After adding logic to build both these codes and ways to compare them, we moved to our second aim of the project: building a universal fault-tolerant gate set for both of these codes.

### Qiskit

In this project, we decided to make use of the qiskit framework for our code. This is an open-source framework offered by IBM with which one can build and measure circuits. These circuits can be run on physical quantum hardware or simulated through Qiskits simulators. The documentation can be found here: https://docs.quantum.ibm.com/guides

### Code structure

You will find a separate folder for the two different codes, called shor and laflamme respectively. In each of these folders there are 4 documents: 
- `code.py` containing the encoding and decoding logic for that specific code
- `gates.py` containing the logic to create our universal, fault-tolerant gates 
- `main.py` in which we actually used the codes, there should be some logic that can be used to actually run methods there
- `measure.py` containing different methods with which the built circuit could be measured   

Aside from these there are two more documents in this repository:
- `laflamme/fidelity.py` containing logic on the fidelity of the laflamme circuit
- `comparison.py` containing logic with which the fault-tolerance of the pure Shor and Laflamme code can be compared
