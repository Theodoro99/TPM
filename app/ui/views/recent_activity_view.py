import flet as ft
import calendar
from datetime import datetime, timedelta, time
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
    margin,
)
from sqlalchemy import desc, or_
from app.db.database import SessionLocal
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
                            Text("Recent Activity", size=24, weight=ft.FontWeight.BOLD, color=colors.BLACK, expand=True,
                                 text_align=ft.TextAlign.CENTER),
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
            self.date_dialog.title = ft.Text(
                "Select End Date" if not self.is_start_date_selection else "Select Start Date")

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
            # Get all entries ordered by creation date (newest first)
            # No need to filter by is_deleted since we're now using hard delete
            query = session.query(LogbookEntry).order_by(desc(LogbookEntry.created_at))

            # Apply date filters if set
            if self.start_date_value:
                query = query.filter(LogbookEntry.created_at >= self.start_date_value)
            if self.end_date_value:
                # Add one day to include entries from the end date
                end_date = self.end_date_value + timedelta(days=1)
                query = query.filter(LogbookEntry.created_at < end_date)

            # Apply status filter if not "All"
            if self.status_dropdown and self.status_dropdown.value != "All":
                # Map dropdown values to StatusEnum values
                status_map = {
                    "Open": "open",
                    "Ongoing": "ongoing",
                    "Completed": "completed",
                    "Escalated": "escalation"  # Note: dropdown has "Escalated" but enum has "escalation"
                }
                if self.status_dropdown.value in status_map:
                    query = query.filter(LogbookEntry.status == status_map[self.status_dropdown.value])

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

            try:
                self.entries = query.all()
                self.filtered_entries = self.entries.copy()
                print(f"Loaded {len(self.entries)} entries from database")
            except Exception as ex:
                print(f"Error loading entries: {ex}")
                self.entries = []
                self.filtered_entries = []

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
        """Create a card for a single entry with comprehensive details"""
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

        # Determine priority color if available
        priority_color = colors.GREY
        priority_text = "Medium"
        if hasattr(entry, 'priority') and entry.priority:
            if entry.priority == "high":
                priority_color = colors.RED
                priority_text = "High"
            elif entry.priority == "medium":
                priority_color = colors.ORANGE
                priority_text = "Medium"
            elif entry.priority == "low":
                priority_color = colors.GREEN
                priority_text = "Low"

        # Format dates for better readability
        start_date = format_date(entry.start_date) if entry.start_date else "Not specified"
        end_date = format_date(entry.end_date) if entry.end_date else "Not specified"
        created_date = format_date(entry.created_at) if entry.created_at else "Unknown"
        updated_date = format_date(entry.updated_at) if entry.updated_at else "Not updated"

        # Format resolution time if available
        resolution_time = "Not specified"
        if entry.resolution_time:
            if isinstance(entry.resolution_time, datetime):
                resolution_time = entry.resolution_time.strftime("%H:%M")
            else:
                resolution_time = str(entry.resolution_time)

        # Create a preview of the call description (first 100 chars)
        description_preview = entry.call_description
        if len(description_preview) > 100:
            description_preview = description_preview[:97] + "..."

        # Create a preview of the solution description if available
        solution_preview = "No solution provided"
        if entry.solution_description and entry.solution_description.strip():
            solution_preview = entry.solution_description
            if len(solution_preview) > 100:
                solution_preview = solution_preview[:97] + "..."

        return Card(
            content=Container(
                content=Column([
                    # Header with ID and status
                    Row([
                        Container(
                            content=Text(
                                str(entry.id).split("-")[0],  # Show first part of UUID
                                color=colors.WHITE,
                                size=12,
                                italic=True,
                            ),
                            padding=padding.only(right=5),
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
                        # Add priority badge if available
                        Container(
                            content=Text(
                                f"Priority: {priority_text}",
                                color=colors.WHITE,
                                size=12,
                            ),
                            bgcolor=priority_color,
                            border_radius=border_radius.all(4),
                            padding=padding.only(left=8, right=8, top=4, bottom=4),
                            margin=margin.only(left=5),
                        ) if hasattr(entry, 'priority') and entry.priority else Container(),
                    ], alignment=ft.MainAxisAlignment.END),

                    # Title - Call Description
                    Container(
                        content=Text(
                            description_preview,
                            weight=ft.FontWeight.BOLD,
                            size=16,
                            color=colors.WHITE,
                        ),
                        margin=margin.only(top=5, bottom=10),
                    ),

                    # Main information grid
                    Container(
                        content=Column([
                            # Row 1: Location and Device
                            Row([
                                Container(
                                    content=Row([
                                        Icon(icons.LOCATION_ON, color=colors.ORANGE_300, size=16),
                                        Text(entry.location.name if entry.location else "Unknown Location", size=14,
                                             color=colors.WHITE),
                                    ]),
                                    expand=True,
                                ),
                                Container(
                                    content=Row([
                                        Icon(icons.DEVICES, color=colors.ORANGE_300, size=16),
                                        Text(entry.device, size=14, color=colors.WHITE),
                                    ]),
                                    expand=True,
                                ),
                            ]),

                            # Row 2: Task and Responsible Person
                            Row([
                                Container(
                                    content=Row([
                                        Icon(icons.TASK_ALT, color=colors.ORANGE_300, size=16),
                                        Text(entry.task if entry.task else "Not specified", size=14,
                                             color=colors.WHITE),
                                    ]),
                                    expand=True,
                                ),
                                Container(
                                    content=Row([
                                        Icon(icons.PERSON, color=colors.ORANGE_300, size=16),
                                        Text(entry.responsible_person, size=14, color=colors.WHITE),
                                    ]),
                                    expand=True,
                                ),
                            ]),

                            # Row 3: Start and End Dates
                            Row([
                                Container(
                                    content=Row([
                                        Icon(icons.EVENT_AVAILABLE, color=colors.ORANGE_300, size=16),
                                        Text(f"Start: {start_date}", size=14, color=colors.WHITE),
                                    ]),
                                    expand=True,
                                ),
                                Container(
                                    content=Row([
                                        Icon(icons.EVENT_BUSY, color=colors.ORANGE_300, size=16),
                                        Text(f"End: {end_date}", size=14, color=colors.WHITE),
                                    ]),
                                    expand=True,
                                ),
                            ]),

                            # Row 4: Resolution Time and Category
                            Row([
                                Container(
                                    content=Row([
                                        Icon(icons.TIMER, color=colors.ORANGE_300, size=16),
                                        Text(f"Resolution: {resolution_time}", size=14, color=colors.WHITE),
                                    ]),
                                    expand=True,
                                ),
                                Container(
                                    content=Row([
                                        Icon(icons.CATEGORY, color=colors.ORANGE_300, size=16),
                                        Text(
                                            entry.category.name if hasattr(entry,
                                                                           'category') and entry.category else "Not categorized",
                                            size=14,
                                            color=colors.WHITE
                                        ),
                                    ]),
                                    expand=True,
                                ),
                            ]),

                            # Row 5: Created and Updated dates
                            Row([
                                Container(
                                    content=Row([
                                        Icon(icons.CALENDAR_TODAY, color=colors.ORANGE_300, size=16),
                                        Text(f"Created: {created_date}", size=14, color=colors.WHITE),
                                    ]),
                                    expand=True,
                                ),
                                Container(
                                    content=Row([
                                        Icon(icons.UPDATE, color=colors.ORANGE_300, size=16),
                                        Text(f"Updated: {updated_date}", size=14, color=colors.WHITE),
                                    ]),
                                    expand=True,
                                ),
                            ]),
                        ]),
                        margin=margin.only(bottom=10),
                    ),

                    # Solution preview if available
                    Container(
                        content=Column([
                            Text("Solution:", weight=ft.FontWeight.BOLD, size=14, color=colors.WHITE),
                            Container(
                                content=Text(solution_preview, size=14, color=colors.WHITE),
                                margin=margin.only(top=5),
                            ),
                            # Action buttons row
                            Row([
                                Container(
                                    content=Text(
                                        str(entry.id).split("-")[0],  # Show first part of UUID
                                        color=colors.WHITE,
                                        size=12,
                                        italic=True,
                                    ),
                                    padding=padding.only(right=5),
                                ),
                                IconButton(
                                    icon=icons.EDIT,
                                    icon_color=colors.BLUE,
                                    tooltip="Edit entry",
                                    on_click=lambda e, entry_id=entry.id: self.edit_entry_by_id(entry_id),
                                    data=entry.id,
                                ),
                                IconButton(
                                    icon=icons.DELETE,
                                    icon_color=colors.RED,
                                    tooltip="Delete entry",
                                    on_click=lambda e, entry_id=entry.id: self.delete_entry_by_id(entry_id),
                                    data=entry.id,
                                ),
                            ]),
                        ]),
                        margin=margin.only(bottom=10),
                        visible=True if entry.solution_description and entry.solution_description.strip() else False,
                    ),
                ]),
                padding=20,
                bgcolor=colors.GREY_900,
                border_radius=border_radius.all(8),
            ),
            elevation=3,
            margin=margin.only(bottom=15),
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

    def view_entry_details(self, entry_id, e=None):
        """View details of a specific entry"""
        print(f"Viewing entry {entry_id}")

        # Convert entry_id to string for consistent comparison
        entry_id_str = str(entry_id).lower().strip()

        # Find the entry in our filtered entries list
        entry = None
        for e in self.filtered_entries:
            if str(e.id).lower().strip() == entry_id_str:
                entry = e
                break

        # If not found in memory, try to fetch from database
        if not entry:
            try:
                with SessionLocal() as session:
                    # Try direct query with the UUID object
                    try:
                        db_entry = session.query(LogbookEntry).get(entry_id)
                        if db_entry:
                            entry = db_entry
                    except Exception as ex:
                        print(f"Error querying by ID directly: {ex}")

                    # If still not found, try string comparison
                    if not entry:
                        all_entries = session.query(LogbookEntry).all()
                        for e in all_entries:
                            if str(e.id).lower().strip() == entry_id_str:
                                entry = e
                                break
            except Exception as ex:
                print(f"Database error while finding entry: {ex}")

        if not entry:
            print(f"Entry with ID {entry_id} not found in filtered entries or database")
            # Show error message to user
            self.page.snack_bar = ft.SnackBar(content=Text("Entry not found"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        print(f"Found entry: {entry.id}, creating details dialog")

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
                    Row([Text("Location:", weight=ft.FontWeight.BOLD),
                         Text(entry.location.name if entry.location else "Unknown")]),
                    Container(height=10),
                    Row([Text("Device:", weight=ft.FontWeight.BOLD), Text(entry.device)]),
                    Container(height=10),
                    Row([Text("Task:", weight=ft.FontWeight.BOLD),
                         Text(entry.task if entry.task else "Not specified")]),
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
        print("Setting up dialog to display entry details")
        self.page.dialog = details_dialog
        self.page.dialog.open = True
        print("Dialog should be visible now")
        self.page.update()
        print("Page updated with dialog")

    def close_details_dialog(self, e=None):
        """Close the details dialog"""
        print("Closing details dialog")
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
            print("Dialog closed")

    def close_delete_dialog(self, e=None):
        """Close the delete confirmation dialog"""
        print("Closing delete dialog")
        if self.delete_dialog:
            self.delete_dialog.open = False
            self.page.update()
            print("Delete dialog closed")

    def delete_entry_by_id(self, entry_id, e=None):
        """Show confirmation dialog before deleting an entry by ID"""
        # Disable the button that triggered this method to prevent multiple clicks
        if e and hasattr(e, 'control') and e.control:
            e.control.disabled = True
            self.page.update()

        print(f"Preparing to delete entry with ID: {entry_id}")

        # Convert entry_id to string for consistent comparison
        entry_id_str = str(entry_id).lower().strip()

        # Directly delete from database without confirmation dialog
        try:
            # Create a new session for this transaction
            session = SessionLocal()
            try:
                # Try direct query with the UUID object
                entry = session.query(LogbookEntry).get(entry_id)

                if not entry:
                    # Try to find by string comparison
                    all_entries = session.query(LogbookEntry).all()
                    for e in all_entries:
                        if str(e.id).lower().strip() == entry_id_str:
                            entry = e
                            break

                if entry:
                    print(f"Found entry to delete: {entry.id}")
                    # HARD DELETE - completely remove the record from the database
                    session.delete(entry)
                    session.commit()
                    print("Entry deleted successfully from database")

                    # Remove from UI lists
                    self.entries = [e for e in self.entries if str(e.id).lower().strip() != entry_id_str]
                    self.filtered_entries = [e for e in self.filtered_entries if
                                             str(e.id).lower().strip() != entry_id_str]

                    # Update UI
                    self.update_entries_list()

                    # Show success message
                    self.page.snack_bar = ft.SnackBar(
                        content=Text("Entry deleted successfully"),
                        action="OK",
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                else:
                    print(f"Entry not found with ID: {entry_id}")
                    self.page.snack_bar = ft.SnackBar(
                        content=Text("Entry not found"),
                        action="OK",
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            except Exception as ex:
                # Rollback on error
                session.rollback()
                print(f"Error deleting entry: {ex}")
                self.page.snack_bar = ft.SnackBar(
                    content=Text(f"Error deleting entry: {str(ex)}"),
                    action="OK",
                )
                self.page.snack_bar.open = True
                self.page.update()
            finally:
                # Always close the session
                session.close()
        except Exception as ex:
            print(f"Database error during deletion: {ex}")
            self.page.snack_bar = ft.SnackBar(
                content=Text(f"Database error: {str(ex)}"),
                action="OK",
            )
            self.page.snack_bar.open = True
            self.page.update()

    # close_delete_dialog method is defined below - no need to duplicate it

    def confirm_delete(self, e=None):
        """Hard delete the entry after confirmation (completely remove from database)"""
        print(f"Confirming deletion of entry: {self.entry_to_delete.id if self.entry_to_delete else 'None'}")
        success = False
        entry_id_to_remove = None

        if self.entry_to_delete:
            entry_id_to_remove = self.entry_to_delete.id
            try:
                # Create a new session for this transaction
                session = SessionLocal()
                try:
                    # Convert UUID to string for consistent comparison
                    entry_id_str = str(entry_id_to_remove).lower().strip()
                    print(f"Looking for entry with ID string: {entry_id_str}")

                    # Try direct query first with the UUID object
                    entry = session.query(LogbookEntry).get(entry_id_to_remove)

                    # If not found, try to find by string comparison
                    if not entry:
                        print("Entry not found by direct get, trying string comparison...")
                        all_entries = session.query(LogbookEntry).all()
                        for e in all_entries:
                            if str(e.id).lower().strip() == entry_id_str:
                                entry = e
                                print(f"Found entry by string comparison: {e.id}")
                                break

                    if entry:
                        print(f"Found entry to delete: {entry.id}")
                        # HARD DELETE - completely remove the record from the database
                        session.delete(entry)
                        session.commit()
                        print("Entry deleted successfully from database")
                        success = True
                    else:
                        print(f"Entry not found with ID: {entry_id_to_remove}")
                except Exception as ex:
                    # Rollback on error
                    session.rollback()
                    print(f"Error deleting entry: {ex}")
                finally:
                    # Always close the session
                    session.close()
            except Exception as ex:
                print(f"Database error during deletion: {ex}")

        # Close dialog first
        self.close_delete_dialog()

        if success:
            # Remove the deleted entry from our local lists to update UI immediately
            if entry_id_to_remove:
                entry_id_str = str(entry_id_to_remove).lower().strip()
                self.entries = [e for e in self.entries if str(e.id).lower().strip() != entry_id_str]
                self.filtered_entries = [e for e in self.filtered_entries if str(e.id).lower().strip() != entry_id_str]

            # Update the entries list in the UI
            self.update_entries_list()

            # Show success message
            self.page.snack_bar = ft.SnackBar(
                content=Text("Entry deleted successfully"),
                action="OK",
            )
            self.page.snack_bar.open = True

            # Force UI update
            self.page.update()

            # Reload entries from database to ensure consistency
            self.load_entries()
        else:
            # Show error message
            self.page.snack_bar = ft.SnackBar(
                content=Text("Failed to delete entry. Please try again."),
                action="OK",
            )
            self.page.snack_bar.open = True
            self.page.update()

    def return_to_home(self, e=None):
        """Navigate back to the home/dashboard page"""
        if hasattr(self.page, "go"):
            self.page.go("/")
        else:
            print("Navigation not available")

    def edit_entry_by_id(self, entry_id):
        """Edit an existing entry by ID"""
        # Import here to avoid circular imports
        from app.ui.views.new_entry_view import NewEntryView

        # Find the entry in the database
        with SessionLocal() as session:
            entry = session.query(LogbookEntry).filter(LogbookEntry.id == entry_id).first()

            if not entry:
                # Show error message if entry not found
                self.page.snack_bar = ft.SnackBar(
                    content=Text(f"Entry with ID {entry_id} not found"),
                    action="OK",
                )
                self.page.snack_bar.open = True
                self.page.update()
                return

            # Create a handler for saving the edited entry
            def handle_save(entry_data):
                try:
                    # Update the entry in the database
                    with SessionLocal() as update_session:
                        db_entry = update_session.query(LogbookEntry).filter(LogbookEntry.id == entry_id).first()

                        if not db_entry:
                            raise ValueError(f"Entry with ID {entry_id} not found")

                        # Find location ID based on device name
                        from app.db.models import Location
                        location = update_session.query(Location).filter(Location.name == entry_data["device"]).first()

                        if not location:
                            # Create a new location if it doesn't exist
                            location = Location(
                                name=entry_data["device"],
                                description=f"Location for {entry_data['device']}",
                                is_active=True,
                                created_at=datetime.now()
                            )
                            update_session.add(location)
                            update_session.flush()  # This will assign an ID to the location

                        # Update entry fields
                        db_entry.responsible_person = entry_data["responsible_person"]
                        db_entry.task = entry_data["task"]
                        db_entry.location_id = location.id
                        db_entry.device = entry_data["device"]

                        # Update dates if provided
                        if entry_data["start_date"]:
                            db_entry.start_date = datetime.strptime(entry_data["start_date"], "%Y-%m-%d").date()

                        if entry_data["end_date"]:
                            db_entry.end_date = datetime.strptime(entry_data["end_date"], "%Y-%m-%d").date()

                        db_entry.call_description = entry_data["call_description"]
                        db_entry.solution_description = entry_data["solution_description"]

                        # Handle resolution time if provided
                        if entry_data["resolution_time"]:
                            # Parse the time in HH:MM format and combine with created_at date
                            time_parts = entry_data["resolution_time"].split(':')
                            hour = int(time_parts[0])
                            minute = int(time_parts[1])

                            # Create a datetime object with the resolution time
                            resolution_date = db_entry.created_at.date()
                            resolution_time = datetime.combine(resolution_date, time(hour, minute))

                            # If resolution time is earlier than created_at, add a day
                            if resolution_time < db_entry.created_at:
                                resolution_time = resolution_time + timedelta(days=1)

                            db_entry.resolution_time = resolution_time

                        # Update status if provided
                        if entry_data["status"]:
                            db_entry.status = entry_data["status"]

                        # Update the updated_at timestamp
                        db_entry.updated_at = datetime.now()

                        # Commit the changes
                        update_session.commit()

                    # Show success message
                    self.page.snack_bar = ft.SnackBar(
                        content=Text("Entry updated successfully"),
                        action="OK",
                    )
                    self.page.snack_bar.open = True

                    # Return to the recent activity view and refresh the entries
                    self.page.clean()
                    self.page.add(self)
                    self.load_entries()  # Reload entries to show the updated one
                    self.page.update()

                except Exception as ex:
                    # Show error message if update fails
                    self.page.snack_bar = ft.SnackBar(
                        content=Text(f"Error updating entry: {str(ex)}"),
                        action="OK",
                    )
                    self.page.snack_bar.open = True
                    self.page.update()

            # Create a handler for canceling the edit
            def handle_cancel():
                # Return to the recent activity view without making changes
                self.page.clean()
                self.page.add(self)
                self.page.update()

            # Create the edit entry view using the NewEntryView with pre-filled data
            edit_view = NewEntryView(on_save=handle_save, on_cancel=handle_cancel)
            edit_view.page = self.page

            # Pre-fill the form with existing entry data
            # Responsible person
            edit_view.responsible_person_field.value = entry.responsible_person

            # Task checkboxes
            if entry.task:
                tasks = [task.strip() for task in entry.task.split(',')]
                for task, checkbox in edit_view.task_checkboxes.items():
                    checkbox.value = task in tasks

            # Location/device
            if entry.device:
                edit_view.location_dropdown.value = entry.device
                # Also check the corresponding location checkbox if it exists
                for loc, checkbox in edit_view.location_checkboxes.items():
                    if loc == entry.device:
                        checkbox.value = True

            # Dates
            if entry.start_date:
                edit_view.start_date_field.value = entry.start_date.strftime("%Y-%m-%d")

            if entry.end_date:
                edit_view.end_date_field.value = entry.end_date.strftime("%Y-%m-%d")

            # Description fields
            edit_view.call_description_field.value = entry.call_description or ""
            edit_view.solution_field.value = entry.solution_description or ""

            # Resolution time
            if entry.resolution_time:
                edit_view.resolution_time_field.value = entry.resolution_time.strftime("%H:%M")

            # Status
            if entry.status:
                edit_view.status_dropdown.value = entry.status

            # Replace the current view with the edit view
            self.page.clean()
            self.page.add(edit_view)
            self.page.update()

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
            user_id = None
            if hasattr(self.page, "data") and self.page.data is not None:
                user_id = self.page.data.get("user_id")

            # If user_id is still None, try to get a default user from the database
            if user_id is None:
                # Find an admin user or any user to use as the creator
                from app.db.models import User, RoleEnum
                default_user = session.query(User).filter(User.role == RoleEnum.ADMIN).first()
                if not default_user:
                    default_user = session.query(User).first()

                if default_user:
                    user_id = default_user.id
                else:
                    # If no users exist in the database, create a system user ID
                    user_id = uuid.uuid4()

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
