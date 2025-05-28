import flet as ft
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import User, Location, Category, Setting, RoleEnum
from werkzeug.security import generate_password_hash
import uuid


# Common UI helper functions
def create_search_field(label="Search", width=300):
    """Create a standard search field"""
    return ft.TextField(
        label=label,
        icon=ft.icons.SEARCH,
        width=width,
    )


def create_action_button(text, icon, on_click, color=ft.colors.ORANGE_600):
    """Create a standard action button"""
    return ft.ElevatedButton(
        text=text,
        icon=icon,
        on_click=on_click,
        bgcolor=color,
        color=ft.colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    )


def create_standard_row(search_field, action_button):
    """Create a standard row with search field and action button"""
    return ft.Row(
        [
            search_field,
            ft.Container(width=10),  # Add spacing between search field and button
            action_button,
            ft.Container(expand=True),  # Push everything to the left
        ],
        alignment=ft.MainAxisAlignment.START,  # Align from the start (left)
    )


def create_confirm_dialog(title, content, on_confirm, on_cancel=None):
    """Create a standard confirmation dialog"""
    return ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Text(content),
        actions=[
            ft.TextButton("Cancel", on_click=on_cancel),
            ft.TextButton("Confirm", on_click=on_confirm),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )


# Base Tab class with common functionality
class BaseTab(ft.Column):
    """Base class for all settings tabs with common functionality"""

    def __init__(self, entity_name, search_label=None):
        super().__init__()
        self.page = None
        self.db = SessionLocal()
        self.entity_name = entity_name
        self.search_label = search_label or f"Search {entity_name}s"

        # Search field
        self.search_field = create_search_field(label=self.search_label)

        # Initialize the UI
        self.scroll = ft.ScrollMode.AUTO

    def close_dialog(self, e):
        """Close the dialog."""
        if self.page and self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def show_snack_bar(self, message, color=ft.colors.GREEN_600):
        """Show a snack bar message"""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message, color=ft.colors.WHITE),
                bgcolor=color,
            )
            self.page.snack_bar.open = True
            self.page.update()


