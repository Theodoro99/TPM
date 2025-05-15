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
    Dropdown,
    dropdown,
    icons,
    colors,
    padding,
    border,
    border_radius,
)


class NewEntryView(ft.Column):
    def __init__(self, on_save=None, on_cancel=None):
        super().__init__()
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO

        # Form fields
        self.responsible_person_field = TextField(
            label="Responsible Person",
            hint_text="Enter the name of the responsible person",
            border=ft.InputBorder.OUTLINE,
            expand=True,
            color=colors.BLACK,
            label_style=ft.TextStyle(color=colors.BLACK),
            hint_style=ft.TextStyle(color=colors.BLACK87),
        )

        # Create a container for task selection with checkboxes
        self.task_options = [
            "Interventie",
            "Onderhoud",
            "Facilities",
            "NVT",
        ]

        self.task_checkboxes = {}
        task_checkbox_rows = []

        # Create checkboxes for each task option
        for task in self.task_options:
            checkbox = ft.Checkbox(label=task, value=False, label_style=ft.TextStyle(color=colors.BLACK))
            self.task_checkboxes[task] = checkbox
            task_checkbox_rows.append(Row([checkbox]))

        # Create a container for the task checkboxes
        self.task_container = Container(
            content=Column(
                [Text("Task:", size=16, weight="bold", color=colors.BLACK)] + task_checkbox_rows,
                spacing=5,
            ),
            border=ft.border.all(1, colors.BLUE_GREY_200),
            border_radius=border_radius.all(5),
            padding=padding.all(10),
            bgcolor=colors.WHITE,
            expand=True,
        )

        # Create a container for location selection with checkboxes
        self.location_options = [
            "Bundelwikkelaar",
            "Stacker platfrom 1/2",
            "Pers",
            "Kaltenbach",
            "Billetoven",
            "Paaltafel",
            "Koudzaag",
            "Hardingsoven",
            "Infra",
            "Scrap",
            "Koeltafel",
            "Destacker 1/2/3",
            "Warmzaag",
            "Borstelmachine",
            "Profielwikkelaar",
            "Kopzaag",
            "Die's",
            "Plier",
            "Puller",
            "Runout-tafel",
        ]

        self.location_checkboxes = {}
        location_checkbox_rows = []

        # Create checkboxes for each location option
        for location in self.location_options:
            checkbox = ft.Checkbox(label=location, value=False, label_style=ft.TextStyle(color=colors.BLACK))
            self.location_checkboxes[location] = checkbox
            location_checkbox_rows.append(Row([checkbox]))

        # Create a scrollable container for the checkboxes
        self.location_container = Container(
            content=Column(
                location_checkbox_rows,
                scroll=ft.ScrollMode.AUTO,
                height=200,
            ),
            border=ft.border.all(1, colors.BLUE_GREY_200),
            border_radius=border_radius.all(5),
            padding=padding.all(10),
            bgcolor=colors.WHITE,
            expand=True,
        )

        # Create a dropdown for single location selection (as fallback)
        self.location_dropdown = Dropdown(
            label="Location",
            hint_text="Select a location",
            options=[
                dropdown.Option("Bundelwikkelaar"),
                dropdown.Option("Stacker platfrom 1/2"),
                dropdown.Option("Pers"),
                dropdown.Option("Kaltenbach"),
                dropdown.Option("Billetoven"),
                dropdown.Option("Paaltafel"),
                dropdown.Option("Koudzaag"),
                dropdown.Option("Hardingsoven"),
                dropdown.Option("Infra"),
                dropdown.Option("Scrap"),
                dropdown.Option("Koeltafel"),
                dropdown.Option("Destacker 1/2/3"),
                dropdown.Option("Warmzaag"),
                dropdown.Option("Borstelmachine"),
                dropdown.Option("Profielwikkelaar"),
                dropdown.Option("Kopzaag"),
                dropdown.Option("Die's"),
                dropdown.Option("Plier"),
                dropdown.Option("Puller"),
                dropdown.Option("Runout-tafel"),
            ],
            border=ft.InputBorder.OUTLINE,
            bgcolor=colors.WHITE,
            color=colors.BLACK,
            focused_bgcolor=colors.BLUE_50,
            focused_color=colors.BLACK,
            focused_border_color=colors.BLUE,
            expand=True,
            visible=False,  # Hide the dropdown, we'll use the checkboxes instead
        )

        # Initialize date picker with today's date
        today = datetime.now()

        # Create a custom date picker dialog
        self.date_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Select a date"),
            content=ft.Column([
                ft.Text("Click on a date to select it:"),
                ft.Container(height=10),  # Spacer
                ft.Row([
                    ft.ElevatedButton(
                        text="Today",
                        on_click=lambda e: self.set_date(datetime.now())
                    ),
                    ft.ElevatedButton(
                        text="Tomorrow",
                        on_click=lambda e: self.set_date(datetime.now() + timedelta(days=1))
                    ),
                    ft.ElevatedButton(
                        text="Next Week",
                        on_click=lambda e: self.set_date(datetime.now() + timedelta(days=7))
                    ),
                ]),
                ft.Container(height=10),  # Spacer
                # Month and day selection
                ft.Row([
                    ft.Dropdown(
                        label="Month",
                        width=150,
                        options=[ft.dropdown.Option(str(i), f"{calendar.month_name[i]}") for i in range(1, 13)],
                        value=str(today.month),
                        on_change=self.update_calendar,
                        expand=1
                    ),
                    ft.Dropdown(
                        label="Year",
                        width=120,
                        options=[ft.dropdown.Option(str(i), str(i)) for i in range(2020, 2031)],
                        value=str(today.year),
                        on_change=self.update_calendar,
                        expand=1
                    ),
                ]),
                ft.Container(height=10),  # Spacer
                # Calendar grid will be added dynamically
                ft.Column([]),
            ]),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_date_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Initialize date-related variables
        self.selected_date = today
        self.initial_date = today.strftime("%Y-%m-%d")
        self.is_end_date_selection = False  # Flag to track which date field we're updating

        self.start_date_field = TextField(
            label="Start Date",
            value=self.initial_date,  # Set initial value
            hint_text="Select start date",
            read_only=True,
            on_click=lambda e: self.show_date_picker(e, is_end_date=False),
            border=ft.InputBorder.OUTLINE,
            filled=True,
            bgcolor=colors.WHITE,
            color=colors.BLACK,
            expand=1,
        )

        self.end_date_field = TextField(
            label="End Date",
            value="",  # Initially empty
            hint_text="Select end date",
            read_only=True,
            on_click=lambda e: self.show_date_picker(e, is_end_date=True),
            border=ft.InputBorder.OUTLINE,
            filled=True,
            bgcolor=colors.WHITE,
            color=colors.BLACK,
            label_style=ft.TextStyle(color=colors.BLACK),
            hint_style=ft.TextStyle(color=colors.BLACK87),
            expand=1,
        )

        self.call_description_field = TextField(
            label="Call Description",
            hint_text="Describe the maintenance call",
            border=ft.InputBorder.OUTLINE,
            multiline=True,
            min_lines=3,
            max_lines=5,
            expand=True,
            color=colors.BLACK,
            label_style=ft.TextStyle(color=colors.BLACK),
            hint_style=ft.TextStyle(color=colors.BLACK87),
        )

        self.solution_field = TextField(
            label="Solution",
            hint_text="Describe the solution implemented",
            border=ft.InputBorder.OUTLINE,
            multiline=True,
            min_lines=3,
            max_lines=5,
            expand=True,
            color=colors.BLACK,
            label_style=ft.TextStyle(color=colors.BLACK),
            hint_style=ft.TextStyle(color=colors.BLACK87),
        )

        # Resolution Time field
        self.resolution_time_field = TextField(
            label="Resolution Time",
            hint_text="HH:MM",
            border=ft.InputBorder.OUTLINE,
            expand=True,
            color=colors.BLACK,
            label_style=ft.TextStyle(color=colors.BLACK),
            hint_style=ft.TextStyle(color=colors.BLACK87),
        )

        self.status_dropdown = Dropdown(
            label="Status",
            hint_text="Select status",
            options=[
                dropdown.Option("Open"),
                dropdown.Option("Completed"),
                dropdown.Option("Ongoing"),
                dropdown.Option("Escalated"),
            ],
            border=ft.InputBorder.OUTLINE,
            expand=True,
            bgcolor=colors.WHITE,
            color=colors.BLACK,
            label_style=ft.TextStyle(color=colors.BLACK),
            hint_style=ft.TextStyle(color=colors.BLACK87),
            focused_bgcolor=colors.BLUE_50,
            focused_color=colors.BLACK,
            focused_border_color=colors.BLUE,
        )

        # Category dropdown
        self.category_dropdown = Dropdown(
            label="Category",
            hint_text="Select category",
            options=[
                dropdown.Option("Not categorized"),
                dropdown.Option("Mechanical"),
                dropdown.Option("Electrical"),
                dropdown.Option("Hydraulic"),
                dropdown.Option("Pneumatic"),
                dropdown.Option("Software"),
                dropdown.Option("Hardware"),
                dropdown.Option("Safety"),
                dropdown.Option("Other"),
            ],
            border=ft.InputBorder.OUTLINE,
            expand=True,
            bgcolor=colors.WHITE,
            color=colors.BLACK,
            label_style=ft.TextStyle(color=colors.BLACK),
            hint_style=ft.TextStyle(color=colors.BLACK87),
            focused_bgcolor=colors.BLUE_50,
            focused_color=colors.BLACK,
            focused_border_color=colors.BLUE,
        )

        # Priority dropdown
        self.priority_dropdown = Dropdown(
            label="Priority",
            hint_text="Select priority",
            options=[
                dropdown.Option("Low"),
                dropdown.Option("Medium"),
                dropdown.Option("High"),
                dropdown.Option("Critical"),
            ],
            border=ft.InputBorder.OUTLINE,
            expand=True,
            bgcolor=colors.WHITE,
            color=colors.BLACK,
            label_style=ft.TextStyle(color=colors.BLACK),
            hint_style=ft.TextStyle(color=colors.BLACK87),
            focused_bgcolor=colors.BLUE_50,
            focused_color=colors.BLACK,
            focused_border_color=colors.BLUE,
            value="Medium",  # Default value
        )

        # Build the UI
        self.setup_ui()

    def setup_ui(self):
        # Create form container
        form_container = Container(
            content=Column(
                [
                    Text(
                        "New Logbook Entry",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=colors.BLACK,
                    ),
                    Container(height=20),

                    # Responsible Person
                    Row(
                        [
                            self.responsible_person_field,
                        ],
                        spacing=10,
                    ),
                    Container(height=10),

                    # Task selection
                    self.task_container,
                    Container(height=10),

                    # Location label
                    Row(
                        [
                            Text(
                                "Locations (select multiple):",
                                size=16,
                                weight="bold",
                                color=colors.BLACK,
                            ),
                        ],
                    ),
                    Container(height=5),

                    # Location checkboxes
                    self.location_container,
                    Container(height=10),

                    # Start Date
                    Row(
                        [
                            Container(
                                content=Row(
                                    [
                                        self.start_date_field,
                                        ft.IconButton(
                                            icon=icons.CALENDAR_TODAY,
                                            on_click=lambda e: self.show_date_picker(e, is_end_date=False),
                                        ),
                                    ]
                                ),
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    Container(height=10),

                    # End Date
                    Row(
                        [
                            Container(width=20),
                            Container(
                                content=Row(
                                    [
                                        self.end_date_field,
                                        ft.IconButton(
                                            icon=icons.CALENDAR_TODAY,
                                            on_click=lambda e: self.show_date_picker(e, is_end_date=True),
                                        ),
                                    ]
                                ),
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    Container(height=10),

                    # Call Description
                    self.call_description_field,
                    Container(height=10),

                    # Solution
                    self.solution_field,
                    Container(height=10),

                    # Resolution Time
                    Row(
                        [
                            Container(
                                content=Row(
                                    [
                                        self.resolution_time_field,
                                    ]
                                ),
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    Container(height=10),

                    # Status, Category and Priority in a row
                    Row(
                        [
                            Container(
                                content=self.status_dropdown,
                                expand=True,
                            ),
                            Container(width=10),
                            Container(
                                content=self.category_dropdown,
                                expand=True,
                            ),
                            Container(width=10),
                            Container(
                                content=self.priority_dropdown,
                                expand=True,
                            ),
                        ],
                        spacing=5,
                    ),
                    Container(height=20),

                    # Buttons
                    Row(
                        [
                            ElevatedButton(
                                "Cancel",
                                icon=icons.CANCEL,
                                on_click=self.handle_cancel,
                                style=ft.ButtonStyle(
                                    color=colors.WHITE,
                                    bgcolor=colors.RED_400,
                                ),
                            ),
                            ElevatedButton(
                                "Save",
                                icon=icons.SAVE,
                                on_click=self.handle_save,
                                style=ft.ButtonStyle(
                                    color=colors.WHITE,
                                    bgcolor=colors.GREEN_500,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=10,
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

        self.controls = [form_container]

    def show_date_picker(self, e, is_end_date=False):
        if self.page:
            # Set the flag to track which date field we're updating
            self.is_end_date_selection = is_end_date

            # Update the dialog title based on which date we're selecting
            self.date_dialog.title = ft.Text("Select End Date" if is_end_date else "Select Start Date")

            # Add date dialog to page overlay if not already added
            if self.date_dialog not in self.page.overlay:
                self.page.overlay.append(self.date_dialog)

            # Update the calendar grid before showing the dialog
            self.update_calendar_grid()

            # Show the date dialog
            self.date_dialog.open = True
            self.page.update()

    def update_calendar(self, e):
        # Update the calendar grid when month or year changes
        self.update_calendar_grid()
        self.page.update()

    def update_calendar_grid(self):
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
        # Handle day button click
        day = e.control.data["day"]
        month = e.control.data["month"]
        year = e.control.data["year"]

        # Create the selected date
        selected_date = datetime(year, month, day)
        self.set_date(selected_date)

    def set_date(self, date):
        # Set the selected date and update the appropriate text field
        self.selected_date = date
        formatted_date = date.strftime("%Y-%m-%d")

        if self.is_end_date_selection:
            # Update end date field
            self.end_date_field.value = formatted_date
            print(f"End date set to: {formatted_date}")
        else:
            # Update start date field
            self.start_date_field.value = formatted_date
            print(f"Start date set to: {formatted_date}")

        # Close the dialog
        self.close_date_dialog(None)

        # Update the page
        self.page.update()

    def close_date_dialog(self, e):
        # Close the date dialog
        self.date_dialog.open = False
        self.page.update()

    def handle_save(self, e):
        # Validate form
        if not self.responsible_person_field.value:
            self.show_error_dialog("Responsible Person is required")
            return

        # Check if at least one task is selected
        selected_tasks = [task for task, checkbox in self.task_checkboxes.items() if checkbox.value]
        if not selected_tasks:
            self.show_error_dialog("At least one Task must be selected")
            return

        # Ensure we have a valid location
        selected_locations = [loc for loc, checkbox in self.location_checkboxes.items() if checkbox.value]
        device = self.location_dropdown.value

        if not device and not selected_locations:
            self.show_error_dialog("Either select a location from the dropdown or check at least one location")
            return

        # If no dropdown selection but checkboxes are selected, use the first checked location
        if not device and selected_locations:
            device = selected_locations[0]

        if not self.start_date_field.value:
            self.show_error_dialog("Start Date is required")
            return

        if not self.call_description_field.value:
            self.show_error_dialog("Call Description is required")
            return

        # Validate end date is after start date if provided
        if self.end_date_field.value:
            try:
                start_date = datetime.strptime(self.start_date_field.value, "%Y-%m-%d")
                end_date = datetime.strptime(self.end_date_field.value, "%Y-%m-%d")

                if end_date < start_date:
                    self.show_error_dialog("End Date must be after Start Date")
                    return
            except ValueError:
                self.show_error_dialog("Invalid date format")
                return

        # Validate resolution time format if provided
        resolution_time = None
        if self.resolution_time_field.value:
            try:
                # Parse the time in HH:MM format
                time_parts = self.resolution_time_field.value.split(':')
                if len(time_parts) != 2:
                    raise ValueError("Time must be in HH:MM format")

                hour = int(time_parts[0])
                minute = int(time_parts[1])

                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    raise ValueError("Invalid time values")

                resolution_time = self.resolution_time_field.value
            except ValueError as e:
                self.show_error_dialog(f"Invalid resolution time format: {str(e)}. Please use HH:MM format.")
                return

        # Format task as a string for database storage
        task_str = ", ".join(selected_tasks)
        print(f"Selected tasks: {selected_tasks}")
        print(f"Task string: {task_str}")

        # Format locations as a string for reference
        locations_str = ", ".join(selected_locations) if selected_locations else ""
        print(f"Selected locations: {selected_locations}")
        print(f"Using device: {device}")

        # Create entry data
        entry_data = {
            "responsible_person": self.responsible_person_field.value,
            "task": task_str,
            "location": locations_str,  # This is just for reference
            "start_date": self.start_date_field.value,
            "end_date": self.end_date_field.value,
            "call_description": self.call_description_field.value,
            "solution_description": self.solution_field.value,
            "resolution_time": resolution_time,  # Add resolution time to entry data
            "status": self.status_dropdown.value or "Open",
            "category": self.category_dropdown.value or "Not categorized",
            "priority": self.priority_dropdown.value or "Medium",
            "device": device  # This is the actual field used for location_id lookup
        }

        print(f"Sending entry data: {entry_data}")

        # Call the save callback
        if self.on_save:
            self.on_save(entry_data)

    def handle_cancel(self, e):
        if self.on_cancel:
            self.on_cancel()

    def show_error_dialog(self, message):
        if self.page:
            def close_dlg(e):
                dlg_modal.open = False
                self.page.update()

            dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text("Validation Error"),
                content=ft.Text(message),
                actions=[
                    ft.TextButton("OK", on_click=close_dlg),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            self.page.dialog = dlg_modal
            dlg_modal.open = True
            self.page.update()
