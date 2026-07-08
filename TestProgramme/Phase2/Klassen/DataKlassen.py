from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Module:
    name: str
    description: str
    ects: int
    exam: Exam



@dataclass
class Exam:
    name: str

# __init__ ist automatisch definiert weil es eine dataclass ist
# typen in python sind nur vorschläge und *müssen* nicht respektiert werden, sollte man natürlich aber schon
moduleInstance = Module("test name", "test beschreibung", 5, Exam("Exam1"))
print(moduleInstance.name)

# gleicher output
print(moduleInstance.exam.name)
print(Exam("Exam1").name)