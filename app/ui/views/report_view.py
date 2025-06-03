import flet as ft
import calendar
from datetime import datetime, timedelta
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
    Checkbox,
)

class ReportView(ft.Column):
    """A view for generating various types of reports with customizable filters and date ranges.

    Provides UI components for selecting report type, date range, status and priority filters,
    and output format. Includes date picker dialogs for selecting start and end dates.
    """
    def __init__(self, on_generate=None, on_back=None):
        """Initialize the ReportView.

        Args:
            on_generate: Callback function to be called when generating a report
            on_back: Callback function to be called when going back
        """
        super().__init__()
        self.on_generate = on_generate
        self.on_back = on_back
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        
        # Report parameters
        self.report_type_dropdown = Dropdown(
            label="Report Type",
            hint_text="Select report type",
            options=[
                dropdown.Option("Daily Activity"),
                dropdown.Option("Monthly Summary"),
                dropdown.Option("Status Report"),
                dropdown.Option("Priority Analysis"),
                dropdown.Option("Custom Report"),
            ],
            border=ft.InputBorder.OUTLINE,
            expand=True,
            bgcolor=colors.WHITE,
            color=colors.BLACK,
            focused_bgcolor=colors.BLUE_50,
            focused_color=colors.BLACK,
            focused_border_color=colors.BLUE,
        )
        
        # Initialize with today's date
        today = datetime.now()
        
        # Create custom date picker dialogs
        # Start date picker dialog
        self.start_date_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Select Start Date"),
            content=ft.Column([
                ft.Text("Click on a date to select it:"),
                ft.Container(height=10),  # Spacer
                ft.Row([
                    ft.ElevatedButton(
                        text="Today",
                        on_click=lambda e: self.set_start_date(datetime.now())
                    ),
                    ft.ElevatedButton(
                        text="Yesterday",
                        on_click=lambda e: self.set_start_date(datetime.now() - timedelta(days=1))
                    ),
                    ft.ElevatedButton(
                        text="Last Week",
                        on_click=lambda e: self.set_start_date(datetime.now() - timedelta(days=7))
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
                        on_change=self.update_start_calendar,
                        expand=1
                    ),
                    ft.Dropdown(
                        label="Year",
                        width=120,
                        options=[ft.dropdown.Option(str(i), str(i)) for i in range(2020, 2031)],
                        value=str(today.year),
                        on_change=self.update_start_calendar,
                        expand=1
                    ),
                ]),
                ft.Container(height=10),  # Spacer
                # Calendar grid will be added dynamically
                ft.Column([]),
            ]),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_start_date_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # End date picker dialog
        self.end_date_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Select End Date"),
            content=ft.Column([
                ft.Text("Click on a date to select it:"),
                ft.Container(height=10),  # Spacer
                ft.Row([
                    ft.ElevatedButton(
                        text="Today",
                        on_click=lambda e: self.set_end_date(datetime.now())
                    ),
                    ft.ElevatedButton(
                        text="Tomorrow",
                        on_click=lambda e: self.set_end_date(datetime.now() + timedelta(days=1))
                    ),
                    ft.ElevatedButton(
                        text="Next Week",
                        on_click=lambda e: self.set_end_date(datetime.now() + timedelta(days=7))
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
                        on_change=self.update_end_calendar,
                        expand=1
                    ),
                    ft.Dropdown(
                        label="Year",
                        width=120,
                        options=[ft.dropdown.Option(str(i), str(i)) for i in range(2020, 2031)],
                        value=str(today.year),
                        on_change=self.update_end_calendar,
                        expand=1
                    ),
                ]),
                ft.Container(height=10),  # Spacer
                # Calendar grid will be added dynamically
                ft.Column([]),
            ]),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_end_date_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Set initial date values
        self.start_selected_date = today
        self.end_selected_date = today
        self.initial_date = today.strftime("%Y-%m-%d")
        
        # Initialize filter options
        self.status_options = ft.Checkbox(label="All Statuses", value=True)
        self.priority_options = ft.Checkbox(label="All Priorities", value=True)
        
        self.start_date_field = TextField(
            label="Start Date",
            value=self.initial_date,  # Set initial value
            hint_text="Select start date",
            border=ft.InputBorder.OUTLINE,
            expand=True,
            read_only=True,
            color=colors.BLACK,
            label_style=ft.TextStyle(color=colors.BLACK),
            hint_style=ft.TextStyle(color=colors.BLACK87),
        )
        
        self.end_date_field = TextField(
            label="End Date",
            value=self.initial_date,  # Set initial value
            hint_text="Select end date",
            border=ft.InputBorder.OUTLINE,
            expand=True,
            read_only=True,
            color=colors.BLACK,
            label_style=ft.TextStyle(color=colors.BLACK),
            hint_style=ft.TextStyle(color=colors.BLACK87),
        )
        
        # Filter options
        self.filter_options = Row([
            Checkbox(label="Open", value=True, label_style=ft.TextStyle(color=colors.BLACK)),
            Checkbox(label="Completed", value=True, label_style=ft.TextStyle(color=colors.BLACK)),
            Checkbox(label="Escalation", value=True, label_style=ft.TextStyle(color=colors.BLACK)),
        ])
        
        self.priority_options = Column([
            Checkbox(label="Low", value=True, label_style=ft.TextStyle(color=colors.BLACK)),
            Checkbox(label="Medium", value=True, label_style=ft.TextStyle(color=colors.BLACK)),
            Checkbox(label="High", value=True, label_style=ft.TextStyle(color=colors.BLACK)),
        ])
        
        # Format options
        self.format_dropdown = Dropdown(
            label="Output Format",
            hint_text="Select output format",
            options=[
                dropdown.Option("PDF"),
                dropdown.Option("Excel"),
                dropdown.Option("CSV"),
                dropdown.Option("HTML"),
            ],
            border=ft.InputBorder.OUTLINE,
            expand=True,
            value="PDF",
            bgcolor=colors.WHITE,
            color=colors.BLACK,
            focused_bgcolor=colors.BLUE_50,
            focused_color=colors.BLACK,
            focused_border_color=colors.BLUE,
        )
        
        # Build the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface with all report generation controls."""
        # Create report container
        report_container = Container(
            content=Column(
                [
                    Text(
                        "Generate Report",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=colors.BLACK,
                    ),
                    Container(height=20),
                    
                    # Report Type
                    self.report_type_dropdown,
                    Container(height=20),
                    
                    # Date Range
                    Text(
                        "Date Range",
                        size=16,
                        color=colors.BLACK,
                        weight=ft.FontWeight.BOLD,
                    ),
                    Container(height=10),
                    Row(
                        [
                            Container(
                                content=Row(
                                    [
                                        self.start_date_field,
                                        ft.IconButton(
                                            icon=icons.CALENDAR_TODAY,
                                            on_click=self.show_start_date_picker,
                                        ),
                                    ]
                                ),
                                expand=True,
                            ),
                            Container(width=20),
                            Container(
                                content=Row(
                                    [
                                        self.end_date_field,
                                        ft.IconButton(
                                            icon=icons.CALENDAR_TODAY,
                                            on_click=self.show_end_date_picker,
                                        ),
                                    ]
                                ),
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    Container(height=20),
                    
                    # Filters
                    Text(
                        "Filters",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=colors.BLACK,
                    ),
                    Container(height=10),
                    Row(
                        [
                            Container(
                                content=Column(
                                    [
                                        Text(
                                            "Status",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=colors.BLACK,
                                        ),
                                        self.status_options,
                                    ],
                                    spacing=5,
                                ),
                                padding=padding.all(10),
                                bgcolor=colors.BLUE_50,
                                border_radius=border_radius.all(5),
                                border=border.all(1, colors.BLUE_100),
                                expand=True,
                            ),
                            Container(width=20),
                            Container(
                                content=Column(
                                    [
                                        Text(
                                            "Priority",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=colors.BLACK,
                                        ),
                                        self.priority_options,
                                    ],
                                    spacing=5,
                                ),
                                padding=padding.all(10),
                                bgcolor=colors.BLUE_50,
                                border_radius=border_radius.all(5),
                                border=border.all(1, colors.BLUE_100),
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    Container(height=20),
                    
                    # Output Format
                    self.format_dropdown,
                    Container(height=30),
                    
                    # Buttons
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
                            ft.Container(expand=True),
                            ElevatedButton(
                                "Generate Report",
                                icon=icons.SUMMARIZE,
                                on_click=self.handle_generate,
                                style=ft.ButtonStyle(
                                    color=colors.WHITE,
                                    bgcolor=colors.INDIGO_500,
                                ),
                            ),
                        ],
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
        
        self.controls = [report_container]
    
    def show_start_date_picker(self, e):
        """Show the start date picker dialog.

        Args:
            e: The event that triggered this action
        """
        if self.page:
            # Add date dialog to page overlay if not already added
            if self.start_date_dialog not in self.page.overlay:
                self.page.overlay.append(self.start_date_dialog)
            
            # Update the calendar grid before showing the dialog
            self.update_start_calendar_grid()
            
            # Show the date dialog
            self.start_date_dialog.open = True
            self.page.update()
            
    def show_end_date_picker(self, e):
        """Show the end date picker dialog.

        Args:
            e: The event that triggered this action
        """
        if self.page:
            # Add date dialog to page overlay if not already added
            if self.end_date_dialog not in self.page.overlay:
                self.page.overlay.append(self.end_date_dialog)
            
            # Update the calendar grid before showing the dialog
            self.update_end_calendar_grid()
            
            # Show the date dialog
            self.end_date_dialog.open = True
            self.page.update()
            
    # Start date calendar methods
    def update_start_calendar(self, e):
        """Update the start date calendar when month or year changes.

        Args:
            e: The event that triggered this update
        """
        # Update the calendar grid when month or year changes
        self.update_start_calendar_grid()
        self.page.update()
    
    def update_start_calendar_grid(self):
        """Update the calendar grid display for start date selection."""
        # Get the selected month and year from dropdowns
        month_dropdown = self.start_date_dialog.content.controls[4].controls[0]
        year_dropdown = self.start_date_dialog.content.controls[4].controls[1]
        
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
        
        # Create calendar grid
        calendar_grid = self.start_date_dialog.content.controls[6]
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
                        on_click=self.start_day_clicked
                    )
                    week_row.controls.append(date_btn)
            calendar_grid.controls.append(week_row)
    
    def start_day_clicked(self, e):
        """Handle day selection in the start date calendar.

        Args:
            e: The event containing the selected day data
        """

        # Handle day button click for start date
        day = e.control.data["day"]
        month = e.control.data["month"]
        year = e.control.data["year"]
        
        # Create the selected date
        selected_date = datetime(year, month, day)
        self.set_start_date(selected_date)
    
    def set_start_date(self, date):
        """Set the selected start date and update the UI.

        Args:
            date: The datetime object to set as start date
        """

        # Set the selected start date and update the text field
        self.start_selected_date = date
        formatted_date = date.strftime("%Y-%m-%d")
        self.start_date_field.value = formatted_date
        print(f"Start date set to: {formatted_date}")
        
        # Close the dialog
        self.close_start_date_dialog(None)
        
        # Update the page
        self.page.update()
    
    def close_start_date_dialog(self, e):
        """Close the start date picker dialog.

        Args:
            e: The event that triggered this action
        """
        # Close the start date dialog
        self.start_date_dialog.open = False
        self.page.update()
    
    # End date calendar methods
    def update_end_calendar(self, e):
        """Update the end date calendar when month or year changes.

        Args:
            e: The event that triggered this update
        """
        # Update the calendar grid when month or year changes
        self.update_end_calendar_grid()
        self.page.update()
    
    def update_end_calendar_grid(self):
        """Update the calendar grid display for end date selection."""
        # Get the selected month and year from dropdowns
        month_dropdown = self.end_date_dialog.content.controls[4].controls[0]
        year_dropdown = self.end_date_dialog.content.controls[4].controls[1]
        
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
        
        # Create calendar grid
        calendar_grid = self.end_date_dialog.content.controls[6]
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
                        on_click=self.end_day_clicked
                    )
                    week_row.controls.append(date_btn)
            calendar_grid.controls.append(week_row)
    
    def end_day_clicked(self, e):
        """Handle day selection in the end date calendar.

        Args:
            e: The event containing the selected day data
        """

        # Handle day button click for end date
        day = e.control.data["day"]
        month = e.control.data["month"]
        year = e.control.data["year"]
        
        # Create the selected date
        selected_date = datetime(year, month, day)
        self.set_end_date(selected_date)
    
    def set_end_date(self, date):
        """Set the selected end date and update the UI.

        Args:
            date: The datetime object to set as end date
        """

        # Set the selected end date and update the text field
        self.end_selected_date = date
        formatted_date = date.strftime("%Y-%m-%d")
        self.end_date_field.value = formatted_date
        print(f"End date set to: {formatted_date}")
        
        # Close the dialog
        self.close_end_date_dialog(None)
        
        # Update the page
        self.page.update()
    
    def close_end_date_dialog(self, e):
        """Close the end date picker dialog.

        Args:
            e: The event that triggered this action
        """
        # Close the end date dialog
        self.end_date_dialog.open = False
        self.page.update()
    
    def handle_generate(self, e):
        """Handle the generate report button click.

        Validates inputs, collects report parameters, and triggers report generation.

        Args:
            e: The event that triggered this action
        """

        # Validate form
        if not self.report_type_dropdown.value:
            self.show_error_dialog("Please select a report type")
            return
        
        if not self.start_date_field.value:
            self.show_error_dialog("Please select a start date")
            return
        
        if not self.end_date_field.value:
            self.show_error_dialog("Please select an end date")
            return
        
        # Get selected status filters
        status_filters = []
        for status_checkbox in self.status_options.controls:
            if status_checkbox.value:
                status_filters.append(status_checkbox.label)
        
        # Get selected priority filters
        priority_filters = []
        for priority_checkbox in self.priority_options.controls:
            if priority_checkbox.value:
                priority_filters.append(priority_checkbox.label)
        
        # Create report parameters
        report_params = {
            "report_type": self.report_type_dropdown.value,
            "start_date": self.start_date_field.value,
            "end_date": self.end_date_field.value,
            "status_filters": status_filters,
            "priority_filters": priority_filters,
            "format": self.format_dropdown.value,
        }
        
        # Show generating report dialog
        self.show_generating_dialog()
        
        # Call the generate callback
        if self.on_generate:
            self.on_generate(report_params)
    
    def handle_back(self, e):
        """Handle the back button click.

        Args:
            e: The event that triggered this action
        """
        if self.on_back:
            self.on_back()
    
    def show_error_dialog(self, message):
        """Show an error dialog with the specified message.

        Args:
            message: The error message to display
        """
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
    
    def show_generating_dialog(self):
        """Show a dialog indicating report generation is in progress."""
        if self.page:
            def close_dlg(e):
                dlg_modal.open = False
                self.page.update()
                
                # Show download dialog after generation
                self.show_download_dialog()
                
            dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text("Generating Report"),
                content=Column(
                    [
                        Text("Please wait while your report is being generated..."),
                        Container(height=10),
                        ft.ProgressBar(width=400),
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=close_dlg),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            self.page.dialog = dlg_modal
            dlg_modal.open = True
            self.page.update()
            
            # Simulate report generation (would be replaced with actual generation)
            self.page.after(3000, lambda _: close_dlg(None))
    
    def show_download_dialog(self):
        """Show a dialog with download options after report generation."""
        if self.page:
            def close_dlg(e):
                dlg_modal.open = False
                self.page.update()
                
            dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text("Report Generated"),
                content=Column(
                    [
                        Text("Your report has been generated successfully!"),
                        Container(height=10),
                        Text(f"Format: {self.format_dropdown.value}"),
                        Container(height=10),
                        ElevatedButton(
                            "Download Report",
                            icon=icons.DOWNLOAD,
                            style=ft.ButtonStyle(
                                color=colors.WHITE,
                                bgcolor=colors.BLUE_500,
                            ),
                            on_click=lambda e: self.handle_download(),
                        ),
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                actions=[
                    ft.TextButton("Close", on_click=close_dlg),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            self.page.dialog = dlg_modal
            dlg_modal.open = True
            self.page.update()
    
    def handle_download(self):
        """Handle the download report button click."""
        # Simulate download (would be replaced with actual download)
        if self.page:
            def close_dlg(e):
                dlg_modal.open = False
                self.page.update()
                
            dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text("Download Started"),
                content=Text("Your report download has started."),
                actions=[
                    ft.TextButton("OK", on_click=close_dlg),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            self.page.dialog = dlg_modal
            dlg_modal.open = True
            self.page.update()
