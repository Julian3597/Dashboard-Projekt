from dashentities import Module, DegreeProgram, Exam, ExamStatus
from dashsaveload import DashboardRepository
from dashevents import EventManager


class DashboardController:
    selected_module: Module | None
    state: DegreeProgram
    repository: DashboardRepository
    event_manager: EventManager

    def __init__(self, repository: DashboardRepository, event_service: EventManager) -> None:
        self.repository = repository
        self.state = repository.load_state()
        self.event_manager = event_service
        self.selected_module = None

    def save(self) -> None:
        self.repository.save_state(self.state)

    def create_module(self) -> Module:
        module = Module("")
        self.state.add_module(module)
        return module

    def delete_module(self, module: Module) -> None:
        self.state.remove_module(module)
        self.selected_module = None
        self.event_manager.publish("module_deleted", module)

    def select_module(self, module: Module) -> None:
        self.selected_module = module
        self.event_manager.publish("module_selected", module)

    def update_module(self, module: Module, attribute: Any, value: Any) -> None:
        if self.selected_module is None:
            return
        if module is None:
                raise ValueError("Module doesn't exist")
        setattr(module, attribute, value)
        self.event_manager.publish("module_updated", module)

    def update_module_exam(self, module: Module, attribute: Any, value: Any) -> None:
        if self.selected_module is None:
            return
        if module is None:
            raise ValueError("Module doesn't exist")
        if module.exam is None:
            module.exam = Exam()
        setattr(module.exam, attribute, value)
        self.event_manager.publish("module_updated", module)
