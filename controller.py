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
        """Saves current state of the dashboard controller using repository."""
        self.repository.save_state(self.state)

    def create_module(self) -> Module:
        """Creates a new module and publishes 'module_created' event."""
        module = Module("")
        self.state.add_module(module)
        self.event_manager.publish("module_created", module)
        return module

    def delete_module(self, module: Module) -> None:
        """Deletes given module and publishes 'module_deleted' event."""
        self.state.remove_module(module)
        self.selected_module = None
        self.event_manager.publish("module_deleted", module)

    def select_module(self, module: Module) -> None:
        """Sets the controllers currently selected module to the desired module and publishes 'module_selected' event."""
        self.selected_module = module
        self.event_manager.publish("module_selected", module)

    def update_module(self, module: Module, attribute: str, value: any) -> None:
        """Updates an attribute of a module and publishes "module_updated" event."""
        if module is None:
                raise ValueError("Module doesn't exist")
        setattr(module, attribute, value)
        self.event_manager.publish("module_updated", module)

    def update_module_exam(self, module: Module, attribute: str, value: any) -> None:
        """Update an attribute of a module's exam and publishes 'module_updated' event."""
        if module is None:
            raise ValueError("Module doesn't exist")
        if module.exam is None:
            module.exam = Exam()
        setattr(module.exam, attribute, value)
        self.event_manager.publish("module_updated", module)
