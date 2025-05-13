import flet as ft
from flet import (
    Card,
    Column,
    Container,
    DataCell,
    DataColumn,
    DataRow,
    DataTable,
    Dropdown,
    ElevatedButton,
    Icon,
    IconButton,
    OutlinedButton,
    Row,
    Tab,
    Tabs,
    Text,
    TextField,
    UserControl,
    colors,
    icons,
    padding,
)
from datetime import datetime, date


class LogbookEntryForm(UserControl):
    def __init__(self, on_submit=None, on_cancel=None, entry_data=None):
        super().__init__()
        self.on_submit = on_submit
        self.on_cancel = on_cancel
        self.entry_data = entry_data or {}
        
        # Form fields
        self.start_date_field = TextField(
            label="Start Date",
            value=self.entry_data.get("start_date", date.today().isoformat()),
            icon=icons.CALENDAR_TODAY,
            width=300,
        )
        
        self.responsible_person_field = TextField(
            label="Responsible Person",
            value=self.entry_data.get("responsible_person", ""),
            icon=icons.PERSON,
            width=300,
        )
        
        self.location_dropdown = Dropdown(
            label="Location",
            width=300,
            options=[
                ft.dropdown.Option("1", "Production Floor"),
                ft.dropdown.Option("2", "Office Building"),
                ft.dropdown.Option("3", "Warehouse"),
                ft.dropdown.Option("4", "Server Room"),
                ft.dropdown.Option("5", "Maintenance Shop"),
            ],
            value=self.entry_data.get("location_id", "1"),
        )
        
        self.device_field = TextField(
            label="Device/Machine",
            value=self.entry_data.get("device", ""),
            icon=icons.DEVICES,
            width=300,
        )
        
        self.call_description_field = TextField(
            label="Description of Call",
            value=self.entry_data.get("call_description", ""),
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=620,
        )
        
        self.solution_description_field = TextField(
            label="Description of Solution",
            value=self.entry_data.get("solution_description", ""),
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=620,
        )
        
        self.status_dropdown = Dropdown(
            label="Status",
            width=300,
            options=[
                ft.dropdown.Option("open", "Open"),
                ft.dropdown.Option("completed", "Completed"),
                ft.dropdown.Option("escalation", "Escalation Needed"),
            ],
            value=self.entry_data.get("status", "open"),
        )
        
        self.downtime_field = TextField(
            label="Downtime (hours)",
            value=str(self.entry_data.get("downtime_hours", "")),
            icon=icons.TIMER,
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        self.end_date_field = TextField(
            label="End Date",
            value=self.entry_data.get("end_date", ""),
            icon=icons.CALENDAR_TODAY,
            width=300,
        )
        
        self.category_dropdown = Dropdown(
            label="Category",
            width=300,
            options=[
                ft.dropdown.Option("1", "Hardware"),
                ft.dropdown.Option("2", "Software"),
                ft.dropdown.Option("3", "Network"),
                ft.dropdown.Option("4", "Electrical"),
                ft.dropdown.Option("5", "Mechanical"),
            ],
            value=self.entry_data.get("category_id", "1"),
        )
        
        self.priority_dropdown = Dropdown(
            label="Priority",
            width=300,
            options=[
                ft.dropdown.Option("low", "Low"),
                ft.dropdown.Option("medium", "Medium"),
                ft.dropdown.Option("high", "High"),
            ],
            value=self.entry_data.get("priority", "medium"),
        )
        
        # File upload
        self.file_picker = ft.FilePicker(
            on_result=self.file_picker_result
        )
        
        self.selected_files = Text("No files selected")
    
    def file_picker_result(self, e):
        if e.files:
            file_names = [file.name for file in e.files]
            self.selected_files.value = f"Selected files: {', '.join(file_names)}"
        else:
            self.selected_files.value = "No files selected"
        self.selected_files.update()
    
    def build(self):
        return Card(
            content=Container(
                content=Column(
                    [
                        Container(
                            content=Text(
                                "Logbook Entry Form",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                            ),
                            padding=padding.only(bottom=20),
                        ),
                        
                        # Basic Information
                        Text(
                            "Basic Information",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        Container(
                            content=Row(
                                [
                                    self.start_date_field,
                                    self.responsible_person_field,
                                ],
                                wrap=True,
                                spacing=20,
                            ),
                            padding=padding.only(top=10, bottom=20),
                        ),
                        
                        # Location & Device
                        Text(
                            "Location & Device",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        Container(
                            content=Row(
                                [
                                    self.location_dropdown,
                                    self.device_field,
                                ],
                                wrap=True,
                                spacing=20,
                            ),
                            padding=padding.only(top=10, bottom=20),
                        ),
                        
                        # Description
                        Text(
                            "Description",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        Container(
                            content=Column(
                                [
                                    self.call_description_field,
                                    self.solution_description_field,
                                ],
                                spacing=20,
                            ),
                            padding=padding.only(top=10, bottom=20),
                        ),
                        
                        # Status & Timing
                        Text(
                            "Status & Timing",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        Container(
                            content=Row(
                                [
                                    self.status_dropdown,
                                    self.downtime_field,
                                    self.end_date_field,
                                ],
                                wrap=True,
                                spacing=20,
                            ),
                            padding=padding.only(top=10, bottom=20),
                        ),
                        
                        # Classification
                        Text(
                            "Classification",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        Container(
                            content=Row(
                                [
                                    self.category_dropdown,
                                    self.priority_dropdown,
                                ],
                                wrap=True,
                                spacing=20,
                            ),
                            padding=padding.only(top=10, bottom=20),
                        ),
                        
                        # Attachments
                        Text(
                            "Attachments",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        Container(
                            content=Column(
                                [
                                    Row(
                                        [
                                            ElevatedButton(
                                                "Select Files",
                                                icon=icons.UPLOAD_FILE,
                                                on_click=lambda _: self.file_picker.pick_files(
                                                    allow_multiple=True
                                                ),
                                            ),
                                            self.selected_files,
                                        ],
                                        spacing=20,
                                    ),
                                ],
                            ),
                            padding=padding.only(top=10, bottom=20),
                        ),
                        
                        # Form buttons
                        Row(
                            [
                                ElevatedButton(
                                    "Submit",
                                    icon=icons.SAVE,
                                    on_click=self.submit_form,
                                ),
                                OutlinedButton(
                                    "Cancel",
                                    icon=icons.CANCEL,
                                    on_click=self.cancel_form,
                                ),
                            ],
                            spacing=20,
                        ),
                    ],
                ),
                padding=padding.all(30),
                width=700,
            ),
            elevation=5,
        )
    
    def submit_form(self, e):
        """Handle form submission."""
        # Validate form
        if not self.validate_form():
            return
        
        # Collect form data
        form_data = {
            "start_date": self.start_date_field.value,
            "responsible_person": self.responsible_person_field.value,
            "location_id": self.location_dropdown.value,
            "device": self.device_field.value,
            "call_description": self.call_description_field.value,
            "solution_description": self.solution_description_field.value,
            "status": self.status_dropdown.value,
            "downtime_hours": self.downtime_field.value if self.downtime_field.value else None,
            "end_date": self.end_date_field.value if self.end_date_field.value else None,
            "category_id": self.category_dropdown.value,
            "priority": self.priority_dropdown.value,
        }
        
        # Call submit callback if provided
        if self.on_submit:
            self.on_submit(form_data)
    
    def cancel_form(self, e):
        """Handle form cancellation."""
        if self.on_cancel:
            self.on_cancel()
    
    def validate_form(self):
        """Validate form fields."""
        # Check required fields
        if not self.start_date_field.value:
            self.start_date_field.error_text = "Start date is required"
            self.update()
            return False
        
        if not self.responsible_person_field.value:
            self.responsible_person_field.error_text = "Responsible person is required"
            self.update()
            return False
        
        if not self.device_field.value:
            self.device_field.error_text = "Device is required"
            self.update()
            return False
        
        if not self.call_description_field.value:
            self.call_description_field.error_text = "Description is required"
            self.update()
            return False
        
        # Additional validation logic can be added here
        
        return True


class LogbookEntryList(UserControl):
    def __init__(self, on_view=None, on_edit=None, on_delete=None):
        super().__init__()
        self.on_view = on_view
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        # Sample data (would be replaced with API data)
        self.entries = [
            {
                "id": "1",
                "start_date": "2025-05-01",
                "responsible_person": "John Smith",
                "device": "Server #3",
                "call_description": "Server not responding to ping",
                "status": "completed",
                "location_name": "Server Room",
            },
            {
                "id": "2",
                "start_date": "2025-05-03",
                "responsible_person": "Jane Doe",
                "device": "Printer HP-2200",
                "call_description": "Paper jam, not printing",
                "status": "open",
                "location_name": "Office Building",
            },
            {
                "id": "3",
                "start_date": "2025-05-05",
                "responsible_person": "Mike Johnson",
                "device": "CNC Machine #2",
                "call_description": "Error code E-201 on startup",
                "status": "escalation",
                "location_name": "Production Floor",
            },
            {
                "id": "4",
                "start_date": "2025-05-06",
                "responsible_person": "Sarah Williams",
                "device": "Forklift #5",
                "call_description": "Battery not holding charge",
                "status": "open",
                "location_name": "Warehouse",
            },
        ]
        
        # Search field
        self.search_field = TextField(
            label="Search",
            icon=icons.SEARCH,
            hint_text="Search by device, description, or person",
            expand=True,
            on_change=self.filter_entries,
        )
        
        # Status filter
        self.status_filter = Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option("all", "All"),
                ft.dropdown.Option("open", "Open"),
                ft.dropdown.Option("completed", "Completed"),
                ft.dropdown.Option("escalation", "Escalation"),
            ],
            value="all",
            on_change=self.filter_entries,
        )
        
        # Data table
        self.data_table = self.build_data_table()
    
    def build_data_table(self):
        """Build the data table with current entries."""
        columns = [
            DataColumn(Text("Start Date")),
            DataColumn(Text("Responsible")),
            DataColumn(Text("Location")),
            DataColumn(Text("Device")),
            DataColumn(Text("Description")),
            DataColumn(Text("Status")),
            DataColumn(Text("Actions")),
        ]
        
        rows = []
        for entry in self.entries:
            # Define status color
            status_color = colors.GREY
            if entry["status"] == "open":
                status_color = colors.AMBER
            elif entry["status"] == "completed":
                status_color = colors.GREEN
            elif entry["status"] == "escalation":
                status_color = colors.RED
            
            # Create row
            rows.append(
                DataRow(
                    cells=[
                        DataCell(Text(entry["start_date"])),
                        DataCell(Text(entry["responsible_person"])),
                        DataCell(Text(entry["location_name"])),
                        DataCell(Text(entry["device"])),
                        DataCell(Text(entry["call_description"], max_lines=2)),
                        DataCell(
                            Container(
                                content=Text(
                                    entry["status"].capitalize(),
                                    color=colors.WHITE,
                                    size=12,
                                ),
                                bgcolor=status_color,
                                border_radius=20,
                                padding=padding.only(left=10, right=10, top=5, bottom=5),
                                alignment=ft.alignment.center,
                            )
                        ),
                        DataCell(
                            Row(
                                [
                                    IconButton(
                                        icon=icons.VISIBILITY,
                                        tooltip="View",
                                        icon_color=colors.BLUE,
                                        on_click=lambda e, id=entry["id"]: self.view_entry(id),
                                    ),
                                    IconButton(
                                        icon=icons.EDIT,
                                        tooltip="Edit",
                                        icon_color=colors.ORANGE,
                                        on_click=lambda e, id=entry["id"]: self.edit_entry(id),
                                    ),
                                    IconButton(
                                        icon=icons.DELETE,
                                        tooltip="Delete",
                                        icon_color=colors.RED,
                                        on_click=lambda e, id=entry["id"]: self.delete_entry(id),
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )
        
        return DataTable(
            columns=columns,
            rows=rows,
            border=ft.border.all(1, colors.BLUE_GREY_200),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, colors.BLUE_GREY_100),
            horizontal_lines=ft.border.BorderSide(1, colors.BLUE_GREY_100),
            sort_column_index=0,
            sort_ascending=False,
            heading_row_height=70,
            data_row_min_height=70,
            data_row_max_height=100,
            column_spacing=5,
            width=1000,
        )
    
    def build(self):
        return Column(
            [
                Row(
                    [
                        self.search_field,
                        self.status_filter,
                        ElevatedButton(
                            text="Add New",
                            icon=icons.ADD,
                            on_click=self.add_new_entry,
                        ),
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                Container(height=20),
                self.data_table,
            ],
            scroll=ft.ScrollMode.AUTO,
        )
    
    def filter_entries(self, e):
        """Filter entries based on search and status filter."""
        # TODO: Implement actual filtering with API
        # For now, just rebuild the table
        self.data_table = self.build_data_table()
        self.update()
    
    def view_entry(self, entry_id):
        """View entry details."""
        if self.on_view:
            self.on_view(entry_id)
    
    def edit_entry(self, entry_id):
        """Edit entry."""
        if self.on_edit:
            self.on_edit(entry_id)
    
    def delete_entry(self, entry_id):
        """Delete entry."""
        if self.on_delete:
            self.on_delete(entry_id)
    
    def add_new_entry(self, e):
        """Add new entry."""
        if self.on_edit:
            self.on_edit(None)  # None indicates a new entry


class LogbookView(UserControl):
    def __init__(self):
        super().__init__()
        self.show_form = False
        self.current_entry_id = None
        
        # Initialize views
        self.entry_list = LogbookEntryList(
            on_view=self.view_entry,
            on_edit=self.edit_entry,
            on_delete=self.delete_entry,
        )
        
        self.entry_form = None
    
    def build(self):
        content = Column(
            [
                Text(
                    "Logbook Entries",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                ),
                Container(height=20),
            ],
        )
        
        if self.show_form:
            self.entry_form = LogbookEntryForm(
                on_submit=self.submit_form,
                on_cancel=self.cancel_form,
                entry_data=self.get_entry_data(),
            )
            content.controls.append(self.entry_form)
        else:
            content.controls.append(self.entry_list)
        
        return Container(
            content=content,
            expand=True,
        )
    
    def view_entry(self, entry_id):
        """View entry details."""
        # TODO: Implement view entry details
        print(f"View entry {entry_id}")
    
    def edit_entry(self, entry_id):
        """Edit entry."""
        self.current_entry_id = entry_id
        self.show_form = True
        self.update()
    
    def delete_entry(self, entry_id):
        """Delete entry."""
        # TODO: Implement delete entry
        print(f"Delete entry {entry_id}")
    
    def submit_form(self, form_data):
        """Handle form submission."""
        # TODO: Implement form submission to API
        print(f"Submit form: {form_data}")
        self.show_form = False
        self.current_entry_id = None
        self.update()
    
    def cancel_form(self):
        """Handle form cancellation."""
        self.show_form = False
        self.current_entry_id = None
        self.update()
    
    def get_entry_data(self):
        """Get entry data for editing."""
        # TODO: Implement getting entry data from API
        if not self.current_entry_id:
            return {}
        
        # Sample data for demonstration
        if self.current_entry_id == "1":
            return {
                "start_date": "2025-05-01",
                "responsible_person": "John Smith",
                "location_id": "4",
                "device": "Server #3",
                "call_description": "Server not responding to ping",
                "solution_description": "Restarted server and updated network configuration",
                "status": "completed",
                "downtime_hours": "2.5",
                "end_date": "2025-05-01",
                "category_id": "3",
                "priority": "high",
            }
        
        return {}
