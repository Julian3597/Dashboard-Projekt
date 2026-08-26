from dataclasses import dataclass, field
from enum import Enum, auto

class ExamStatus(Enum):
    NOT_TAKEN = auto()
    IN_PROGRESS = auto()
    SUCCEEDED = auto()
    FAILED = auto()

class DegreeTitle(Enum):
    OTHER = auto()
    BACHELOR = auto()
    MASTER = auto()
    DOCTOR = auto()

@dataclass()
class Exam:
    attempts: int = 0
    grade: int = 0
    _status: ExamStatus = field(default=ExamStatus.NOT_TAKEN)

    def __post_init__(self):
        self.status = self._status

    @property
    def status(self):
        """Represents an exams current part of the grading process.
           Is an enum value, but can also be set as a string or int and will
            be automatically converted to the equivalent ExamStatus value.
        """
        return self._status

    @status.setter
    def status(self, value):
        if value is None:
            self._status = ExamStatus.NOT_TAKEN
        elif isinstance(value, str):
            self._status = ExamStatus[value]  # by name
        elif isinstance(value, int):
            self._status = ExamStatus(value)  # by value
        elif isinstance(value, ExamStatus):
            self._status = value
        else:
            raise TypeError("status must be a string, int, or ExamStatus")

@dataclass(slots=True)
class Module:
    id: str
    name: str = ""
    description: str = ""
    _ects: int = 0
    _exam: Exam | None = None

    def __post_init__(self):
        if not self.id:
            self.id = "MODULE_ID"
            self.name = "MODULE_NAME"
            self.description = "MODULE_DESCRIPTION"

    @property
    def ects(self) -> int:
        return self._ects

    @ects.setter
    def ects(self, value: int):
        if not isinstance(value, int):
            raise TypeError("ects must be an integer")
        if value < 0:
            raise ValueError("ects must not be negative")
        self._ects = value

    @property
    def exam(self):
        return self._exam

    @exam.setter
    def exam(self, value):
        if value is None:
            self._exam = None
            return
        if isinstance(value, dict):
            value = Exam(**value)
        if not isinstance(value, Exam):
            raise TypeError("exam must be an Exam, dict, or None")
        self._exam = value

    def add_exam(self) -> None:
        if self._exam is not None:
            raise ValueError("Module already has an exam, call remove_exam() first")
        self._exam = Exam()

    def remove_exam(self) -> None:
        self._exam = None

@dataclass
class DegreeProgram:
    max_ects: int
    _degree_title: DegreeTitle
    duration_months: int
    modules: list[Module] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        self.degree_title = self._degree_title

    @property
    def spent_ects(self) -> int:
        """Returns the total ECTS of all modules in DegreeProgram"""
        return sum(module.ects for module in self.modules)

    @property
    def degree_title(self):
        """Represents"""
        return self._degree_title

    @degree_title.setter
    def degree_title(self, value):
        if value is None:
            #fallback value
            self._degree_title = DegreeTitle.OTHER
        elif isinstance(value, str):
            self._degree_title = DegreeTitle[value]  # by name
        elif isinstance(value, int):
            self._degree_title = DegreeTitle(value)  # by value
        elif isinstance(value, DegreeTitle):
            self._degree_title = value
        else:
            raise TypeError("degree_title must be a string, int, or DegreeTitle")

    def add_module(self, module: Module) -> None:
        """Adds a module to the DegreeProgram"""
        self.modules.append(module)

    def remove_module(self, module: Module) -> None:
        """Removes a module from the DegreeProgram"""
        self.modules.remove(module)