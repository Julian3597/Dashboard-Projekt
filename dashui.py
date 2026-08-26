from __future__ import annotations

import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import OptionMenu, font
from typing import TYPE_CHECKING, Callable

import _tkinter

from dashentities import Module, ExamStatus
from dashevents import EventManager

if TYPE_CHECKING:
    from controller import DashboardController

# ABCs
class Refreshable(ABC):
    """ABC for UI components that can update their displayed state."""
    @abstractmethod
    def refresh(self) -> None:
        """Refresh components' displayed values"""
        pass

# Subobjects
class ModuleCard(tk.Frame, Refreshable):
    """Display a summary of a module's data as a clickable card."""
    controller: DashboardController
    _event_manager: EventManager
    module: Module
    def __init__(self, master: tk.Misc, controller: DashboardController, event_manager: EventManager, module: Module) -> None:
        # Init
        super().__init__(master, bg="white", bd=2, relief="raised", padx=10, pady=10)
        self.controller = controller
        self.module = module
        self._event_manager = event_manager
        # Vars
        self.module_title = tk.StringVar()
        self.module_description = tk.StringVar()
        self.module_exam_grade = tk.DoubleVar()
        self.module_exam_status = tk.StringVar()

        # Text
        self.title = tk.Label(self, textvariable=self.module_title, bg="white", width=40, font=("Arial", 10), anchor="w")
        self.description = tk.Label(self, textvariable=self.module_description, bg="white", anchor="w")
        self.exam_grade_text = tk.Label(self, textvariable=self.module_exam_grade, bg="white", font=("Arial", 14))
        self.exam_status_text = tk.Label(self, textvariable=self.module_exam_status, bg="white", font=("Arial", 14))

        # Grid
        # Rows
        self.grid_rowconfigure(0, weight=0)  # Title
        self.grid_rowconfigure(1, weight=0)  # Description

        # Columns
        self.grid_columnconfigure(0, weight=0) # Labels
        self.grid_columnconfigure(1, weight=1) # Exam grade display

        # Add Objects to Grid
        self.title.grid(row=0, column=0, sticky="nw")
        self.description.grid(row=1, column=0, sticky="nw")
        # Grade display handled in _conditional_grade_display

        # Bindings
        # Bind events for each part of the Card so everything is clickable
        self.bind("<Button-1>", self._on_click)
        self.title.bind("<Button-1>", self._on_click)
        self.description.bind("<Button-1>", self._on_click)

        # subscribed events
        self._event_manager.subscribe("module_updated", self._on_module_updated)

        self.refresh()

    def _on_module_updated(self, module: Module) -> None:
        if module == self.module:
            self.refresh()

    def _on_click(self, event: tk.Event) -> None:
        self.controller.select_module(self.module)

    @staticmethod
    def _truncate_text(text: str, max_pixel_length: int, fontname="TkDefaultFont") -> str:
        label_font = font.nametofont(fontname)
        truncated = False
        text = text.replace("\n", " ")
        while label_font.measure(text + "...") > max_pixel_length:
            text = text[:-1]
            truncated = True
        if truncated:
            text += "..."
        return text

    def _conditional_grade_display(self) -> None:
        """Show the grade for passed exams, otherwise exam status."""
        for widget in (self.exam_status_text, self.exam_grade_text):
            try:
                if widget.winfo_exists():
                    widget.grid_forget()
            except tk.TclError:
                # Widget was already destroyed.
                pass
        if self.module.exam is not None:
            if self.module.exam.status == ExamStatus.SUCCEEDED:
                self.exam_grade_text.grid(row=0, column=1, rowspan=2, sticky="nesw")
            else:
                self.exam_status_text.grid(row=0, column=1, rowspan=2, sticky="nesw")

    def _set_fields(self) -> None:
        self.module_title.set(self.module.name)
        self.module_description.set(self._truncate_text(self.module.description, 250))
        if self.module.exam is not None:
            self.module_exam_grade.set(self.module.exam.grade)
            self.module_exam_status.set(self.module.exam.status.name)

    def destroy(self) -> None:
        # Unsubscribe from EventManager before this gets destroyed properly
        self._event_manager.unsubscribe("module_updated", self._on_module_updated)
        super().destroy()

    def refresh(self) -> None:
        self._set_fields()
        self._conditional_grade_display()


