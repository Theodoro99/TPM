import flet as ft
from flet import (
    Column, 
    Container, 
    Row, 
    Text, 
    TextField, 
    ElevatedButton, 
    Dropdown, 
    dropdown,
    DataTable,
    DataColumn,
    DataRow,
    DataCell,
    icons,
    colors,
    padding,
    border,
    border_radius,
)
from datetime import datetime

class SearchView(ft.Column):
    """A view component for searching and displaying logbook entries.

    This class provides a user interface for searching logbook entries with various filters
    and displaying the results in a table format. It includes functionality for viewing
    and editing individual entries.

    Attributes:
        on_search (callable): Callback function to execute when search is performed.
        on_back (callable): Callback function to execute when back button is clicked.
        expand (bool): Whether the view should expand to fill available space.
        scroll (ScrollMode): Scroll behavior of the view.
        keyword_field (TextField): Input field for search keyword.
        status_dropdown (Dropdown): Dropdown for filtering by status.
        priority_dropdown (Dropdown): Dropdown for filtering by priority.
        results_table (DataTable): Table for displaying search results.
    """

    def __init__(self, on_search=None, on_back=None):
        """Initialize the SearchView component.

        Args:
            on_search (callable, optional): Callback function for search operations.
                Receives search parameters as a dictionary.
            on_back (callable, optional): Callback function for back button clicks.
        """

        super().__init__()
        self.on_search = on_search
        self.on_back = on_back
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        
        # Search fields
        self.keyword_field = TextField(
            label="Keyword",
            hint_text="Search by keyword",
            border=ft.InputBorder.OUTLINE,
            expand=True,
            color=colors.BLACK,
            label_style=ft.TextStyle(color=colors.BLACK),
            hint_style=ft.TextStyle(color=colors.BLACK87),
        )
        
        self.status_dropdown = Dropdown(
            label="Status",
            hint_text="Filter by status",
            options=[
                dropdown.Option("All"),
                dropdown.Option("Open"),
                dropdown.Option("Completed"),
                dropdown.Option("Escalation"),
            ],
            border=ft.InputBorder.OUTLINE,
            expand=True,
            bgcolor=colors.WHITE,
            color=colors.BLACK,
            focused_bgcolor=colors.BLUE_50,
            focused_color=colors.BLACK,
            focused_border_color=colors.BLUE,
        )
        
        self.priority_dropdown = Dropdown(
            label="Priority",
            hint_text="Filter by priority",
            options=[
                dropdown.Option("All"),
                dropdown.Option("Low"),
                dropdown.Option("Medium"),
                dropdown.Option("High"),
            ],
            border=ft.InputBorder.OUTLINE,
            expand=True,
            bgcolor=colors.WHITE,
            color=colors.BLACK,
            focused_bgcolor=colors.BLUE_50,
            focused_color=colors.BLACK,
            focused_border_color=colors.BLUE,
        )
        
        # Results table
        self.results_table = DataTable(
            columns=[
                DataColumn(Text("ID")),
                DataColumn(Text("Device")),
                DataColumn(Text("Description")),
                DataColumn(Text("Status")),
                DataColumn(Text("Priority")),
                DataColumn(Text("Date")),
                DataColumn(Text("Actions")),
            ],
            rows=[],
            border=border.all(1, colors.GREY_300),
            border_radius=border_radius.all(5),
            vertical_lines=ft.border.BorderSide(1, colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, colors.GREY_300),
            sort_column_index=5,
            sort_ascending=False,
            heading_row_height=50,
            data_row_min_height=50,
            data_row_max_height=80,
            column_spacing=10,
            expand=True,
        )
        
        # Build the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface components and layout.

        This method creates and arranges all UI elements including search fields,
        results table, and navigation buttons.
        """

        # Create search container
        search_container = Container(
            content=Column(
                [
                    Text(
                        "Search Logbook Entries",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=colors.BLACK,
                    ),
                    Container(height=20),
                    
                    # Search fields
                    Row(
                        [
                            self.keyword_field,
                            Container(width=10),
                            self.status_dropdown,
                            Container(width=10),
                            self.priority_dropdown,
                            Container(width=10),
                            ElevatedButton(
                                "Search",
                                icon=icons.SEARCH,
                                on_click=self.handle_search,
                                style=ft.ButtonStyle(
                                    color=colors.WHITE,
                                    bgcolor=colors.BLUE_500,
                                ),
                            ),
                        ],
                        spacing=5,
                    ),
                    Container(height=20),
                    
                    # Results
                    Container(
                        content=Column(
                            [
                                Text(
                                    "Search Results",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                Container(height=10),
                                self.results_table,
                            ],
                        ),
                        padding=padding.all(10),
                        bgcolor=colors.WHITE,
                        border_radius=border_radius.all(5),
                        border=border.all(1, colors.GREY_300),
                        expand=True,
                    ),
                    Container(height=20),
                    
                    # Back button
                    Row(
                        [
                            ElevatedButton(
                                "Back to Dashboard",
                                icon=icons.ARROW_BACK,
                                on_click=self.handle_back,
                                style=ft.ButtonStyle(
                                    color=colors.WHITE,
                                    bgcolor=colors.GREY_500,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=padding.all(20),
            bgcolor=colors.WHITE,
            border_radius=border_radius.all(10),
            border=border.all(1, colors.GREY_300),
            expand=True,
        )
        
        self.controls = [search_container]
    
    def handle_search(self, e):
        """Handle the search button click event.

        Collects search parameters from input fields and executes the search operation.
        If no callback is provided, displays demo results.

        Args:
            e: The event object from the button click.
        """

        # Get search criteria
        keyword = self.keyword_field.value
        status = self.status_dropdown.value
        priority = self.priority_dropdown.value
        
        # Create search parameters
        search_params = {
            "keyword": keyword,
            "status": status if status != "All" else None,
            "priority": priority if priority != "All" else None,
        }
        
        # Call the search callback
        if self.on_search:
            results = self.on_search(search_params)
            self.update_results_table(results)
        else:
            # Placeholder for demo
            self.show_demo_results()
    
    def update_results_table(self, results):
        """Update the results table with new data.

        Args:
            results (list): A list of dictionaries containing logbook entry data.
                Each dictionary should contain keys: id, device, description,
                status, priority, and date.
        """

        # Clear existing rows
        self.results_table.rows.clear()
        
        # Add rows for each result
        for result in results:
            row = DataRow(
                cells=[
                    DataCell(Text(str(result.get("id", "")))),
                    DataCell(Text(result.get("device", ""))),
                    DataCell(Text(result.get("description", ""))),
                    DataCell(Text(result.get("status", ""))),
                    DataCell(Text(result.get("priority", ""))),
                    DataCell(Text(result.get("date", ""))),
                    DataCell(
                        Row(
                            [
                                ft.IconButton(
                                    icon=icons.VISIBILITY,
                                    tooltip="View",
                                    on_click=lambda e, id=result.get("id"): self.handle_view(id),
                                ),
                                ft.IconButton(
                                    icon=icons.EDIT,
                                    tooltip="Edit",
                                    on_click=lambda e, id=result.get("id"): self.handle_edit(id),
                                ),
                            ],
                            spacing=0,
                        )
                    ),
                ]
            )
            self.results_table.rows.append(row)
        
        # Update the UI
        self.update()
    
    def show_demo_results(self):
        """Display demonstration results in the table.

        This method is used when no search callback is provided, showing sample data
        for demonstration purposes.
        """

        # Sample results for demonstration
        demo_results = [
            {
                "id": "1",
                "device": "Fire Extinguisher",
                "description": "Quarterly inspection of fire extinguishers",
                "status": "Completed",
                "priority": "High",
                "date": "2025-04-15",
            },
            {
                "id": "2",
                "device": "HVAC System",
                "description": "Annual maintenance check",
                "status": "Open",
                "priority": "Medium",
                "date": "2025-05-01",
            },
            {
                "id": "3",
                "device": "Chemical Storage",
                "description": "Chemical spill in laboratory area",
                "status": "Escalation",
                "priority": "High",
                "date": "2025-05-05",
            },
        ]
        
        self.update_results_table(demo_results)
    
    def handle_view(self, entry_id):
        """Handle the view action for a specific logbook entry.

        Displays a modal dialog with details for the specified entry.

        Args:
            entry_id (str): The ID of the entry to view.
        """

        # Show details dialog
        if self.page:
            def close_dlg(e):
                dlg_modal.open = False
                self.page.update()
                
            dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text(f"Entry Details (ID: {entry_id})"),
                content=ft.Text("Entry details will be displayed here."),
                actions=[
                    ft.TextButton("Close", on_click=close_dlg),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            self.page.dialog = dlg_modal
            dlg_modal.open = True
            self.page.update()
    
    def handle_edit(self, entry_id):
        """Handle the edit action for a specific logbook entry.

        Displays a modal dialog for editing the specified entry.

        Args:
            entry_id (str): The ID of the entry to edit.
        """

        # Show edit dialog
        if self.page:
            def close_dlg(e):
                dlg_modal.open = False
                self.page.update()
                
            dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text(f"Edit Entry (ID: {entry_id})"),
                content=ft.Text("Edit form will be displayed here."),
                actions=[
                    ft.TextButton("Cancel", on_click=close_dlg),
                    ft.TextButton("Save", on_click=close_dlg),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            self.page.dialog = dlg_modal
            dlg_modal.open = True
            self.page.update()
    
    def handle_back(self, e):
        """Handle the back button click event.

        Executes the back callback if one is provided.

        Args:
            e: The event object from the button click.
        """
        if self.on_back:
            self.on_back()
