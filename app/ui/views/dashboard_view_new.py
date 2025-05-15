import flet as ft
from flet import (
    Card,
    Column,
    Container,
    Icon,
    Row,
    Text,
    colors,
    icons,
    padding,
)


class StatCard(Container):
    def __init__(self, title, value, icon, color):
        content = Card(
            content=Container(
                content=Row(
                    [
                        Icon(
                            icon,
                            size=40,
                            color=color,
                        ),
                        Column(
                            [
                                Text(
                                    title,
                                    size=14,
                                    color=colors.WHITE,
                                ),
                                Text(
                                    value,
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                    color=colors.WHITE,
                                ),
                            ],
                            spacing=5,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=padding.all(20),
                width=250,
            ),
            elevation=3,
        )
        super().__init__(content=content)


class RecentActivityItem(Container):
    def __init__(self, title, description, time, status):
        content = Row(
            [
                Column(
                    [
                        Row(
                            [
                                Text(
                                    title,
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                Container(
                                    content=Text(
                                        status.capitalize(),
                                        size=12,
                                        color=colors.WHITE,
                                    ),
                                    bgcolor={
                                        "open": colors.AMBER_500,
                                        "ongoing": colors.PURPLE_500,
                                        "completed": colors.GREEN_500,
                                        "escalation": colors.RED_500,
                                    }.get(status.lower(), colors.GREY_500),
                                    border_radius=20,
                                    padding=padding.only(left=10, right=10, top=5, bottom=5),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            width=400,
                        ),
                        Text(
                            description,
                            size=14,
                            color=colors.BLUE_GREY_700,
                        ),
                        Container(height=5),
                        Text(
                            time,
                            size=12,
                            color=colors.BLUE_GREY_400,
                            italic=True,
                        ),
                    ],
                    spacing=5,
                ),
            ],
            alignment="start",
            vertical_alignment="center",
        )
        super().__init__(
            content=content,
            margin=ft.margin.only(bottom=10),
            padding=padding.all(10),
            border_radius=5,
            border=ft.border.all(1, ft.colors.BLACK12),
        )


class DashboardView(Column):
    def __init__(self):
        super().__init__()

        # Reference to the page for updating UI
        self.page = None

        # Create the alert dialog for notifications
        self.alert_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Information"),
            content=ft.Text("This is a placeholder message."),
            actions=[
                ft.TextButton("OK", on_click=self.close_dialog),
            ],
            actions_alignment="end",
        )

        # Load data from database
        self.load_data_from_database()

        # Build the UI
        self.setup_ui()

    def load_data_from_database(self):
        # Connect to the database and load entries
        from app.db.database import SessionLocal
        from app.db.models import LogbookEntry, StatusEnum
        from sqlalchemy import func

        # Initialize counters
        total_count = 0
        open_count = 0
        ongoing_count = 0
        completed_count = 0
        escalated_count = 0
        recent_activities = []

        # Create a database session
        db = SessionLocal()
        try:
            # Count total entries
            total_count = db.query(func.count(LogbookEntry.id)).filter(LogbookEntry.is_deleted == False).scalar() or 0

            # Count open entries
            open_count = db.query(func.count(LogbookEntry.id)).filter(
                LogbookEntry.status == StatusEnum.OPEN,
                LogbookEntry.is_deleted == False
            ).scalar() or 0

            # Count completed entries
            completed_count = db.query(func.count(LogbookEntry.id)).filter(
                LogbookEntry.status == StatusEnum.COMPLETED,
                LogbookEntry.is_deleted == False
            ).scalar() or 0

            # Count ongoing entries
            ongoing_count = db.query(func.count(LogbookEntry.id)).filter(
                LogbookEntry.status == StatusEnum.ONGOING,
                LogbookEntry.is_deleted == False
            ).scalar() or 0

            # Count escalated entries
            escalated_count = db.query(func.count(LogbookEntry.id)).filter(
                LogbookEntry.status == StatusEnum.ESCALATION,
                LogbookEntry.is_deleted == False
            ).scalar() or 0

            # Get recent activities (latest 5 entries)
            recent_entries = db.query(LogbookEntry).filter(
                LogbookEntry.is_deleted == False
            ).order_by(LogbookEntry.created_at.desc()).limit(5).all()

            # Convert to activity format
            for entry in recent_entries:
                activity = {
                    "title": f"New entry: {entry.device}",
                    "description": entry.call_description,
                    "time": entry.created_at.strftime("%Y-%m-%d %H:%M") if entry.created_at else "",
                    "status": entry.status.value if entry.status else "open"
                }
                recent_activities.append(activity)

        except Exception as e:
            print(f"Error loading data from database: {e}")
        finally:
            db.close()

        # Update instance variables
        self.total_entries = str(total_count)
        self.open_entries = str(open_count)
        self.ongoing_entries = str(ongoing_count)
        self.completed_entries = str(completed_count)
        self.escalated_entries = str(escalated_count)
        self.recent_activities = recent_activities

    def setup_ui(self):
        # Create stat cards
        stat_cards = Row(
            [
                StatCard("Open", self.open_entries, icons.PENDING_ACTIONS, colors.AMBER_500),
                StatCard("Ongoing", self.ongoing_entries, icons.LOOP, colors.PURPLE_500),
                StatCard("Completed", self.completed_entries, icons.TASK_ALT, colors.GREEN_500),
                StatCard("Escalated", self.escalated_entries, icons.PRIORITY_HIGH, colors.RED_500),
            ],
            wrap=True,
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,  # Center the cards horizontally
        )

        # Create total entries card
        total_entries_card = Row(
            [
                StatCard("Total Entries", self.total_entries, icons.BOOK, colors.BLUE_500),
            ],
            wrap=True,
            spacing=20,
        )

        # We've removed the Recent Activity section as it's now a separate page

        # Create professional quick actions with enhanced styling
        quick_actions = Card(
            content=Container(
                content=Column(
                    [
                        Container(
                            content=Text(
                                "Quick Actions",
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=colors.BLACK87,
                            ),
                            margin=ft.margin.only(bottom=15),
                            alignment=ft.alignment.center,  # Center the title
                            width=float('inf'),  # Take full width to enable centering
                        ),
                        Row(
                            [
                                # New Entry Button with enhanced styling
                                Container(
                                    content=ft.ElevatedButton(
                                        content=Row(
                                            [
                                                Icon(
                                                    icons.ADD_CIRCLE_OUTLINE,
                                                    color=colors.WHITE,
                                                    size=20,
                                                ),
                                                Container(width=8),
                                                Text(
                                                    "New Entry",
                                                    size=14,
                                                    weight=ft.FontWeight.W_500,
                                                    color=colors.WHITE,
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=0,
                                        ),
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                            color=colors.WHITE,
                                            bgcolor=colors.BLUE,
                                            elevation=4,
                                            padding=padding.symmetric(horizontal=20, vertical=15),
                                            animation_duration=300,
                                            side={"active": ft.BorderSide(3, colors.BLUE_ACCENT)},
                                            overlay_color=ft.colors.with_opacity(0.2, ft.colors.WHITE),
                                        ),
                                        on_click=self.show_new_entry_dialog,
                                        height=48,
                                    ),
                                    shadow=ft.BoxShadow(
                                        spread_radius=1,
                                        blur_radius=10,
                                        color=ft.colors.with_opacity(0.2, ft.colors.BLUE),
                                        offset=ft.Offset(0, 3),
                                    ),
                                ),

                                # View Recent Activity Button with enhanced styling
                                Container(
                                    content=ft.ElevatedButton(
                                        content=Row(
                                            [
                                                Icon(
                                                    icons.HISTORY_ROUNDED,
                                                    color=colors.WHITE,
                                                    size=20,
                                                ),
                                                Container(width=8),
                                                Text(
                                                    "View Recent Activity",
                                                    size=14,
                                                    weight=ft.FontWeight.W_500,
                                                    color=colors.WHITE,
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=0,
                                        ),
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                            color=colors.WHITE,
                                            bgcolor=colors.GREEN,
                                            elevation=4,
                                            padding=padding.symmetric(horizontal=20, vertical=15),
                                            animation_duration=300,
                                            side={"active": ft.BorderSide(3, colors.GREEN_ACCENT)},
                                            overlay_color=ft.colors.with_opacity(0.2, ft.colors.WHITE),
                                        ),
                                        on_click=self.navigate_to_recent_activity,
                                        height=48,
                                    ),
                                    shadow=ft.BoxShadow(
                                        spread_radius=1,
                                        blur_radius=10,
                                        color=ft.colors.with_opacity(0.2, ft.colors.GREEN),
                                        offset=ft.Offset(0, 3),
                                    ),
                                ),

                                # Generate Report Button with enhanced styling
                                Container(
                                    content=ft.ElevatedButton(
                                        content=Row(
                                            [
                                                Icon(
                                                    icons.SUMMARIZE_ROUNDED,
                                                    color=colors.WHITE,
                                                    size=20,
                                                ),
                                                Container(width=8),
                                                Text(
                                                    "Generate Report",
                                                    size=14,
                                                    weight=ft.FontWeight.W_500,
                                                    color=colors.WHITE,
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=0,
                                        ),
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                            color=colors.WHITE,
                                            bgcolor=colors.ORANGE,
                                            elevation=4,
                                            padding=padding.symmetric(horizontal=20, vertical=15),
                                            animation_duration=300,
                                            side={"active": ft.BorderSide(3, colors.ORANGE_ACCENT)},
                                            overlay_color=ft.colors.with_opacity(0.2, ft.colors.WHITE),
                                        ),
                                        on_click=self.show_report_dialog,
                                        height=48,
                                    ),
                                    shadow=ft.BoxShadow(
                                        spread_radius=1,
                                        blur_radius=10,
                                        color=ft.colors.with_opacity(0.2, ft.colors.ORANGE),
                                        offset=ft.Offset(0, 3),
                                    ),
                                ),
                            ],
                            spacing=16,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                ),
                padding=padding.all(25),
                bgcolor=colors.WHITE,
                border_radius=10,
            ),
            elevation=5,
        )

        # Add all components to the column
        self.controls = [
            # Centered Dashboard title
            Container(
                content=Text(
                    "Dashboard",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=colors.BLACK,
                ),
                alignment=ft.alignment.center,
                width=float('inf'),  # Take full width to enable centering
            ),
            Container(height=20),
            # Centered total entries card
            Container(
                content=total_entries_card,
                alignment=ft.alignment.center,
                width=float('inf'),  # Take full width to enable centering
            ),
            Container(height=20),
            # Wrap stat cards in a container to ensure full width centering
            Container(
                content=stat_cards,
                alignment=ft.alignment.center,
                width=float('inf'),  # Take full width to enable centering
            ),
            Container(height=30),
            # Wrap quick actions in a container for centering
            Container(
                content=quick_actions,
                alignment=ft.alignment.center,
                width=float('inf'),  # Take full width to enable centering
            ),
        ]
        self.spacing = 20
        self.scroll = ft.ScrollMode.AUTO
        self.expand = True

    def show_dialog(self, title, message):
        """Show a dialog with the given title and message."""
        # Create a new dialog each time to avoid issues with reusing dialogs
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self.close_dialog(e, dialog)),
            ],
            actions_alignment="end",
        )

        # Show the dialog using the page reference
        if self.page:
            # Set the dialog on the page and open it
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
            print(f"Dialog shown: {title}")
        else:
            print("Warning: Page reference not set, cannot show dialog")
            self.update()

    def close_dialog(self, e, dialog=None):
        """Close the dialog."""
        if dialog:
            dialog.open = False
        else:
            # Fallback to the old behavior for backward compatibility
            self.alert_dialog.open = False

        if self.page:
            self.page.update()
        else:
            self.update()

    def show_new_entry_dialog(self, e):
        """Navigate to the New Entry view."""
        print("New Entry button clicked")
        if self.page:
            # Import here to avoid circular imports
            from app.ui.views.new_entry_view import NewEntryView

            # Create the new entry view
            def handle_save(entry_data):
                print(f"Saving entry: {entry_data}")
                # Save the entry to the database
                from app.db.database import SessionLocal
                from app.db.models import LogbookEntry, StatusEnum, PriorityEnum, Location, User, RoleEnum
                import uuid
                import datetime
                from sqlalchemy import func

                # Validate required fields
                required_fields = ['responsible_person', 'device', 'call_description', 'start_date']
                missing_fields = [field for field in required_fields if not entry_data.get(field)]

                if missing_fields:
                    print(f"Missing required fields: {missing_fields}")
                    # Show error dialog
                    self.show_dialog(
                        "Validation Error",
                        f"Missing required fields: {', '.join(missing_fields)}"
                    )
                    return

                # Create a database session
                db = SessionLocal()
                try:
                    # Get or create location
                    location_name = entry_data['device']
                    location = db.query(Location).filter(Location.name == location_name).first()

                    if not location:
                        # Create a new location if it doesn't exist
                        print(f"Creating new location: {location_name}")

                        # Generate a user ID for the created_by_id field
                        # In a real app, this would be the current user's ID
                        admin_user = db.query(User).filter(User.role == RoleEnum.ADMIN).first()
                        created_by_id = admin_user.id if admin_user else uuid.uuid4()

                        location = Location(
                            name=location_name,
                            description=f"Auto-created from log entry for device: {location_name}",
                            created_by_id=created_by_id,
                            is_active=True
                        )
                        db.add(location)
                        db.flush()  # Get the ID without committing

                    print(f"Using location ID: {location.id} for {location_name}")

                    # Format task field if it exists
                    task = entry_data.get('task', '')

                    # Parse dates properly
                    try:
                        start_date = datetime.datetime.strptime(entry_data['start_date'], '%Y-%m-%d').date()
                    except ValueError as e:
                        print(f"Invalid start date format: {e}")
                        self.show_dialog("Date Error", f"Invalid start date format: {entry_data['start_date']}")
                        return

                    end_date = None
                    if entry_data.get('end_date'):
                        try:
                            end_date = datetime.datetime.strptime(entry_data['end_date'], '%Y-%m-%d').date()
                        except ValueError as e:
                            print(f"Invalid end date format: {e}")
                            self.show_dialog("Date Error", f"Invalid end date format: {entry_data['end_date']}")
                            return

                    # Get the status from the entry data or default to OPEN
                    status_value = entry_data.get('status', 'Open')

                    # Map UI status values to StatusEnum values
                    status_mapping = {
                        'Open': StatusEnum.OPEN,
                        'Ongoing': StatusEnum.ONGOING,
                        'Completed': StatusEnum.COMPLETED,
                        'Escalated': StatusEnum.ESCALATION
                    }

                    # Get the appropriate enum value or default to OPEN
                    status = status_mapping.get(status_value, StatusEnum.OPEN)
                    print(f"Mapped status '{status_value}' to enum value: {status}")

                    # Get the priority from the entry data or default to MEDIUM
                    priority_value = entry_data.get('priority', 'MEDIUM').upper()
                    # Make sure it's a valid PriorityEnum value
                    try:
                        priority = getattr(PriorityEnum, priority_value)
                    except AttributeError:
                        print(f"Invalid priority value: {priority_value}, defaulting to MEDIUM")
                        priority = PriorityEnum.MEDIUM

                    print(f"Using status: {status} and priority: {priority}")

                    # Process resolution time if provided
                    resolution_time = None
                    if entry_data.get('resolution_time'):
                        try:
                            # Parse the time in HH:MM format
                            time_str = entry_data['resolution_time']
                            hour, minute = map(int, time_str.split(':'))

                            # Create a datetime object with today's date and the specified time
                            # In a real app, you might want to use the end_date or another specific date
                            base_date = datetime.datetime.now().date()
                            if end_date:
                                base_date = end_date

                            resolution_time = datetime.datetime.combine(base_date, datetime.time(hour, minute))
                            print(f"Parsed resolution time: {resolution_time}")
                        except (ValueError, IndexError) as e:
                            print(f"Error parsing resolution time: {e}")
                            # Continue without resolution time if there's an error
                            pass

                    # Look up the category ID based on the category name
                    from app.db.models import Category
                    category_name = entry_data.get('category', 'Not categorized')
                    category = db.query(Category).filter(Category.name == category_name).first()

                    # If category doesn't exist, create it
                    if not category and category_name != 'Not categorized':
                        print(f"Creating new category: {category_name}")
                        # Get an admin user for the created_by_id field
                        admin_user = db.query(User).filter(User.role == RoleEnum.ADMIN).first()
                        created_by_id = admin_user.id if admin_user else uuid.uuid4()

                        category = Category(
                            name=category_name,
                            description=f"Auto-created from log entry",
                            created_by_id=created_by_id,
                            is_active=True
                        )
                        db.add(category)
                        db.flush()  # Get the ID without committing

                    # Create a new LogbookEntry object
                    new_entry = LogbookEntry(
                        id=uuid.uuid4(),
                        user_id=uuid.uuid4(),  # In a real app, this would be the current user's ID
                        start_date=start_date,
                        end_date=end_date,
                        responsible_person=entry_data['responsible_person'],
                        location_id=location.id,
                        device=entry_data['device'],
                        task=task,
                        call_description=entry_data['call_description'],
                        solution_description=entry_data.get('solution_description', ''),
                        resolution_time=resolution_time,  # Add resolution time to the entry
                        status=status,
                        priority=priority,
                        category_id=category.id if category else None,  # Set the category_id field
                        created_at=func.now(),
                        updated_at=func.now()
                    )

                    print(f"Created LogbookEntry object: {new_entry}")

                    # Add and commit to the database
                    db.add(new_entry)
                    db.commit()

                    # Verify the entry was saved
                    check_entry = db.query(LogbookEntry).filter(LogbookEntry.id == new_entry.id).first()
                    if check_entry:
                        print(f"Entry confirmed in database with ID: {check_entry.id}")
                    else:
                        print("Warning: Entry not found in database after commit!")

                    print(f"Entry saved to database with ID: {new_entry.id}")
                except Exception as e:
                    db.rollback()
                    print(f"Error saving entry to database: {e}")
                    import traceback
                    traceback.print_exc()
                    # Show error dialog
                    self.show_dialog("Database Error", f"Failed to save entry: {str(e)}")
                    return
                finally:
                    db.close()

                # Update the statistics based on the entry's status
                self.total_entries = str(int(self.total_entries) + 1)

                # Update the appropriate counter based on the status
                status_value = status.value.lower()
                if status_value == "open":
                    self.open_entries = str(int(self.open_entries) + 1)
                elif status_value == "completed":
                    self.completed_entries = str(int(self.completed_entries) + 1)
                elif status_value == "ongoing":
                    self.ongoing_entries = str(int(self.ongoing_entries) + 1)
                elif status_value == "escalation":
                    self.escalated_entries = str(int(self.escalated_entries) + 1)

                # Add to recent activities
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

                new_activity = {
                    "title": f"New entry: {entry_data['device']}",
                    "description": entry_data['call_description'],
                    "time": current_time,
                    "status": status_value
                }

                # Add the new activity to the beginning of the list
                self.recent_activities.insert(0, new_activity)

                # Rebuild the UI with updated statistics and activities
                self.controls = []
                self.setup_ui()

                # Return to dashboard
                self.page.clean()
                self.page.add(self)
                self.page.update()

                # Show success message
                def close_success_dlg(e):
                    success_dlg.open = False
                    self.page.update()

                success_dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Success"),
                    content=ft.Text("Entry has been saved successfully!"),
                    actions=[
                        ft.TextButton("OK", on_click=close_success_dlg),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )

                self.page.dialog = success_dlg
                success_dlg.open = True
                self.page.update()

            def handle_cancel():
                # Return to dashboard
                self.page.clean()
                self.page.add(self)
                self.page.update()

            # Create and show the new entry view
            new_entry_view = NewEntryView(on_save=handle_save, on_cancel=handle_cancel)
            new_entry_view.page = self.page

            # Replace the current view with the new entry view
            self.page.clean()
            self.page.add(new_entry_view)
            self.page.update()
        else:
            print("Page reference not set")

    def show_report_dialog(self, e):
        """Navigate to the Reports view."""
        print("Navigating to Reports view")
        if self.page:
            self.page.go("/reports")

    def navigate_to_recent_activity(self, e):
        """Navigate to the Recent Activity view."""
        print("Navigating to Recent Activity view")
        if self.page:
            self.page.go("/recent_activity")

    def show_search_dialog(self, e):
        """Navigate to the Search view."""
        print("Search button clicked")
        if self.page:
            # Import here to avoid circular imports
            from app.ui.views.search_view import SearchView

            # Create the search view
            def handle_search(search_params):
                print(f"Searching with parameters: {search_params}")
                # Here you would query the database with search parameters
                # For now, return demo results
                return [
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

            def handle_back():
                # Return to dashboard
                self.page.clean()
                self.page.add(self)
                self.page.update()

            # Create and show the search view
            search_view = SearchView(on_search=handle_search, on_back=handle_back)
            search_view.page = self.page

            # Replace the current view with the search view
            self.page.clean()
            self.page.add(search_view)
            self.page.update()
        else:
            print("Page reference not set")