# Views
class ListView(tk.Frame, Refreshable):
    """Display all modules as a scrollable list of module cards."""
    controller: DashboardController
    _event_manager: EventManager
    module_cards: list[ModuleCard]
    def __init__(self, master: tk.Misc, controller: DashboardController, event_manager: EventManager) -> None:
        # Init
        super().__init__(master, bg="lightblue")
        self.controller = controller
        self._event_manager = event_manager
        self.module_cards = []

        # Header
        tk.Label(self, text="List View", bg="lightblue", font=("Arial", 24)).pack(side="top")

        # Module Container
        self.container = tk.Canvas(self, width=400, height=300, bg="lightblue")
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.container.yview)
        scrollbar.pack(side="right", fill="y")
        self.container.configure(yscrollcommand=scrollbar.set)
        self.container.bind("<Configure>", self._resize_content)
        self.container.bind_all("<MouseWheel>",
            lambda e:
            self.container.yview_scroll(-e.delta // 120, "units")
            if self.container.yview() != (0.0, 1.0)
            else None
        )
        self.container.pack(side="left", fill="both", expand=True)
        self.container_content = tk.Frame(self.container, bg="lightblue")
        self.container_content.bind("<Configure>",lambda e: self.container.configure(scrollregion=self.container.bbox("all")))
        self.window = self.container.create_window((0, 0), window=self.container_content, anchor="nw")

        # New Modules Button
        tk.Button(self.container_content, text="New Module", width=30, command=lambda: self._new_module()).pack(side="bottom", pady=8)

        self._event_manager.subscribe("module_deleted", self._module_deleted)
        self.refresh()

    def _resize_content(self, event: tk.Event) -> None:
        self.container.itemconfigure(self.window, width=event.width)

    def _generate_module_card(self, module: Module) -> None:
        card = ModuleCard(self.container_content, self.controller, self._event_manager, module)
        card.pack(pady=10, fill="x", padx=20)
        self.module_cards.append(card)

    def _generate_module_cards(self) -> None:
        """Rebuild list module_cards from controller state."""
        for card in self.module_cards:
            card.destroy()
        self.module_cards.clear()
        for entry in self.controller.state.modules:
            self._generate_module_card(entry)

    def _module_deleted(self, module: Module) -> None:
        self.refresh()

    def _new_module(self) -> Module:
        new_module = self.controller.create_module()
        self.controller.select_module(new_module)
        self.refresh()
        return new_module

    def refresh(self) -> None:
        self._generate_module_cards()
        self.container_content.update_idletasks()
        self.container.configure(scrollregion=self.container.bbox("all"))



class DetailView(tk.Frame):
    """Display and edit the details of selected module."""
    controller: DashboardController
    _event_manager: EventManager
    is_editable: bool
    _status_list: list[str]
    def __init__(self, master: tk.Misc, controller: DashboardController, event_manager: EventManager) -> None:
        # Init
        super().__init__(master, bg="lightgreen")
        self.controller = controller
        self._event_manager = event_manager
        self.is_editable = False
        self._status_list = [status.name for status in ExamStatus]

        # Vars
        self.course_id = tk.StringVar()
        self.course_title = tk.StringVar()
        self.course_ects = tk.IntVar()
        self.exam_status = tk.StringVar()
        self.exam_grade = tk.DoubleVar()
        self.exam_attempts = tk.IntVar()

        # Fields and Labels
        self.header = tk.Label(self, text="Detail View", bg="lightgreen", font=("Arial", 24))
        self.exam_header = tk.Label(self, text="Course Exam", bg="lightgreen", font=("Arial", 16))
        self.course_id_label = tk.Label(self, text="ID", bg="lightgreen", font=("Arial", 24))
        self.course_id_entry = tk.Entry(self, textvariable=self.course_id, bg="lightgreen", font=("Arial", 24))
        self.course_tite_label = tk.Label(self, text="Course Title", bg="lightgreen", font=("Arial", 24))
        self.course_title_entry = tk.Entry(self, textvariable=self.course_title, bg="lightgreen", font=("Arial", 24))
        self.course_ects_label = tk.Label(self, text="ECTS", bg="lightgreen", font=("Arial", 24))
        self.course_ects_entry = tk.Entry(self, textvariable=self.course_ects, bg="lightgreen", font=("Arial", 24))
        self.course_description_entry = tk.Text(self, bg="lightgreen", font=("Arial", 24), width=50, height=15) # Text doesn't support textvariables
        self.exam_grade_entry = tk.Entry(self, textvariable=self.exam_grade, bg="lightgreen", font=("Arial", 16), width=12)
        self.exam_attempts_entry = tk.Entry(self, textvariable=self.exam_attempts, bg="lightgreen", font=("Arial", 16),width=12)
        self.exam_menu_label = tk.Label(self, text="Exam Status", bg="lightgreen", font=("Arial", 16))
        self.exam_grade_label = tk.Label(self, text="Grade", bg="lightgreen", font=("Arial", 16))
        self.exam_attempts_label = tk.Label(self, text="Attempts", bg="lightgreen", font=("Arial", 16))

        # Menus
        self.exam_status_menu = OptionMenu(self, self.exam_status, *self._status_list)
        self.exam_status_menu.config(width=15)

        # Bindings
        self._bind_module_field(self.course_id, "id")
        self._bind_module_field(self.course_title, "name")
        self._bind_module_field(self.course_ects, "ects")
        self._bind_exam_field(self.exam_grade, "grade")
        self._bind_exam_field(self.exam_attempts, "attempts")
        self._bind_exam_field(self.exam_status, "status")
        self.course_description_entry.bind("<<Modified>>", self._description_modified)

        # Buttons
        self.toggle_edit_button = tk.Button(self, text="Edit Course", command=lambda: self.toggle_editable(), width=18)
        self.delete_module_button = tk.Button(self, text="Delete Course", command=lambda: self.delete_module(controller.selected_module), width=18)

        # Grid
        # Rows
        self.grid_rowconfigure(0, weight=0)  # Heading
        self.grid_rowconfigure(1, weight=0)  # Module ID, Buttons
        self.grid_rowconfigure(2, weight=0)  # Title, Buttons
        self.grid_rowconfigure(3, weight=0)  # ECTS, Buttons
        self.grid_rowconfigure(4, weight=1)  # Description

        # Columns
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=0)

        # Add Objects to Grid
        self.header.grid(row=0, column=1, sticky="n")
        self.exam_header.grid(row=0, column=2, sticky="n")

        self.course_id_label.grid(row=1, column=0, sticky="e")
        self.course_id_entry.grid(row=1, column=1, sticky="s")

        self.course_tite_label.grid(row=2, column=0, sticky="e")
        self.course_title_entry.grid(row=2, column=1, sticky="s")

        self.course_ects_label.grid(row=3, column=0, sticky="e")
        self.course_ects_entry.grid(row=3, column=1,sticky="n")

        self.exam_menu_label.grid(row=1, column=1, sticky="e")
        self.exam_grade_label.grid(row=2, column=1, sticky="e")
        self.exam_attempts_label.grid(row=3, column=1, sticky="e")

        self.exam_status_menu.grid(row=1, column=2, sticky="w")
        self.exam_grade_entry.grid(row=2, column=2, sticky="w")
        self.exam_attempts_entry.grid(row=3, column=2, sticky="n")

        self.toggle_edit_button.grid(row=1, column=3, sticky="w")
        self.delete_module_button.grid(row=2, column=3, sticky="w")

        self.course_description_entry.grid(row=4, column=1, sticky="n")

        # Subscribe to module events exposed by eventManager
        self._event_manager.subscribe("module_selected", self.display_module)
        self._event_manager.subscribe("module_deleted", self.display_module)

        self.refresh()

    def _set_fields(self, module: Module) -> None:
            self.course_id.set(module.id)
            self.course_title.set(module.name)
            self.course_ects.set(module.ects)
            if module.exam is not None:
                self.exam_grade.set(module.exam.grade)
                self.exam_attempts.set(module.exam.attempts)
                self.exam_status.set(module.exam.status.name)
            self.course_description_entry.delete("1.0", tk.END)
            self.course_description_entry.insert("1.0", module.description)

    def _clear_fields(self) -> None:
            self.course_id.set("")
            self.course_title.set("")
            self.course_ects.set(0)
            self.exam_grade.set(0)
            self.exam_attempts.set(0)
            self.exam_status.set(self._status_list[0])
            self.course_description_entry.delete("1.0", tk.END)

    def _bind_field(self, var: tk.Variable, attribute: str, update_method: Callable[[object, str, object], None]) -> None:
        """Bind Tkinter variable to module attribute.
            Everytime variable gets updated, calls specified controller update method.
        """
        def callback(variable_name, index, operation) -> None:
                try:
                    var_value = var.get()
                except _tkinter.TclError:
                    return
                if var_value is not None:
                    if self.controller.selected_module is not None:
                        update_method(self.controller.selected_module, attribute, var_value)
        var.trace_add("write", callback)

    def _bind_exam_field(self, var: tk.Variable, attribute: str) -> None:
        self._bind_field(var, attribute, self.controller.update_module_exam)

    def _bind_module_field(self, var: tk.Variable, attribute: str) -> None:
        self._bind_field(var, attribute, self.controller.update_module)

    def _description_modified(self, event) -> None:
        text_widget = event.widget

        if text_widget.edit_modified(): # Make sure we don't catch events that set modified to false
            text = text_widget.get("1.0", "end-1c") # end-1c so we get the text without the newline at the end
            self.controller.update_module(self.controller.selected_module, "description", text)
        text_widget.edit_modified(False) # Reset modified flag

    def display_module(self, module: Module | None) -> None:
        # We have to temporarily unlock to write to the course_description_entry
        relock = False
        if not self.is_editable:
            self._unlock()
            relock = True
        if module is not None:
            self._set_fields(module)
        else:
            self._clear_fields()
        if relock:
            self._lock()

    def delete_module(self, module: Module | None) -> None:
        self.controller.delete_module(module)
        self.refresh()

    def _update_editable(self) -> None:
        if self.is_editable:
            self._unlock()
        else:
            self._lock()

    def _lock(self) -> None:
        """Disable all editable fields and the delete button."""
        self.course_id_entry.config(state=tk.DISABLED)
        self.course_title_entry.config(state=tk.DISABLED)
        self.course_description_entry.config(state=tk.DISABLED)
        self.course_ects_entry.config(state=tk.DISABLED)
        self.exam_status_menu.config(state=tk.DISABLED)
        self.exam_attempts_entry.config(state=tk.DISABLED)
        self.exam_grade_entry.config(state=tk.DISABLED)
        self.delete_module_button.config(state=tk.DISABLED)

    def _unlock(self) -> None:
        """Enable all editable fields and the delete button."""
        self.course_id_entry.config(state=tk.NORMAL)
        self.course_title_entry.config(state=tk.NORMAL)
        self.course_description_entry.config(state=tk.NORMAL)
        self.course_ects_entry.config(state=tk.NORMAL)
        self.exam_status_menu.config(state=tk.NORMAL)
        self.exam_attempts_entry.config(state=tk.NORMAL)
        self.exam_grade_entry.config(state=tk.NORMAL)
        self.delete_module_button.config(state=tk.NORMAL)

    def toggle_editable(self) -> None:
        """Toggle access to editable fields."""
        self.is_editable = not self.is_editable
        self._update_editable()

    def refresh(self) -> None:
        self.display_module(self.controller.selected_module)
        self._update_editable()