class UserManagementTab(BaseTab):
    def __init__(self):
        super().__init__(entity_name="User", search_label="Search Users")

        # Load users from database
        self.load_users_from_db()

        # Add user button
        print("Creating Add User button")
        self.add_user_button = create_action_button(
            text="Add User",
            icon=ft.icons.PERSON_ADD,
            on_click=self.show_add_user_dialog
        )
        print(f"Add User button created with on_click={self.show_add_user_dialog}")

        # User table
        self.user_table = self.build_user_table()

        # Set up the controls
        self.controls = [
            create_standard_row(self.search_field, self.add_user_button),
            ft.Container(height=20),
            self.user_table,
        ]

    def show_add_user_dialog(self, e):
        """Show the add user dialog."""
        print("show_add_user_dialog called")
        try:
            if not hasattr(self, 'page') or self.page is None:
                print("Error: page reference is not set in UserManagementTab")
                return

            print(f"self.page is {self.page}")

            # Instead of using a dialog, we'll create a modal-like UI directly in the page
            # Create a new container that will overlay the current view

            # First, remove any existing add_user_overlay
            for control in self.page.controls:
                if hasattr(control, 'data') and control.data == 'add_user_overlay':
                    self.page.controls.remove(control)
                    break

            # Create form fields
            username_field = ft.TextField(
                label="Username",
                hint_text="Enter username",
                border_color=ft.colors.BLUE_GREY_400,
                color=ft.colors.BLACK,
                width=300,
                bgcolor=ft.colors.WHITE,
            )

            full_name_field = ft.TextField(
                label="Full Name",
                hint_text="Enter full name",
                border_color=ft.colors.BLUE_GREY_400,
                color=ft.colors.BLACK,
                width=300,
                bgcolor=ft.colors.WHITE,
            )

            email_field = ft.TextField(
                label="Email",
                hint_text="Enter email address",
                border_color=ft.colors.BLUE_GREY_400,
                color=ft.colors.BLACK,
                width=300,
                bgcolor=ft.colors.WHITE,
            )

            password_field = ft.TextField(
                label="Password",
                hint_text="Enter password",
                password=True,
                border_color=ft.colors.BLUE_GREY_400,
                color=ft.colors.BLACK,
                width=300,
                bgcolor=ft.colors.WHITE,
            )

            role_dropdown = ft.Dropdown(
                label="Role",
                hint_text="Select role",
                options=[
                    ft.dropdown.Option("admin", "Admin"),
                    ft.dropdown.Option("manager", "Manager"),
                    ft.dropdown.Option("technician", "Technician"),
                ],
                border_color=ft.colors.BLUE_GREY_400,
                color=ft.colors.BLACK,
                width=300,
                bgcolor=ft.colors.WHITE,
            )

            department_field = ft.TextField(
                label="Department",
                hint_text="Enter department",
                border_color=ft.colors.BLUE_GREY_400,
                color=ft.colors.BLACK,
                width=300,
                bgcolor=ft.colors.WHITE,
            )

            # Store the fields as instance variables for later use
            self.username_field = username_field
            self.full_name_field = full_name_field
            self.email_field = email_field
            self.password_field = password_field
            self.role_dropdown = role_dropdown
            self.department_field = department_field

            # Create the form card
            form_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Add New User", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
                        ft.Divider(),
                        username_field,
                        full_name_field,
                        email_field,
                        password_field,
                        role_dropdown,
                        department_field,
                        ft.Row([
                            ft.ElevatedButton(
                                "Cancel",
                                on_click=self.close_dialog,
                                bgcolor=ft.colors.RED_400,
                                color=ft.colors.WHITE,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            ),
                            ft.ElevatedButton(
                                "Add User",
                                on_click=self.add_user,
                                bgcolor=ft.colors.GREEN_400,
                                color=ft.colors.WHITE,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            ),
                        ], alignment=ft.MainAxisAlignment.END),
                    ], spacing=20),
                    padding=20,
                    bgcolor=ft.colors.WHITE,
                ),
                elevation=10,
                width=400,
            )

            # Create an overlay container
            overlay = ft.Container(
                content=ft.Column([
                    ft.Row([form_card], alignment=ft.MainAxisAlignment.CENTER),
                ], alignment=ft.MainAxisAlignment.CENTER),
                width=self.page.width,
                height=self.page.height,
                bgcolor=ft.colors.with_opacity(0.7, ft.colors.BLACK),
                alignment=ft.alignment.center,
                data="add_user_overlay",  # Tag it for easy identification
            )

            # Add the overlay to the page
            self.page.overlay.append(overlay)
            self.page.update()
            print("User add form should be visible now")

        except Exception as ex:
            print(f"Exception in show_add_user_dialog: {ex}")
            import traceback
            traceback.print_exc()

    def close_dialog(self, e):
        """Close the dialog or overlay form."""
        # Handle overlay form (new method)
        if self.page:
            # Check if there's an overlay to remove
            overlays_to_remove = []
            for overlay in self.page.overlay:
                if hasattr(overlay, 'data') and overlay.data == 'add_user_overlay':
                    overlays_to_remove.append(overlay)

            # Remove the overlays
            for overlay in overlays_to_remove:
                self.page.overlay.remove(overlay)

            # Update the page
            self.page.update()
            print("Form closed")

    def load_users_from_db(self):
        """Load users from the database."""
        try:
            # Query all users from the database
            db_users = self.db.query(User).all()

            # Convert database users to dictionary format for the UI
            self.users = []
            for user in db_users:
                self.users.append({
                    "id": str(user.id),
                    "username": user.username,
                    "full_name": user.full_name,
                    "email": user.email,
                    "role": user.role.value,
                    "department": user.department or "",
                    "is_active": user.is_active,
                })

        except Exception as e:
            print(f"Error loading users from database: {e}")
            # Fallback to sample data if database connection fails
            self.users = [
                {
                    "id": "1",
                    "username": "admin",
                    "full_name": "Admin User",
                    "email": "admin@example.com",
                    "role": "admin",
                    "department": "IT",
                    "is_active": True,
                },
                {
                    "id": "2",
                    "username": "jsmith",
                    "full_name": "John Smith",
                    "email": "john.smith@example.com",
                    "role": "technician",
                    "department": "Maintenance",
                    "is_active": True,
                },
                {
                    "id": "3",
                    "username": "jdoe",
                    "full_name": "Jane Doe",
                    "email": "jane.doe@example.com",
                    "role": "manager",
                    "department": "Operations",
                    "is_active": True,
                },
                {
                    "id": "4",
                    "username": "mjohnson",
                    "full_name": "Mike Johnson",
                    "email": "mike.johnson@example.com",
                    "role": "technician",
                    "department": "Maintenance",
                    "is_active": True,
                },
                {
                    "id": "2",
                    "username": "jsmith",
                    "full_name": "John Smith",
                    "email": "john.smith@example.com",
                    "role": "technician",
                    "department": "Maintenance",
                    "is_active": True,
                },
                {
                    "id": "3",
                    "username": "jdoe",
                    "full_name": "Jane Doe",
                    "email": "jane.doe@example.com",
                    "role": "manager",
                    "department": "Operations",
                    "is_active": True,
                },
                {
                    "id": "4",
                    "username": "mjohnson",
                    "full_name": "Mike Johnson",
                    "email": "mike.johnson@example.com",
                    "role": "technician",
                    "department": "Maintenance",
                    "is_active": False,
                },
            ]

    def add_user(self, e):
        """Add a new user to the database."""
        print("add_user method called")
        try:
            # Get form values
            username = self.username_field.value
            full_name = self.full_name_field.value
            email = self.email_field.value
            password = self.password_field.value
            role = self.role_dropdown.value
            department = self.department_field.value

            # Validate required fields
            if not username or not password or not role:
                print(f"Missing required fields: username={username}, role={role}")
                self.page.snack_bar = ft.SnackBar(content=ft.Text("Missing required fields"))
                self.page.snack_bar.open = True
                self.page.update()
                return

            print(f"Form values: username={username}, role={role}")

            # Check if email already exists
            if email:
                existing_user = self.db.query(User).filter(User.email == email).first()
                if existing_user:
                    print(f"Email {email} already exists in the database")
                    self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Email {email} is already registered"))
                    self.page.snack_bar.open = True
                    self.page.update()
                    return

            # Convert role string to enum
            role_enum = RoleEnum.TECHNICIAN  # Default role
            if role == "admin":
                role_enum = RoleEnum.ADMIN
                print("Role converted to: RoleEnum.ADMIN")
            elif role == "manager":
                role_enum = RoleEnum.MANAGER
                print("Role converted to: RoleEnum.MANAGER")
            else:
                print("Role converted to: RoleEnum.TECHNICIAN")

            # Generate a UUID for the user
            user_id = uuid.uuid4()
            print(f"Generated UUID: {user_id}")

            # Create user object
            new_user = User(
                id=user_id,
                username=username,
                full_name=full_name,
                email=email,
                password_hash=generate_password_hash(password),
                role=role_enum,
                department=department,
                is_active=True
            )
            print("User object created, adding to database")

            # Add to database
            self.db.add(new_user)
            self.db.commit()
            print(f"User added to database with ID: {user_id}")

            # Close the overlay form
            self.close_dialog(e)

            # Refresh the user list
            self.load_users_from_db()

            # Show success message
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"User {username} added successfully"))
            self.page.snack_bar.open = True
            self.page.update()

        except Exception as ex:
            print(f"Error adding user: {ex}")
            # Rollback the transaction in case of error
            self.db.rollback()

            # Close the overlay form
            self.close_dialog(e)

            # Show error message
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Error adding user: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def edit_user(self, e):
        """Edit an existing user."""
        try:
            # Get the user ID from the event data
            user_id = e.control.data

            # Find the user in the database
            user = self.db.query(User).filter(User.id == user_id).first()

            if user:
                # Show edit user dialog (to be implemented)
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Editing user {user.username}", color=ft.colors.WHITE),
                        bgcolor=ft.colors.BLUE_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                # User not found
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("User not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error editing user: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error: {str(e)}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def delete_user(self, e):
        """Delete a user from the system."""
        try:
            # Get the user ID from the event data
            user_id = e.control.data

            # Show confirmation dialog
            self.confirm_delete_user(user_id)

        except Exception as e:
            print(f"Error deleting user: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error: {str(e)}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def confirm_delete_user(self, user_id):
        """Confirm deletion of a user."""
        try:
            # Find the user in the database
            user = self.db.query(User).filter(User.id == user_id).first()

            if user:
                # Show confirmation dialog
                if self.page:
                    self.page.dialog = ft.AlertDialog(
                        title=ft.Text("Confirm Deletion", color=ft.colors.BLACK),
                        content=ft.Text(f"Are you sure you want to delete user {user.username}?",
                                        color=ft.colors.BLACK),
                        actions=[
                            ft.TextButton("Cancel", on_click=self.close_dialog),
                            ft.TextButton(
                                "Delete",
                                on_click=lambda e: self.perform_delete_user(user_id),
                                style=ft.ButtonStyle(
                                    color={ft.MaterialState.DEFAULT: ft.colors.RED_600}
                                ),
                            ),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    self.page.dialog.open = True
                    self.page.update()
            else:
                # User not found
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("User not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error confirming delete user: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error deleting user", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def perform_delete_user(self, user_id):
        """Actually delete the user after confirmation."""
        try:
            # Find the user in the database
            user = self.db.query(User).filter(User.id == user_id).first()

            if user:
                # Delete from database
                self.db.delete(user)
                self.db.commit()

                # Remove from UI list
                self.users = [u for u in self.users if u["id"] != str(user_id)]

                # Rebuild the user table
                self.user_table = self.build_user_table()

                # Update the controls
                self.controls = [
                    ft.Row(
                        [
                            self.search_field,
                            self.add_user_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    self.user_table,
                ]
                self.update()

                # Show success message
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"User deleted successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("User not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error deleting user: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error: {str(e)}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

        # Close the dialog
        self.close_dialog(None)

    def build_user_table(self):
        """Build the user table with current users."""
        try:
            columns = [
                ft.DataColumn(ft.Text("Username", color=ft.colors.BLACK)),
                ft.DataColumn(ft.Text("Full Name", color=ft.colors.BLACK)),
                ft.DataColumn(ft.Text("Email", color=ft.colors.BLACK)),
                ft.DataColumn(ft.Text("Role", color=ft.colors.BLACK)),
                ft.DataColumn(ft.Text("Department", color=ft.colors.BLACK)),
                ft.DataColumn(ft.Text("Status", color=ft.colors.BLACK)),
                ft.DataColumn(ft.Text("Actions", color=ft.colors.BLACK)),
            ]

            rows = []
            for user in self.users:
                # Create row
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(user["username"], color=ft.colors.BLACK)),
                            ft.DataCell(ft.Text(user["full_name"], color=ft.colors.BLACK)),
                            ft.DataCell(ft.Text(user["email"], color=ft.colors.BLACK)),
                            ft.DataCell(ft.Text(user["role"], color=ft.colors.BLACK)),
                            ft.DataCell(ft.Text(user["department"], color=ft.colors.BLACK)),
                            ft.DataCell(
                                ft.Text(
                                    "Active" if user["is_active"] else "Inactive",
                                    color=ft.colors.GREEN if user["is_active"] else ft.colors.RED,
                                )
                            ),
                            ft.DataCell(
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.icons.EDIT,
                                            tooltip="Edit User",
                                            icon_color=ft.colors.BLUE,
                                            data=user["id"],
                                            on_click=self.edit_user,
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE,
                                            tooltip="Delete User",
                                            icon_color=ft.colors.RED,
                                            data=user["id"],
                                            on_click=self.delete_user,
                                        ),
                                        ft.Switch(
                                            value=user["is_active"],
                                            active_color=ft.colors.GREEN,
                                            inactive_thumb_color=ft.colors.GREY,
                                            data={"user_id": user["id"], "index": self.users.index(user)},
                                            on_change=self.toggle_user_status,
                                        ),
                                    ]
                                )
                            ),
                        ]
                    )
                )

            return ft.DataTable(
                columns=columns,
                rows=rows,
                border=ft.border.all(1, ft.colors.GREY_400),
                border_radius=10,
                vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
                horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
                sort_column_index=0,
                sort_ascending=True,
                heading_row_height=70,
                data_row_min_height=60,
                width=1200,
            )
        except Exception as e:
            print(f"Error building user table: {e}")
            return ft.Text(f"Error loading users: {str(e)}")

    def toggle_user_status(self, e):
        """Toggle user active status."""
        try:
            # Get the user ID and index from the event data
            data = e.control.data
            user_id = data["user_id"]
            index = data["index"]
            new_status = e.control.value

            print(f"Toggling status for user ID: {user_id}, new status: {new_status}")

            # Convert string UUID to UUID object if needed
            if isinstance(user_id, str):
                import uuid
                try:
                    user_id = uuid.UUID(user_id)
                except ValueError as ve:
                    print(f"Error converting UUID: {ve}")

            # Find the user in the database
            user = self.db.query(User).filter(User.id == user_id).first()

            if user:
                # Set the user's active status to match the switch
                user.is_active = new_status
                print(f"User {user.username} status set to: {user.is_active}")
                self.db.commit()

                # Update the user in the UI list directly using the index
                self.users[index]["is_active"] = new_status
                print(f"Updated UI list item at index {index}: {self.users[index]}")

                # Force immediate update of the status text in the table
                status_cell = self.user_table.rows[index].cells[5]
                status_cell.content.value = "Active" if new_status else "Inactive"
                status_cell.content.color = ft.colors.GREEN if new_status else ft.colors.RED

                # Show success message
                status = "activated" if new_status else "deactivated"
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"User {user.username} {status} successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True

                # Rebuild the user table
                self.user_table = self.build_user_table()

                # Update the controls
                self.controls = [
                    ft.Row(
                        [
                            self.search_field,
                            self.add_user_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    self.user_table,
                ]

                # Show success message
                status = "activated" if user.is_active else "deactivated"
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"User {user.username} {status} successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("User not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error toggling user status: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error toggling user status", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()


class LocationsTab(BaseTab):
    def __init__(self):
        super().__init__(entity_name="Location", search_label="Search Locations")

        # Load locations from database
        self.load_locations_from_db()

        # Add location button
        self.add_location_button = create_action_button(
            text="Add Location",
            icon=ft.icons.ADD_LOCATION,
            on_click=self.show_add_location_dialog
        )

        # Location table
        self.location_table = self.build_location_table()

        # Set up the controls
        self.controls = [
            create_standard_row(self.search_field, self.add_location_button),
            ft.Container(height=20),
            self.location_table,
        ]

    def build_location_table(self):
        """Build the location table with current locations."""
        columns = [
            ft.DataColumn(ft.Text("Name", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Description", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Address", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Status", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Actions", color=ft.colors.BLACK)),
        ]

        rows = []
        for location in self.locations:
            # Create row
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(location["name"], color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(location["description"], color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(location["address"], color=ft.colors.BLACK)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    "Active" if location["is_active"] else "Inactive",
                                    color=ft.colors.WHITE,
                                    size=12,
                                ),
                                bgcolor=ft.colors.GREEN if location["is_active"] else ft.colors.GREY,
                                border_radius=20,
                                padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                                alignment=ft.alignment.center,
                            )
                        ),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        tooltip="Edit",
                                        icon_color=ft.colors.BLUE,
                                        on_click=self.edit_location,
                                        data=location["id"],
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        tooltip="Delete",
                                        icon_color=ft.colors.RED,
                                        on_click=self.delete_location,
                                        data=location["id"],
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )

        return ft.DataTable(
            columns=columns,
            rows=rows,
            border=ft.border.all(1, ft.colors.BLUE_GREY_200),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_100),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_100),
            heading_row_height=70,
            data_row_min_height=70,
            data_row_max_height=100,
            column_spacing=5,
        )

    def load_locations_from_db(self):
        """Load locations from the database."""
        try:
            # Query all locations from the database
            db_locations = self.db.query(Location).all()

            # Convert database locations to dictionary format for the UI
            self.locations = []
            for location in db_locations:
                self.locations.append({
                    "id": str(location.id),
                    "name": location.name,
                    "description": location.description,
                    "address": location.address,
                    "is_active": location.is_active,
                })

        except Exception as e:
            print(f"Error loading locations: {e}")
            # Fallback to real location data if database query fails
            self.locations = [
                {
                    "id": "1",
                    "name": "Bundelwikkelaar",
                    "description": "Production Line",
                    "address": "Building A, 1st Floor",
                    "is_active": True,
                },
                {
                    "id": "2",
                    "name": "Stacker platfrom 1/2",
                    "description": "Production Line",
                    "address": "Building A, 1st Floor",
                    "is_active": True,
                },
                {
                    "id": "3",
                    "name": "Pers",
                    "description": "Production Line",
                    "address": "Building A, 1st Floor",
                    "is_active": True,
                },
                {
                    "id": "4",
                    "name": "Kaltenbach",
                    "description": "Production Line",
                    "address": "Building B, Ground Floor",
                    "is_active": True,
                },
                {
                    "id": "5",
                    "name": "Billetoven",
                    "description": "Production Line",
                    "address": "Building B, Ground Floor",
                    "is_active": True,
                },
                {
                    "id": "6",
                    "name": "Paaltafel",
                    "description": "Production Line",
                    "address": "Building B, Ground Floor",
                    "is_active": True,
                },
                {
                    "id": "7",
                    "name": "Koudzaag",
                    "description": "Production Line",
                    "address": "Building C, 2nd Floor",
                    "is_active": True,
                },
                {
                    "id": "8",
                    "name": "Hardingsoven",
                    "description": "Production Line",
                    "address": "Building C, 2nd Floor",
                    "is_active": True,
                },
                {
                    "id": "9",
                    "name": "Infra",
                    "description": "Infrastructure",
                    "address": "Building D, Ground Floor",
                    "is_active": True,
                },
                {
                    "id": "10",
                    "name": "Scrap",
                    "description": "Waste Management",
                    "address": "Building D, Ground Floor",
                    "is_active": True,
                },
                {
                    "id": "11",
                    "name": "Koeltafel",
                    "description": "Production Line",
                    "address": "Building C, 2nd Floor",
                    "is_active": True,
                },
                {
                    "id": "12",
                    "name": "Destacker 1/2/3",
                    "description": "Production Line",
                    "address": "Building A, 1st Floor",
                    "is_active": True,
                },
                {
                    "id": "13",
                    "name": "Warmzaag",
                    "description": "Production Line",
                    "address": "Building B, Ground Floor",
                    "is_active": True,
                },
                {
                    "id": "14",
                    "name": "Borstelmachine",
                    "description": "Production Line",
                    "address": "Building C, 2nd Floor",
                    "is_active": True,
                },
                {
                    "id": "15",
                    "name": "Profielwikkelaar",
                    "description": "Production Line",
                    "address": "Building A, 1st Floor",
                    "is_active": True,
                },
                {
                    "id": "16",
                    "name": "Kopzaag",
                    "description": "Production Line",
                    "address": "Building B, Ground Floor",
                    "is_active": True,
                },
                {
                    "id": "17",
                    "name": "Die's",
                    "description": "Production Line",
                    "address": "Building C, 2nd Floor",
                    "is_active": True,
                },
                {
                    "id": "18",
                    "name": "Plier",
                    "description": "Production Line",
                    "address": "Building A, 1st Floor",
                    "is_active": True,
                },
                {
                    "id": "19",
                    "name": "Puller",
                    "description": "Production Line",
                    "address": "Building B, Ground Floor",
                    "is_active": True,
                },
                {
                    "id": "20",
                    "name": "Runout-tafel",
                    "description": "Production Line",
                    "address": "Building C, 2nd Floor",
                    "is_active": True,
                },
            ]

    def show_add_location_dialog(self, e):
        """Show dialog to add a new location."""
        if self.page:
            # Create text fields for the dialog
            self.name_field = ft.TextField(label="Location Name", autofocus=True)
            self.description_field = ft.TextField(label="Description")
            self.address_field = ft.TextField(label="Address")

            # Create the dialog
            self.add_location_dialog = ft.AlertDialog(
                title=ft.Text("Add New Location"),
                content=ft.Column(
                    [
                        self.name_field,
                        self.description_field,
                        self.address_field,
                    ],
                    width=400,
                    height=300,
                    scroll=ft.ScrollMode.AUTO,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=self.close_dialog),
                    ft.TextButton("Add", on_click=self.add_location),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            # Show the dialog
            self.page.dialog = self.add_location_dialog
            self.page.dialog.open = True
            self.page.update()

    def close_dialog(self, e):
        """Close the dialog."""
        if self.page and self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def add_location(self, e):
        """Add a new location to the system."""
        # Validate form fields
        if not self.name_field.value:
            # Show error message
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Please enter a location name", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
            return

        try:
            # Get the first user as the creator (in a real app, this would be the current user)
            user = self.db.query(User).first()
            if not user:
                raise Exception("No users found in the database")

            # Create a new location in the database
            new_location_db = Location(
                name=self.name_field.value,
                description=self.description_field.value,
                created_by_id=user.id,
                is_active=True
            )

            self.db.add(new_location_db)
            self.db.commit()
            self.db.refresh(new_location_db)

            # Add the new location to the UI list
            new_location = {
                "id": str(new_location_db.id),
                "name": new_location_db.name,
                "description": new_location_db.description or "",
                "address": new_location_db.description or "",  # Using description as address for now
                "is_active": new_location_db.is_active,
            }
            self.locations.append(new_location)

        except Exception as e:
            # If database operation fails, show error and add to local list only
            print(f"Error adding location to database: {e}")
            new_location = {
                "id": str(len(self.locations) + 1),
                "name": self.name_field.value,
                "description": self.description_field.value,
                "address": self.address_field.value,
                "is_active": True,
            }
            self.locations.append(new_location)

        # Rebuild the location table with the updated data
        self.location_table = self.build_location_table()

        # Update the controls
        self.controls = [
            ft.Row(
                [
                    self.search_field,
                    self.add_location_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Container(height=20),
            self.location_table,
        ]

        # Show success message
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Location {new_location['name']} added successfully", color=ft.colors.WHITE),
                bgcolor=ft.colors.GREEN_600,
            )
            self.page.snack_bar.open = True
            self.page.update()

        # Close the dialog
        self.close_dialog(None)

    def edit_location(self, e):
        """Edit an existing location."""
        try:
            # Get the location ID from the event data
            location_id = e.control.data

            # Find the location in the database
            location = self.db.query(Location).filter(Location.id == location_id).first()

            if location:
                # Create text fields for the dialog with current values
                self.edit_name_field = ft.TextField(label="Location Name", value=location.name)
                self.edit_description_field = ft.TextField(label="Description", value=location.description or "")
                self.edit_address_field = ft.TextField(label="Address", value=location.description or "")

                # Create the dialog
                self.edit_location_dialog = ft.AlertDialog(
                    title=ft.Text(f"Edit Location: {location.name}"),
                    content=ft.Column(
                        [
                            self.edit_name_field,
                            self.edit_description_field,
                            self.edit_address_field,
                        ],
                        width=400,
                        height=300,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    actions=[
                        ft.TextButton("Cancel", on_click=self.close_dialog),
                        ft.TextButton("Save", on_click=lambda e: self.save_location_edit(location_id)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )

                # Show the dialog
                if self.page:
                    self.page.dialog = self.edit_location_dialog
                    self.page.dialog.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Location not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error editing location: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error editing location", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def save_location_edit(self, location_id):
        """Save the edited location."""
        try:
            # Find the location in the database
            location = self.db.query(Location).filter(Location.id == location_id).first()

            if location:
                # Update the location in the database
                location.name = self.edit_name_field.value
                location.description = self.edit_description_field.value
                self.db.commit()

                # Update the location in the UI list
                for loc in self.locations:
                    if loc["id"] == str(location_id):
                        loc["name"] = location.name
                        loc["description"] = location.description or ""
                        loc["address"] = location.description or ""
                        break

                # Rebuild the location table
                self.location_table = self.build_location_table()

                # Update the controls
                self.controls = [
                    ft.Row(
                        [
                            self.search_field,
                            self.add_location_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    self.location_table,
                ]

                # Show success message
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Location {location.name} updated successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Location not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error saving location edit: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error saving location", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

        # Close the dialog
        self.close_dialog(None)

    def delete_location(self, e):
        """Delete a location."""
        try:
            # Get the location ID from the event data
            location_id = e.control.data

            # Find the location in the database
            location = self.db.query(Location).filter(Location.id == location_id).first()

            if location:
                # Show confirmation dialog
                if self.page:
                    self.page.dialog = ft.AlertDialog(
                        title=ft.Text(f"Delete Location: {location.name}"),
                        content=ft.Text("Are you sure you want to delete this location? This action cannot be undone."),
                        actions=[
                            ft.TextButton("Cancel", on_click=self.close_dialog),
                            ft.TextButton("Delete", on_click=lambda e: self.confirm_delete_location(location_id)),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    self.page.dialog.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Location not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error deleting location: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error deleting location", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def confirm_delete_location(self, location_id):
        """Confirm deletion of a location."""
        try:
            # Find the location in the database
            location = self.db.query(Location).filter(Location.id == location_id).first()

            if location:
                # Delete the location from the database
                self.db.delete(location)
                self.db.commit()

                # Remove the location from the UI list
                self.locations = [loc for loc in self.locations if loc["id"] != str(location_id)]

                # Rebuild the location table
                self.location_table = self.build_location_table()

                # Update the controls
                self.controls = [
                    ft.Row(
                        [
                            self.search_field,
                            self.add_location_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    self.location_table,
                ]

                # Show success message
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Location deleted successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Location not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error confirming delete location: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error deleting location", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

        # Close the dialog
        self.close_dialog(None)


class CategoriesTab(BaseTab):
    def __init__(self):
        super().__init__(entity_name="Category", search_label="Search Categories")

        # Load categories from database
        self.load_categories_from_db()

        # Add category button
        self.add_category_button = create_action_button(
            text="Add Category",
            icon=ft.icons.ADD_CIRCLE,
            on_click=self.show_add_category_dialog
        )

        # Category table
        self.category_table = self.build_category_table()

        # Set up the controls
        self.controls = [
            create_standard_row(self.search_field, self.add_category_button),
            ft.Container(height=20),
            self.category_table,
        ]

    def build_category_table(self):
        """Build the category table with current categories."""
        columns = [
            ft.DataColumn(ft.Text("Name", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Description", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Subcategories", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Color", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Status", color=ft.colors.BLACK)),
            ft.DataColumn(ft.Text("Actions", color=ft.colors.BLACK)),
        ]

        rows = []
        for category in self.categories:
            # Create row
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(category["name"], color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(category["description"], color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(", ".join(category["subcategories"]), color=ft.colors.BLACK)),
                        ft.DataCell(
                            ft.Container(
                                bgcolor=category["color"],
                                width=30,
                                height=30,
                                border_radius=15,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    "Active" if category["is_active"] else "Inactive",
                                    color=ft.colors.WHITE,
                                    size=12,
                                ),
                                bgcolor=ft.colors.GREEN if category["is_active"] else ft.colors.GREY,
                                border_radius=20,
                                padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                                alignment=ft.alignment.center,
                            )
                        ),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        tooltip="Edit",
                                        icon_color=ft.colors.BLUE,
                                        on_click=self.edit_category,
                                        data=category["id"],
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        tooltip="Delete",
                                        icon_color=ft.colors.RED,
                                        on_click=self.delete_category,
                                        data=category["id"],
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.BLOCK if category["is_active"] else ft.icons.CHECK_CIRCLE,
                                        tooltip="Disable" if category["is_active"] else "Enable",
                                        icon_color=ft.colors.RED if category["is_active"] else ft.colors.GREEN,
                                        on_click=self.toggle_category_status,
                                        data=category["id"],
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )

        return ft.DataTable(
            columns=columns,
            rows=rows,
            border=ft.border.all(1, ft.colors.BLUE_GREY_200),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_100),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_100),
            heading_row_height=70,
            data_row_min_height=70,
            data_row_max_height=100,
            column_spacing=5,
        )

    def load_categories_from_db(self):
        """Load categories from the database."""
        try:
            # Query all categories from the database
            db_categories = self.db.query(Category).all()

            # Convert database categories to dictionary format for the UI
            self.categories = []
            for category in db_categories:
                # Map color code to flet color
                color = ft.colors.BLUE
                if category.color_code:
                    if category.color_code.startswith('#'):
                        color = category.color_code
                    else:
                        # Try to map string color names to flet colors
                        color_map = {
                            'red': ft.colors.RED,
                            'blue': ft.colors.BLUE,
                            'green': ft.colors.GREEN,
                            'yellow': ft.colors.YELLOW,
                            'purple': ft.colors.PURPLE,
                            'orange': ft.colors.ORANGE,
                        }
                        color = color_map.get(category.color_code.lower(), ft.colors.BLUE)

                self.categories.append({
                    "id": str(category.id),
                    "name": category.name,
                    "description": category.description or "",
                    "color": color,
                    "subcategories": [],  # No subcategories in the database model yet
                    "is_active": category.is_active,
                })

        except Exception as e:
            print(f"Error loading categories from database: {e}")
            # Fallback to real task categories from the new entry view
            self.categories = [
                {
                    "id": "1",
                    "name": "Interventie",
                    "description": "Intervention tasks and emergency repairs",
                    "color": ft.colors.RED,
                    "subcategories": ["Emergency", "Critical"],
                    "is_active": True,
                },
                {
                    "id": "2",
                    "name": "Onderhoud",
                    "description": "Maintenance and regular upkeep",
                    "color": ft.colors.BLUE,
                    "subcategories": ["Preventive", "Scheduled"],
                    "is_active": True,
                },
                {
                    "id": "3",
                    "name": "Facilities",
                    "description": "Facility management and infrastructure",
                    "color": ft.colors.GREEN,
                    "subcategories": ["Building", "Equipment"],
                    "is_active": True,
                },
                {
                    "id": "4",
                    "name": "NVT",
                    "description": "Not applicable or other tasks",
                    "color": ft.colors.GREY,
                    "subcategories": ["Other", "Miscellaneous"],
                    "is_active": True,
                },
            ]

    def close_dialog(self, e):
        """Close the dialog."""
        if self.page and self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def show_add_category_dialog(self, e):
        """Show dialog to add a new category."""
        if self.page:
            # Create text fields for the dialog
            self.name_field = ft.TextField(label="Category Name", autofocus=True)
            self.description_field = ft.TextField(label="Description")

            # Create color dropdown
            self.color_dropdown = ft.Dropdown(
                label="Color",
                options=[
                    ft.dropdown.Option("RED", text="Red"),
                    ft.dropdown.Option("BLUE", text="Blue"),
                    ft.dropdown.Option("GREEN", text="Green"),
                    ft.dropdown.Option("YELLOW", text="Yellow"),
                    ft.dropdown.Option("PURPLE", text="Purple"),
                    ft.dropdown.Option("ORANGE", text="Orange"),
                ],
                value="BLUE",
            )

            # Create the dialog
            self.add_category_dialog = ft.AlertDialog(
                title=ft.Text("Add New Category"),
                content=ft.Column(
                    [
                        self.name_field,
                        self.description_field,
                        self.color_dropdown,
                    ],
                    width=400,
                    height=300,
                    scroll=ft.ScrollMode.AUTO,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=self.close_dialog),
                    ft.TextButton("Add", on_click=self.add_category),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            # Show the dialog
            self.page.dialog = self.add_category_dialog
            self.page.dialog.open = True
            self.page.update()

    def add_category(self, e):
        """Add a new category to the system."""
        # Validate form fields
        if not self.name_field.value:
            # Show error message
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Please enter a category name", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
            return

        try:
            # Get the first user as the creator (in a real app, this would be the current user)
            user = self.db.query(User).first()
            if not user:
                raise Exception("No users found in the database")

            # Map color string to color code
            color_code = self.color_dropdown.value.lower()

            # Create a new category in the database
            new_category_db = Category(
                name=self.name_field.value,
                description=self.description_field.value,
                color_code=color_code,
                created_by_id=user.id,
                is_active=True
            )

            self.db.add(new_category_db)
            self.db.commit()
            self.db.refresh(new_category_db)

            # Map color to flet color
            color_map = {
                'red': ft.colors.RED,
                'blue': ft.colors.BLUE,
                'green': ft.colors.GREEN,
                'yellow': ft.colors.YELLOW,
                'purple': ft.colors.PURPLE,
                'orange': ft.colors.ORANGE,
            }
            color = color_map.get(color_code.lower(), ft.colors.BLUE)

            # Add the new category to the UI list
            new_category = {
                "id": str(new_category_db.id),
                "name": new_category_db.name,
                "description": new_category_db.description or "",
                "color": color,
                "subcategories": [],
                "is_active": new_category_db.is_active,
            }
            self.categories.append(new_category)

        except Exception as e:
            # If database operation fails, show error and add to local list only
            print(f"Error adding category to database: {e}")
            new_category = {
                "id": str(len(self.categories) + 1),
                "name": self.name_field.value,
                "description": self.description_field.value,
                "color": getattr(ft.colors, self.color_dropdown.value),
                "subcategories": [],
                "is_active": True,
            }
            self.categories.append(new_category)

        # Rebuild the category table with the updated data
        self.category_table = self.build_category_table()

        # Update the controls
        self.controls = [
            ft.Row(
                [
                    self.search_field,
                    self.add_category_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Container(height=20),
            self.category_table,
        ]

        # Show success message
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Category {new_category['name']} added successfully", color=ft.colors.WHITE),
                bgcolor=ft.colors.GREEN_600,
            )
            self.page.snack_bar.open = True
            self.page.update()

        # Close the dialog
        self.close_dialog(None)

    def edit_category(self, e):
        """Edit an existing category."""
        try:
            # Get the category ID from the event data
            category_id = e.control.data

            # Find the category in the database
            category = self.db.query(Category).filter(Category.id == category_id).first()

            if category:
                # Get color value for dropdown
                color_value = "BLUE"
                if category.color_code:
                    color_value = category.color_code.upper()

                # Create text fields for the dialog with current values
                self.edit_name_field = ft.TextField(label="Category Name", value=category.name)
                self.edit_description_field = ft.TextField(label="Description", value=category.description or "")

                # Create color dropdown
                self.edit_color_dropdown = ft.Dropdown(
                    label="Color",
                    options=[
                        ft.dropdown.Option("RED", text="Red"),
                        ft.dropdown.Option("BLUE", text="Blue"),
                        ft.dropdown.Option("GREEN", text="Green"),
                        ft.dropdown.Option("YELLOW", text="Yellow"),
                        ft.dropdown.Option("PURPLE", text="Purple"),
                        ft.dropdown.Option("ORANGE", text="Orange"),
                    ],
                    value=color_value,
                )

                # Create the dialog
                self.edit_category_dialog = ft.AlertDialog(
                    title=ft.Text(f"Edit Category: {category.name}"),
                    content=ft.Column(
                        [
                            self.edit_name_field,
                            self.edit_description_field,
                            self.edit_color_dropdown,
                        ],
                        width=400,
                        height=300,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    actions=[
                        ft.TextButton("Cancel", on_click=self.close_dialog),
                        ft.TextButton("Save", on_click=lambda e: self.save_category_edit(category_id)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )

                # Show the dialog
                if self.page:
                    self.page.dialog = self.edit_category_dialog
                    self.page.dialog.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Category not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error editing category: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error editing category", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def save_category_edit(self, category_id):
        """Save the edited category."""
        try:
            # Find the category in the database
            category = self.db.query(Category).filter(Category.id == category_id).first()

            if category:
                # Update the category in the database
                category.name = self.edit_name_field.value
                category.description = self.edit_description_field.value
                category.color_code = self.edit_color_dropdown.value.lower()
                self.db.commit()

                # Map color to flet color
                color_map = {
                    'red': ft.colors.RED,
                    'blue': ft.colors.BLUE,
                    'green': ft.colors.GREEN,
                    'yellow': ft.colors.YELLOW,
                    'purple': ft.colors.PURPLE,
                    'orange': ft.colors.ORANGE,
                }
                color = color_map.get(category.color_code.lower(), ft.colors.BLUE)

                # Update the category in the UI list
                for cat in self.categories:
                    if cat["id"] == str(category_id):
                        cat["name"] = category.name
                        cat["description"] = category.description or ""
                        cat["color"] = color
                        break

                # Rebuild the category table
                self.category_table = self.build_category_table()

                # Update the controls
                self.controls = [
                    ft.Row(
                        [
                            self.search_field,
                            self.add_category_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    self.category_table,
                ]

                # Show success message
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Category {category.name} updated successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Category not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error saving category edit: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error saving category", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

        # Close the dialog
        self.close_dialog(None)

    def delete_category(self, e):
        """Delete a category."""
        try:
            # Get the category ID from the event data
            category_id = e.control.data

            # Find the category in the database
            category = self.db.query(Category).filter(Category.id == category_id).first()

            if category:
                # Show confirmation dialog
                if self.page:
                    self.page.dialog = ft.AlertDialog(
                        title=ft.Text(f"Delete Category: {category.name}"),
                        content=ft.Text("Are you sure you want to delete this category? This action cannot be undone."),
                        actions=[
                            ft.TextButton("Cancel", on_click=self.close_dialog),
                            ft.TextButton("Delete", on_click=lambda e: self.confirm_delete_category(category_id)),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    self.page.dialog.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Category not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error deleting category: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error deleting category", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def confirm_delete_category(self, category_id):
        """Confirm deletion of a category."""
        try:
            # Find the category in the database
            category = self.db.query(Category).filter(Category.id == category_id).first()

            if category:
                # Delete the category from the database
                self.db.delete(category)
                self.db.commit()

                # Remove the category from the UI list
                self.categories = [cat for cat in self.categories if cat["id"] != str(category_id)]

                # Rebuild the category table
                self.category_table = self.build_category_table()

                # Update the controls
                self.controls = [
                    ft.Row(
                        [
                            self.search_field,
                            self.add_category_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    self.category_table,
                ]

                # Show success message
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Category deleted successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Category not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error confirming delete category: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error deleting category", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

        # Close the dialog
        self.close_dialog(None)

    def toggle_category_status(self, e):
        """Toggle category active status."""
        try:
            # Get the category ID from the event data
            category_id = e.control.data

            # Find the category in the database
            category = self.db.query(Category).filter(Category.id == category_id).first()

            if category:
                # Toggle the category's active status
                category.is_active = not category.is_active
                self.db.commit()

                # Update the category in the UI list
                for cat in self.categories:
                    if cat["id"] == str(category_id):
                        cat["is_active"] = category.is_active
                        break

                # Rebuild the category table
                self.category_table = self.build_category_table()

                # Update the controls
                self.controls = [
                    ft.Row(
                        [
                            self.search_field,
                            self.add_category_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    self.category_table,
                ]

                # Show success message
                status = "activated" if category.is_active else "deactivated"
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Category {category.name} {status} successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Category not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"Error toggling category status: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error toggling category status", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()


class SystemSettingsTab(BaseTab):
    def __init__(self):
        super().__init__(entity_name="System", search_label=None)
        self.db = SessionLocal()

        # Application settings
        self.app_name_field = ft.TextField(
            label="Application Name",
            value="LogBook",
            width=300,
            color=ft.colors.BLACK,
            border_color=ft.colors.ORANGE_600,
            focused_border_color=ft.colors.ORANGE_600,
        )

        self.company_name_field = ft.TextField(
            label="Company Name",
            value="Your Company",
            width=300,
            color=ft.colors.BLACK,
            border_color=ft.colors.ORANGE_600,
            focused_border_color=ft.colors.ORANGE_600,
        )

        self.company_logo_field = ft.TextField(
            label="Company Logo URL",
            value="/assets/logo.png",
            width=300,
            color=ft.colors.BLACK,
            border_color=ft.colors.ORANGE_600,
            focused_border_color=ft.colors.ORANGE_600,
        )

        self.logo_upload_button = ft.ElevatedButton(
            text="Upload Logo",
            icon=ft.icons.UPLOAD_FILE,
            bgcolor=ft.colors.ORANGE_600,
            color=ft.colors.WHITE,
        )

        self.theme_dropdown = ft.Dropdown(
            label="Default Theme",
            width=300,
            options=[
                ft.dropdown.Option("light", "Light"),
                ft.dropdown.Option("dark", "Dark"),
                ft.dropdown.Option("system", "System Default"),
            ],
            value="dark",
            bgcolor=ft.colors.WHITE,
            color=ft.colors.BLACK,
            border_color=ft.colors.ORANGE_600,
            focused_border_color=ft.colors.ORANGE_600,
            focused_bgcolor=ft.colors.WHITE,
        )

        # Email settings
        self.smtp_server_field = ft.TextField(
            label="SMTP Server",
            value="smtp.example.com",
            width=300,
            color=ft.colors.BLACK,
            border_color=ft.colors.ORANGE_600,
            focused_border_color=ft.colors.ORANGE_600,
        )

        self.smtp_port_field = ft.TextField(
            label="SMTP Port",
            value="587",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
            color=ft.colors.BLACK,
            border_color=ft.colors.ORANGE_600,
            focused_border_color=ft.colors.ORANGE_600,
        )

        self.smtp_username_field = ft.TextField(
            label="SMTP Username",
            value="user@example.com",
            width=300,
            color=ft.colors.BLACK,
            border_color=ft.colors.ORANGE_600,
            focused_border_color=ft.colors.ORANGE_600,
        )

        # Backup settings
        self.auto_backup_switch = ft.Switch(
            label="Enable Automatic Backups",
            value=True,
            active_color=ft.colors.ORANGE_600,
            active_track_color=ft.colors.ORANGE_400,
        )

        self.backup_frequency_dropdown = ft.Dropdown(
            label="Backup Frequency",
            width=300,
            options=[
                ft.dropdown.Option("daily", "Daily"),
                ft.dropdown.Option("weekly", "Weekly"),
                ft.dropdown.Option("monthly", "Monthly"),
            ],
            value="weekly",  # Default value
            bgcolor=ft.colors.WHITE,
            color=ft.colors.BLACK,
            border_color=ft.colors.ORANGE_600,
            focused_border_color=ft.colors.ORANGE_600,
            focused_bgcolor=ft.colors.WHITE,
        )

        self.backup_retention_field = ft.TextField(
            label="Backup Retention (days)",
            value="30",
            width=300,
            color=ft.colors.BLACK,
            border_color=ft.colors.ORANGE_600,
            focused_border_color=ft.colors.ORANGE_600,
        )

        self.backup_now_button = create_action_button(
            text="Backup Now",
            icon=ft.icons.BACKUP,
            on_click=self.backup_now,
            color=ft.colors.WHITE
        )

        # Save button
        self.save_settings_button = create_action_button(
            text="Save Settings",
            icon=ft.icons.SAVE,
            on_click=self.save_settings
        )

        # Set up the controls
        self.controls = [
            # General Settings
            ft.Container(
                content=ft.Text("General Settings", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
                margin=ft.margin.only(left=30)
            ),
            ft.Container(
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                self.app_name_field,
                                self.company_name_field,
                                self.company_logo_field,
                                self.theme_dropdown,
                            ],
                            spacing=15,
                        ),
                        padding=ft.padding.all(25),
                        bgcolor=ft.colors.WHITE,
                    ),
                ),
                margin=ft.margin.only(left=30, right=30),
            ),
            ft.Container(height=40),

            # Email Settings
            ft.Container(
                content=ft.Text("Email Settings", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
                margin=ft.margin.only(left=30)
            ),
            ft.Container(
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                self.smtp_server_field,
                                self.smtp_port_field,
                                self.smtp_username_field,
                            ],
                            spacing=15,
                        ),
                        padding=ft.padding.all(25),
                        bgcolor=ft.colors.WHITE,
                    ),
                ),
                margin=ft.margin.only(left=30, right=30),
            ),
            ft.Container(height=40),

            # Backup Settings
            ft.Container(
                content=ft.Text("Backup Settings", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
                margin=ft.margin.only(left=30)
            ),
            ft.Container(
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                self.auto_backup_switch,
                                self.backup_frequency_dropdown,
                                self.backup_retention_field,
                                self.backup_now_button,
                            ],
                            spacing=15,
                        ),
                        padding=ft.padding.all(25),
                        bgcolor=ft.colors.WHITE,
                    ),
                ),
                margin=ft.margin.only(left=30, right=30),
            ),
            ft.Container(height=40),

            # Save Button
            ft.Container(
                content=self.save_settings_button,
                margin=ft.margin.only(left=30, top=10, bottom=20)
            ),
        ]

    def load_settings(self):
        """Load system settings from the database."""
        # In a real application, you would load settings from the database
        # For now, we'll just use the default values
        pass

    def backup_now(self, e):
        """Perform a manual backup."""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Backup initiated successfully", color=ft.colors.WHITE),
                bgcolor=ft.colors.BLUE_600,
            )
            self.page.snack_bar.open = True
            self.page.update()

    def save_settings(self, e):
        """Save system settings."""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Settings saved successfully", color=ft.colors.WHITE),
                bgcolor=ft.colors.GREEN_600,
            )
            self.page.snack_bar.open = True
            self.page.update()


class SettingsView(ft.Container):
    def __init__(self):
        super().__init__()
        self._page = None

        # Create tab contents
        self.user_management_tab = UserManagementTab()
        self.locations_tab = LocationsTab()
        self.categories_tab = CategoriesTab()
        self.system_settings_tab = SystemSettingsTab()

        # Set up on_mount event handler
        self.on_mount = lambda _: self.did_mount()

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, value):
        print(f"SettingsView: Setting page to {value}")
        self._page = value
        # Pass the page to all tabs immediately when it's set
        if value is not None:
            print("SettingsView: Passing page to all tabs")
            self.user_management_tab.page = value
            self.locations_tab.page = value
            self.categories_tab.page = value
            self.system_settings_tab.page = value

        # Initialize tabs
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Users",
                    icon=ft.icons.PEOPLE,
                    content=ft.Container(
                        content=self.user_management_tab,
                        padding=ft.padding.only(top=20),
                    ),
                ),
                ft.Tab(
                    text="Locations",
                    icon=ft.icons.LOCATION_ON,
                    content=ft.Container(
                        content=self.locations_tab,
                        padding=ft.padding.only(top=20),
                    ),
                ),
                ft.Tab(
                    text="Categories",
                    icon=ft.icons.CATEGORY,
                    content=ft.Container(
                        content=self.categories_tab,
                        padding=ft.padding.only(top=20),
                    ),
                ),
                ft.Tab(
                    text="System",
                    icon=ft.icons.SETTINGS,
                    content=ft.Container(
                        content=self.system_settings_tab,
                        padding=ft.padding.only(top=20),
                    ),
                ),
            ],
            expand=1,
        )

        ## Set up the container
        self.content = self.build_content()
        self.expand = True

    def did_mount(self):
        """Called when the view is mounted to the page."""
        print("SettingsView.did_mount called")
        # No need to pass the page to tabs here as it's done in the page setter
        # Just make sure we have a page
        if self.page is None:
            print("WARNING: self.page is None in did_mount")
        else:
            print(f"SettingsView.did_mount: self.page is {self.page}")
            print(f"UserManagementTab.page is {self.user_management_tab.page}")

    def build_content(self):
        return ft.Column(
            [
                ft.Text(
                    "Settings",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLACK,
                ),
                ft.Container(height=20),
                self.tabs,
            ],
        )
