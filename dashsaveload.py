import json
from abc import ABC, abstractmethod
from dataclasses import asdict
from dashentities import DegreeProgram, DegreeTitle, Exam, Module


class DashboardRepository(ABC):
    @abstractmethod
    def load_state(self) -> DegreeProgram:
        pass

    @abstractmethod
    def save_state(self, state: DegreeProgram) -> None:
        pass


class JSONDashboardRepository(DashboardRepository):
    save_file_path: str

    def __init__(self, save_file_path: str):
        self.save_file_path = save_file_path

    @staticmethod
    def _create_default_state() -> DegreeProgram:
        return DegreeProgram(150, DegreeTitle.BACHELOR, 36)

    def load_state(self) -> DegreeProgram:
        state = self._read_state_from_file(self.save_file_path)
        return state

    def save_state(self, state: DegreeProgram) -> None:
        self._write_state_to_file(self.save_file_path, state)

    def _read_state_from_file(self, path: str) -> DegreeProgram:
        try:
            with open(path, "r") as file:
                raw_degreeprogram = json.load(file)
        except FileNotFoundError:
                degreeprogram = self._create_default_state()
                return degreeprogram
        degree_program = DegreeProgram(raw_degreeprogram["max_ects"], raw_degreeprogram["degree_title"],
                                       raw_degreeprogram["duration_months"])
        for module_data in raw_degreeprogram["modules"]:
            exam = Exam(**module_data["_exam"]) if module_data["_exam"] else None
            module = Module(id=module_data["id"], name=module_data["name"], description=module_data["description"], _exam=exam, _ects=module_data["_ects"])
            degree_program.add_module(module)
        return degree_program

    @staticmethod
    def _write_state_to_file(path: str, data: DegreeProgram) -> None:
        with open(path, "w") as file:
            json.dump(asdict(data), file, indent=4, default=lambda x: x.value)  # lambda for enums