class EctsView(tk.Frame, Refreshable):
    """Display the number of ECTS credits used relative to the maximum."""
    controller: DashboardController
    _event_manager: EventManager
    def __init__(self, master: tk.Misc, controller: DashboardController, event_manager: EventManager) -> None:
        # Init
        super().__init__(master, bg="lightcoral")
        self.controller = controller
        self._event_manager = event_manager

        # Vars
        self.text_var = tk.StringVar()

        # Text
        tk.Label(self, text="ECTS", bg="lightcoral", font=("Arial", 24)).pack(side="top")
        tk.Label(self, textvariable=self.text_var, bg="lightcoral", font=("Arial", 32)).pack(expand=True)

        self.refresh()

    def refresh(self):
        self.text_var.set(f"{self.controller.state.spent_ects} out of {self.controller.state.max_ects} used")

# Takes controller, resolution and 3 UI Classes as arguments, detail_view: left 50%, list_view: bottom right 66%, ects_view: top right 33%
class ViewContainer(tk.Tk, Refreshable):
    """Dashboard View Class Containers"""
    controller: DashboardController
    _event_manager: EventManager
    detail_view: Refreshable
    list_view: Refreshable
    ects_view: Refreshable
    def __init__(self, controller: DashboardController, event_manager: EventManager, resolution: str,
                 detail_view: type[tk.Frame, Refreshable], list_view: type[tk.Frame, Refreshable],
                 ects_view: type[tk.Frame, Refreshable]) -> None:
        # Init
        self.controller = controller
        self._event_manager = event_manager
        super().__init__()  # Call Tk init to create a top-level container
        self.geometry(resolution)  # Set frame size to specified resolution
        self._configure_grid()
        right_grid = self._create_right_grid_container()

        # Put views into grid
        self.detail_view = detail_view(self, controller, event_manager)
        self.detail_view.grid(row=0, column=0, sticky="nsew", padx=(8, 4), pady=8)
        self.detail_view.grid_propagate(False)

        self.ects_view = ects_view(right_grid, controller, event_manager)
        self.ects_view.grid(row=0, column=0, sticky="nsew", pady=(0, 4))
        self.ects_view.grid_propagate(False)

        self.list_view = list_view(right_grid, controller, event_manager)
        self.list_view.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        self.list_view.grid_propagate(False)

        # Run on close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _configure_grid(self) -> None:
        """Configure grid layout and resizing behavior."""
        # Grid Config
        # Set a minsize to hopefully avoid grid resizing
        self.grid_columnconfigure(0, weight=2, minsize=700)  # left 2/3
        self.grid_columnconfigure(1, weight=1, minsize=400)  # right 1/3
        self.grid_rowconfigure(0, weight=1, minsize=400)

    def _create_right_grid_container(self) -> tk.Frame:
        # Helper Container
        right = tk.Frame(self)
        right.grid(row=0, column=1, sticky="nsew", padx=(4, 8), pady=8)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=2)
        return right

    def _on_closing(self) -> None:
        """On close: save application state and close the main window."""
        self.controller.save()
        self.destroy()

    def refresh(self) -> None:
        self.detail_view.refresh()
        self.list_view.refresh()
        self.ects_view.refresh()
