import flet as ft
import calendar
from flet import (
    Column,
    Container,
    Row,
    Text,
    TextField,
    ElevatedButton,
    IconButton,
    Dropdown,
    TextButton,
    Card,
    Icon,
    colors,
    icons,
    dropdown,
    padding,
    border_radius,
    margin
)
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from app.db.database import SessionLocal, get_db
from app.db.models import LogbookEntry
from app.utils.date_utils import format_date


class RecentActivityView(ft.Column):
    def __init__(self):
        super().__init__()
        self.entries = []
        self.filtered_entries = []
        
        # Filters
        self.start_date_picker = None
        self.start_date_value = None
        self.end_date_picker = None
        self.end_date_value = None
        self.status_dropdown = None
        self.search_field = None
        
        # Confirmation dialog
        self.delete_dialog = None
        self.entry_to_delete = None
        
        # Date picker dialog
        self.date_dialog = None
        self.is_start_date_selection = True
        self.selected_date = None
        
        # UI components
        self.entries_column = Column(scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Initialize filters with default values (last 30 days)
        self.init_date_range()
        
        # Create date picker dialog
        self.create_date_dialog()
        
        # Create filter components
        self.create_filter_components()
        
        # Create confirmation dialog
        self.create_delete_dialog()
        
        # Generate report button
        self.generate_report_button = ElevatedButton(
            "Generate Report",
            icon=icons.SUMMARIZE,
            on_click=self.handle_generate_report,
            style=ft.ButtonStyle(
                color=colors.WHITE,
                bgcolor=colors.BLUE_700,
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )
        
        # Main layout
        main_container = Container(
            content=Column([
                # Header with prominent home button
                Container(
                    content=Column([
                        Row([
                            ElevatedButton(
                                "Return Home",
                                icon=icons.HOME,
                                on_click=self.return_to_home,
                                style=ft.ButtonStyle(
                                    color=colors.WHITE,
                                    bgcolor=colors.BLUE_700,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                            ),
                            Text("Recent Activity", size=24, weight=ft.FontWeight.BOLD, color=colors.BLACK, expand=True, text_align=ft.TextAlign.CENTER),
                            self.generate_report_button,
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ]),
                    padding=padding.only(bottom=20),
                ),
                
                # Filters section
                Card(
                    content=Container(
                        content=Column([
                            Text("Filters", weight=ft.FontWeight.BOLD, size=16),
                            Row([
                                Container(
                                    content=Column([
                                        Text("Start Date"),
                                        self.start_date_picker,
                                    ]),
                                    expand=1,
                                ),
                                Container(
                                    content=Column([
                                        Text("End Date"),
                                        self.end_date_picker,
                                    ]),
                                    expand=1,
                                ),
                                Container(
                                    content=Column([
                                        Text("Status"),
                                        self.status_dropdown,
                                    ]),
                                    expand=1,
                                ),
                                Container(
                                    content=Column([
                                        Text("Search"),
                                        self.search_field,
                                    ]),
                                    expand=1,
                                ),
                            ]),
                            Row([
                                ElevatedButton(
                                    "Apply Filters",
                                    icon=icons.FILTER_ALT,
                                    on_click=self.apply_filters,
                                ),
                                ElevatedButton(
                                    "Reset Filters",
                                    icon=icons.CLEAR_ALL,
                                    on_click=self.reset_filters,
                                ),
                            ], alignment=ft.MainAxisAlignment.END),
                        ]),
                        padding=padding.all(20),
                    ),
                    elevation=2,
                    margin=margin.only(bottom=20),
                ),
                
                # Entries list
                Text("Recent Entries", weight=ft.FontWeight.BOLD, size=18, color=colors.BLACK),
                self.entries_column,
            ]),
            expand=True,
            padding=padding.all(20),
        )
        
        # Add the main container to this column
        self.expand = True
        self.controls = [main_container]
    
    def init_date_range(self):
        """Initialize default date range for filters (last 30 days)"""
        today = datetime.now()
        self.end_date_value = today
        self.start_date_value = today - timedelta(days=30)
    
    def did_mount(self):
        # This method is called when the control is added to the page
        # Load initial data
        self.load_entries()
        self.update()
        
    def build(self):
        # This method is no longer needed for ft.Column
        # It's kept for compatibility but doesn't do anything
        pass
    
    def create_filter_components(self):
        """Create filter UI components"""
        # Start date picker
        self.start_date_picker = TextField(
            value=self.start_date_value.strftime("%Y-%m-%d") if self.start_date_value else "",
            read_only=True,
            suffix_icon=icons.CALENDAR_TODAY,
            on_click=lambda e: self.show_date_picker("start"),
        )
        
        # End date picker
        self.end_date_picker = TextField(
            value=self.end_date_value.strftime("%Y-%m-%d") if self.end_date_value else "",
            read_only=True,
            suffix_icon=icons.CALENDAR_TODAY,
            on_click=lambda e: self.show_date_picker("end"),
        )
        
        # Status dropdown
        self.status_dropdown = Dropdown(
            options=[
                dropdown.Option("All"),
                dropdown.Option("Open"),
                dropdown.Option("Ongoing"),
                dropdown.Option("Completed"),
                dropdown.Option("Escalated"),
            ],
            value="All",
            width=200,
            bgcolor=colors.BLUE_GREY_800,
            color=colors.WHITE,
            focused_bgcolor=colors.BLUE_GREY_700,
            focused_color=colors.WHITE,
        )
        
        # Search field
        self.search_field = TextField(
            hint_text="Search by description, location, or responsible person",
            prefix_icon=icons.SEARCH,
            expand=True,
        )
    
    def create_delete_dialog(self):
        """Create confirmation dialog for delete operations"""
        self.delete_dialog = ft.AlertDialog(
            modal=True,
            title=Text("Confirm Deletion"),
            content=Text("Are you sure you want to delete this entry? This action cannot be undone."),
            actions=[
                TextButton("Cancel", on_click=self.close_delete_dialog),
                TextButton("Delete", on_click=self.confirm_delete, style=ft.ButtonStyle(color=colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def create_date_dialog(self):
        """Create a custom date picker dialog"""
        # Create month and year dropdowns
        current_year = datetime.now().year
        month_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(str(i), f"{calendar.month_name[i]}") 
                for i in range(1, 13)
            ],
            value=str(datetime.now().month),
            width=150,
            on_change=self.update_calendar,
        )
        
        year_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(str(year)) 
                for year in range(current_year - 5, current_year + 6)
            ],
            value=str(current_year),
            width=100,
            on_change=self.update_calendar,
        )
        
        # Create calendar grid
        calendar_grid = ft.Column(spacing=5)
        
        # Create date dialog
        self.date_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Select Date"),
            content=ft.Column([
                ft.Text("Click on a date to select it:"),
                ft.Container(height=10),  # Spacer
                ft.Row([
                    ft.ElevatedButton(
                        text="Today",
                        on_click=lambda e: self.set_date(datetime.now().date()),
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.BLUE_600,
                        ),
                    ),
                ]),
                ft.Container(height=10),  # Spacer
                ft.Row([
                    month_dropdown,
                    year_dropdown,
                ]),
                ft.Container(height=10),  # Spacer
                calendar_grid,
                ft.Container(height=10),  # Spacer
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_date_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
    def show_date_picker(self, date_type):
        """Show date picker for start or end date"""
        if self.page:
            # Set the flag to track which date field we're updating
            self.is_start_date_selection = (date_type == "start")
            
            # Update the dialog title based on which date we're selecting
            self.date_dialog.title = ft.Text("Select End Date" if not self.is_start_date_selection else "Select Start Date")
            
            # Add date dialog to page overlay if not already added
            if self.date_dialog not in self.page.overlay:
                self.page.overlay.append(self.date_dialog)
            
            # Update the calendar grid before showing the dialog
            self.update_calendar_grid()
            
            # Show the date dialog
            self.date_dialog.open = True
            self.page.update()
            
    def update_calendar(self, e):
        """Update calendar when month or year changes"""
        self.update_calendar_grid()
        self.page.update()
        
    def update_calendar_grid(self):
        """Update the calendar grid with days for the selected month and year"""
        # Get the dialog content column
        content_column = self.date_dialog.content
        
        # Get the row containing month and year dropdowns (index 4)
        month_year_row = content_column.controls[4]
        
        # Get the month and year dropdowns
        month_dropdown = month_year_row.controls[0]
        year_dropdown = month_year_row.controls[1]
        
        try:
            month = int(month_dropdown.value)
            year = int(year_dropdown.value)
        except (ValueError, TypeError):
            # Default to current month/year if there's an issue
            today = datetime.now()
            month = today.month
            year = today.year
            month_dropdown.value = str(month)
            year_dropdown.value = str(year)
        
        # Get the calendar grid column (index 6)
        calendar_grid = content_column.controls[6]
        calendar_grid.controls.clear()
        
        # Add day headers
        day_headers = ft.Row([
            ft.Container(
                ft.Text(day, size=14, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                width=40,
                height=30,
                alignment=ft.alignment.center
            ) for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        ])
        calendar_grid.controls.append(day_headers)
        
        # Get the calendar for the selected month
        cal = calendar.monthcalendar(year, month)
        
        # Add days to the grid
        for week in cal:
            week_row = ft.Row()
            for day in week:
                if day == 0:
                    # Empty cell for days not in this month
                    week_row.controls.append(
                        ft.Container(width=40, height=40)
                    )
                else:
                    # Create a date button
                    date_btn = ft.ElevatedButton(
                        text=str(day),
                        width=40,
                        height=40,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=5),
                        ),
                        data={"day": day, "month": month, "year": year},
                        on_click=self.day_clicked
                    )
                    week_row.controls.append(date_btn)
            calendar_grid.controls.append(week_row)
            
    def day_clicked(self, e):
        """Handle day button click in calendar"""
        day = e.control.data["day"]
        month = e.control.data["month"]
        year = e.control.data["year"]
        selected_date = datetime(year, month, day).date()
        self.set_date(selected_date)
        
    def set_date(self, date):
        """Set the selected date and update the appropriate text field"""
        self.selected_date = date
        formatted_date = date.strftime("%Y-%m-%d")
        
        if not self.is_start_date_selection:
            # Update end date field
            self.end_date_value = date
            self.end_date_picker.value = formatted_date
            print(f"End date set to: {formatted_date}")
        else:
            # Update start date field
            self.start_date_value = date
            self.start_date_picker.value = formatted_date
            print(f"Start date set to: {formatted_date}")
        
        # Close the dialog
        self.close_date_dialog(None)
        
        # Update the page
        self.update()
        
    def close_date_dialog(self, e):
        """Close the date dialog"""
        self.date_dialog.open = False
        self.page.update()
    
    def load_entries(self):
        """Load entries from database based on current filters"""
        with SessionLocal() as session:
            # Only show entries that are not marked as deleted
            query = session.query(LogbookEntry).filter(LogbookEntry.is_deleted == False).order_by(desc(LogbookEntry.created_at))
            
            # Apply date filters if set
            if self.start_date_value:
                query = query.filter(LogbookEntry.created_at >= self.start_date_value)
            if self.end_date_value:
                # Add one day to include entries from the end date
                end_date = self.end_date_value + timedelta(days=1)
                query = query.filter(LogbookEntry.created_at < end_date)
            
            # Apply status filter if not "All"
            if self.status_dropdown and self.status_dropdown.value != "All":
                query = query.filter(LogbookEntry.status == self.status_dropdown.value)
            
            # Apply search filter if provided
            if self.search_field and self.search_field.value:
                search_term = f"%{self.search_field.value}%"
                query = query.filter(
                    or_(
                        LogbookEntry.call_description.ilike(search_term),
                        LogbookEntry.responsible_person.ilike(search_term),
                        LogbookEntry.task.ilike(search_term),
                        LogbookEntry.device.ilike(search_term)
                    )
                )
            
            self.entries = query.all()
            self.filtered_entries = self.entries.copy()
            
            # Update UI
            self.update_entries_list()
    
    def update_entries_list(self):
        """Update the entries list in the UI"""
        self.entries_column.controls.clear()
        
        if not self.filtered_entries:
            self.entries_column.controls.append(
                Container(
                    content=Text("No entries found matching your filters", italic=True),
                    alignment=ft.alignment.center,
                    padding=20,
                )
            )
        else:
            for entry in self.filtered_entries:
                self.entries_column.controls.append(self.create_entry_card(entry))
        
        # Force a page update to refresh the UI
        self.page.update()
    
    def create_entry_card(self, entry):
        """Create a card for a single entry"""
        # Determine status color
        status_color = colors.BLUE
        if entry.status == "Open":
            status_color = colors.BLUE
        elif entry.status == "Ongoing":
            status_color = colors.PURPLE
        elif entry.status == "Completed":
            status_color = colors.GREEN
        elif entry.status == "Escalated":
            status_color = colors.RED
        
        return Card(
            content=Container(
                content=Column([
                    Row([
                        Text(
                            entry.call_description,
                            weight=ft.FontWeight.BOLD,
                            size=16,
                            expand=True,
                        ),
                        Container(
                            content=Text(
                                entry.status,
                                color=colors.WHITE,
                                size=12,
                                weight=ft.FontWeight.BOLD,
                            ),
                            bgcolor=status_color,
                            border_radius=border_radius.all(4),
                            padding=padding.only(left=8, right=8, top=4, bottom=4),
                        ),
                    ]),
                    Row([
                        Icon(icons.LOCATION_ON, color=colors.GREY, size=16),
                        Text(entry.location.name if entry.location else "Unknown Location", size=14),
                    ]),
                    Row([
                        Icon(icons.TASK_ALT, color=colors.GREY, size=16),
                        Text(f"Task: {entry.task if entry.task else 'Not specified'}", size=14),
                    ]),
                    Row([
                        Icon(icons.DEVICES, color=colors.GREY, size=16),
                        Text(f"Device: {entry.device}", size=14),
                    ]),
                    Row([
                        Icon(icons.PERSON, color=colors.GREY, size=16),
                        Text(f"Responsible: {entry.responsible_person}", size=14),
                    ]),
                    Row([
                        Icon(icons.CALENDAR_TODAY, color=colors.GREY, size=16),
                        Text(f"Created: {format_date(entry.created_at)}", size=14),
                    ]),
                    Row([
                        ElevatedButton(
                            "View Details",
                            icon=icons.VISIBILITY,
                            on_click=lambda e, entry_id=entry.id: self.view_entry_details(entry_id),
                            data=entry.id,  # Store ID in the button's data property as backup
                        ),
                        IconButton(
                            icon=icons.DELETE,
                            icon_color=colors.RED,
                            tooltip="Delete entry",
                            on_click=lambda e, entry_id=entry.id: self.delete_entry_by_id(entry_id),
                            data=entry.id,  # Store ID in the button's data property as backup
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ]),
                padding=15,
            ),
            elevation=2,
            margin=margin.only(bottom=10),
        )
    
    def apply_filters(self, e=None):
        """Apply current filters and reload entries"""
        self.load_entries()
    
    def reset_filters(self, e=None):
        """Reset filters to default values"""
        self.init_date_range()
        self.start_date_picker.value = self.start_date_value.strftime("%Y-%m-%d")
        self.end_date_picker.value = self.end_date_value.strftime("%Y-%m-%d")
        self.status_dropdown.value = "All"
        self.search_field.value = ""
        self.update()
        self.load_entries()
    
    def view_entry_details(self, entry_id):
        """View details of a specific entry"""
        print(f"Viewing entry {entry_id}")
        
        # Find the entry in our filtered entries list
        entry = None
        for e in self.filtered_entries:
            if str(e.id) == str(entry_id):
                entry = e
                break
        
        if not entry:
            print(f"Entry with ID {entry_id} not found in filtered entries")
            # Show error message to user
            self.page.snack_bar = ft.SnackBar(content=Text(f"Entry not found"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Create a details dialog
        details_dialog = ft.AlertDialog(
            modal=True,
            title=Text("Entry Details", weight=ft.FontWeight.BOLD),
            content=Container(
                content=Column([
                    Container(height=10),
                    Row([Text("ID:", weight=ft.FontWeight.BOLD), Text(str(entry.id))]),
                    Container(height=10),
                    Row([Text("Description:", weight=ft.FontWeight.BOLD), Text(entry.call_description)]),
                    Container(height=10),
                    Row([Text("Status:", weight=ft.FontWeight.BOLD), Text(entry.status)]),
                    Container(height=10),
                    Row([Text("Location:", weight=ft.FontWeight.BOLD), Text(entry.location.name if entry.location else "Unknown")]),
                    Container(height=10),
                    Row([Text("Device:", weight=ft.FontWeight.BOLD), Text(entry.device)]),
                    Container(height=10),
                    Row([Text("Task:", weight=ft.FontWeight.BOLD), Text(entry.task if entry.task else "Not specified")]),
                    Container(height=10),
                    Row([Text("Responsible Person:", weight=ft.FontWeight.BOLD), Text(entry.responsible_person)]),
                    Container(height=10),
                    Row([Text("Created At:", weight=ft.FontWeight.BOLD), Text(format_date(entry.created_at))]),
                    Container(height=10),
                    Row([Text("Updated At:", weight=ft.FontWeight.BOLD), Text(format_date(entry.updated_at))]),
                    Container(height=10),
                    # Add more fields as needed
                ], scroll=ft.ScrollMode.AUTO),
                width=400,
                height=400,
                padding=padding.all(20),
            ),
            actions=[
                TextButton("Close", on_click=lambda e: self.close_details_dialog(e)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Show the dialog
        self.page.dialog = details_dialog
        self.page.dialog.open = True
        self.page.update()
        
    def close_details_dialog(self, e):
        """Close the details dialog"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
        
    def delete_entry_by_id(self, entry_id):
        """Show confirmation dialog before deleting an entry by ID"""
        print(f"Preparing to delete entry with ID: {entry_id}")
        # Find the entry in our filtered entries list
        for entry in self.filtered_entries:
            if str(entry.id) == str(entry_id):
                self.entry_to_delete = entry
                # Make sure the delete dialog exists
                if not self.delete_dialog:
                    self.create_delete_dialog()
                # Set the dialog content to include the entry description
                self.delete_dialog.title = Text("Delete Entry")
                self.delete_dialog.content = Text(f"Are you sure you want to delete the entry:\n\n{entry.call_description}?")
                # Show the dialog
                self.page.dialog = self.delete_dialog
                self.page.dialog.open = True
                self.page.update()
                return
    
        # If we get here, the entry wasn't found
        print(f"Entry with ID {entry_id} not found in filtered entries")
        self.page.snack_bar = ft.SnackBar(content=Text("Entry not found"))
        self.page.snack_bar.open = True
        self.page.update()
        
    def close_delete_dialog(self, e=None):
        """Close the delete confirmation dialog"""
        if self.delete_dialog:
            self.delete_dialog.open = False
            self.page.update()
    
    def confirm_delete(self, e=None):
        """Soft delete the entry after confirmation (mark as deleted)"""
        print(f"Confirming deletion of entry: {self.entry_to_delete.id if self.entry_to_delete else 'None'}")
        success = False
        if self.entry_to_delete:
            try:
                with SessionLocal() as session:
                    entry = session.query(LogbookEntry).filter(LogbookEntry.id == self.entry_to_delete.id).first()
                    if entry:
                        print(f"Found entry to mark as deleted: {entry.id}")
                        # Soft delete - set is_deleted flag to True instead of removing the record
                        entry.is_deleted = True
                        session.commit()
                        print("Entry marked as deleted successfully")
                        success = True
                    else:
                        print(f"Entry not found with ID: {self.entry_to_delete.id}")
            except Exception as ex:
                print(f"Error marking entry as deleted: {ex}")
        
        # Close dialog and reload entries
        self.close_delete_dialog()
        if success:
            # Remove the entry from the filtered_entries list
            self.filtered_entries = [e for e in self.filtered_entries if e.id != self.entry_to_delete.id]
            # Update the UI directly instead of reloading from database
            self.update_entries_list()
            # Also reload from database to ensure consistency
            self.load_entries()
    
    def return_to_home(self, e=None):
        """Navigate back to the home/dashboard page"""
        if hasattr(self.page, "go"):
            self.page.go("/")
        else:
            print("Navigation not available")
    
    def handle_generate_report(self, e=None):
        """Generate a report based on current filtered entries"""
        if not self.filtered_entries:
            # Show a message if there are no entries to include in the report
            self.page.snack_bar = ft.SnackBar(
                content=Text("No entries to include in the report"),
                action="OK",
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
            
        # Create a new report in the database
        with SessionLocal() as session:
            from app.db.models import Report
            import uuid
            
            # Get current user ID (assuming it's available in the page data)
            user_id = self.page.data.get("user_id") if hasattr(self.page, "data") else None
            
            # Create report parameters from current filters
            parameters = {
                "start_date": self.start_date_value.strftime("%Y-%m-%d") if self.start_date_value else None,
                "end_date": self.end_date_value.strftime("%Y-%m-%d") if self.end_date_value else None,
                "status": self.status_dropdown.value if self.status_dropdown else None,
                "search": self.search_field.value if self.search_field else None,
                "entry_count": len(self.filtered_entries)
            }
            
            # Create a new report record
            new_report = Report(
                id=uuid.uuid4(),
                name=f"Activity Report {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                parameters=parameters,
                start_date=self.start_date_value,
                end_date=self.end_date_value,
                file_type="PDF",
                status="generated",
                created_by_id=user_id
            )
            
            session.add(new_report)
            session.commit()
            
            # Show success message
            self.page.snack_bar = ft.SnackBar(
                content=Text(f"Report generated successfully with {len(self.filtered_entries)} entries"),
                action="OK",
            )
            self.page.snack_bar.open = True
            self.page.update()
            
            # Navigate to the Reports view
            if hasattr(self.page, "go"):
                self.page.go("/reports")
