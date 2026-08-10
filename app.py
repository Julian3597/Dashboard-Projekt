from dashevents import EventManager
from controller import DashboardController
from dashsaveload import JSONDashboardRepository
from dashui import ViewContainer, DetailView, EctsView, ListView

class DashboardApp:
    _save_file_path: str
    def start(self):
        self._save_file_path = "save.json"
        repository = JSONDashboardRepository(self._save_file_path)
        event_service = EventManager()
        controller = DashboardController(repository, event_service)
        container = ViewContainer(controller, event_service,"1800x900", DetailView, ListView, EctsView)
        container.mainloop()
