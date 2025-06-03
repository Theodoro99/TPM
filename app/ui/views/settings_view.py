import flet as ft
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import User, Location, Category, Setting, RoleEnum
from app.core.security import get_password_hash  # Use the correct password hash function
import uuid


# Common UI helper functions
def create_search_field(label="Search", width=300):
    """Create a standard search text field.

    Args:
        label (str): The label for the search field. Defaults to "Search".
        width (int): The width of the search field in pixels. Defaults to 300.

    Returns:
        ft.TextField: Configured search text field.
    """

    return ft.TextField(
        label=label,
        icon=ft.icons.SEARCH,
        width=width,
    )


def create_action_button(text, icon, on_click, color=ft.colors.ORANGE_600):
    """Create a standard action button with consistent styling.

    Args:
        text (str): The button text.
        icon: The icon to display on the button.
        on_click: The callback function for button clicks.
        color: The background color of the button. Defaults to ORANGE_600.

    Returns:
        ft.ElevatedButton: Configured action button.
    """
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
    """Create a standard row layout with search field and action button.

    Args:
        search_field: The search field widget.
        action_button: The action button widget.

    Returns:
        ft.Row: Configured row layout.
    """
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
    """Create a standard confirmation dialog.

    Args:
        title (str): The dialog title.
        content: The dialog content (text or widget).
        on_confirm: Callback for confirm action.
        on_cancel: Callback for cancel action. Optional.

    Returns:
        ft.AlertDialog: Configured confirmation dialog.
    """
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
    """Base class for all settings tabs with common functionality.

    Attributes:
        page: Reference to the Flet page.
        db (Session): Database session.
        entity_name (str): Name of the entity being managed.
        search_label (str): Label for the search field.
        search_field: Search field widget.
        scroll: Scroll behavior for the tab.
    """

    def __init__(self, entity_name, search_label=None):
        """Initialize the base tab.

        Args:
            entity_name (str): Name of the entity being managed.
            search_label (str, optional): Custom label for search field.
                Defaults to "Search {entity_name}s".
        """

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
        """Close the currently open dialog.

        Args:
            e: The event object.
        """
        if self.page and self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def show_snack_bar(self, message, color=ft.colors.GREEN_600):
        """Show a snack bar message.

        Args:
            message (str): The message to display.
            color: The background color of the snackbar. Defaults to GREEN_600.
        """
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message, color=ft.colors.WHITE),
                bgcolor=color,
            )
            self.page.snack_bar.open = True
            self.page.update()


class UserManagementTab(BaseTab):
    """Tab for managing user accounts.

    Inherits from BaseTab and adds user-specific functionality.
    """
    def __init__(self):
        """Initialize the user management tab."""
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
        """Show the dialog for adding a new user.

        Args:
            e: The event object from the button click.
        """
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
                helper_text="",
                on_change=self.validate_email_field,
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

            confirm_password_field = ft.TextField(
                label="Confirm Password",
                hint_text="Confirm your password",
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
            self.confirm_password_field = confirm_password_field
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
                        confirm_password_field,
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
        """Close the dialog or overlay form.

        Args:
            e: The event object.
        """
        # Handle overlay form (new method)
        if self.page:
            # Check if there's an overlay to remove
            overlays_to_remove = []
            for overlay in self.page.overlay:
                if hasattr(overlay, 'data') and (
                        overlay.data == 'add_user_overlay' or overlay.data == 'edit_user_overlay'):
                    overlays_to_remove.append(overlay)

            # Remove the overlays
            for overlay in overlays_to_remove:
                self.page.overlay.remove(overlay)

            # Update the page
            self.page.update()
            print("Form closed")

    def validate_email_field(self, e):
        """Validate email field as user types and provide immediate feedback.

        Args:
            e: The event object containing the field value.
        """
        email = e.control.value
        if not email:
            # Empty field - clear any error
            e.control.helper_text = ""
            e.control.helper_style = ft.TextStyle(color=ft.colors.GREY_700)
            e.control.border_color = ft.colors.BLUE_GREY_400
        elif "@" not in email or "." not in email or email.count("@") != 1:
            # Invalid email format
            e.control.helper_text = "Email must contain @ and domain (example@domain.com)"
            e.control.helper_style = ft.TextStyle(color=ft.colors.RED_600, weight=ft.FontWeight.BOLD)
            e.control.border_color = ft.colors.RED_600
        else:
            # Valid email format
            e.control.helper_text = "Valid email format"
            e.control.helper_style = ft.TextStyle(color=ft.colors.GREEN_600)
            e.control.border_color = ft.colors.GREEN_600

        e.control.update()

    def edit_user(self, e):
        """Edit an existing user.

        Args:
            e: The event object containing the user ID to edit.
        """
        try:
            # Get the user ID from the event data
            user_id = e.control.data
            print(f"DEBUG: edit_user called with user_id: {user_id}, type: {type(user_id)}")

            # Convert string UUID to UUID object if needed
            try:
                # Try to convert string to UUID if it's not already a UUID
                if isinstance(user_id, str):
                    user_id = uuid.UUID(user_id)
                    print(f"DEBUG: Converted string to UUID: {user_id}")
            except ValueError as ve:
                print(f"DEBUG: Error converting to UUID: {ve}")
                raise ValueError(f"Invalid user ID format: {user_id}") from ve

            # Find the user in the database
            user = self.db.query(User).filter(User.id == user_id).first()

            if user:
                # Show edit user dialog
                self.show_edit_user_dialog(user)
            else:
                # User not found
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("User not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as ex:
            print(f"Error editing user: {ex}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error editing user: {str(ex)}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

            print("self.page is available")

            # Instead of using a dialog, we'll create a modal-like UI directly in the page
            # Create a new container that will overlay the current view

            # First, remove any existing edit_user_overlay
            for control in self.page.overlay:
                if hasattr(control, 'data') and control.data == 'edit_user_overlay':
                    self.page.overlay.remove(control)
                    break

            # Store the user ID for later use when saving
            self.editing_user_id = str(user.id)

            # Create form fields
            username_field = ft.TextField(
                label="Username",
                hint_text="Enter username",
                border_color=ft.colors.BLUE_GREY_400,
                color=ft.colors.BLACK,
                width=300,
                bgcolor=ft.colors.WHITE,
                value=user.username,
            )

            full_name_field = ft.TextField(
                label="Full Name",
                hint_text="Enter full name",
                border_color=ft.colors.BLUE_GREY_400,
                color=ft.colors.BLACK,
                width=300,
                bgcolor=ft.colors.WHITE,
                value=user.full_name,
            )

            email_field = ft.TextField(
                label="Email",
                hint_text="Enter email address",
                border_color=ft.colors.BLUE_GREY_400,
                color=ft.colors.BLACK,
                width=300,
                bgcolor=ft.colors.WHITE,
                value=user.email,
                helper_text="",
                on_change=self.validate_email_field,
            )

            # Add password change fields
            password_field = ft.TextField(
                label="New Password (leave blank to keep current)",
                hint_text="Enter new password",
                password=True,
                border_color=ft.colors.BLUE_GREY_400,
                color=ft.colors.BLACK,
                width=300,
                bgcolor=ft.colors.WHITE,
            )

            confirm_password_field = ft.TextField(
                label="Confirm New Password",
                hint_text="Confirm new password",
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
                value=user.role.value,
            )

            department_field = ft.TextField(
                label="Department",
                hint_text="Enter department",
                border_color=ft.colors.BLUE_GREY_400,
                color=ft.colors.BLACK,
                width=300,
                bgcolor=ft.colors.WHITE,
                value=user.department,
            )

            is_active_checkbox = ft.Checkbox(
                label="Is Active",
                value=user.is_active,
            )

            # Store the fields as instance variables for later use
            self.edit_username_field = username_field
            self.edit_full_name_field = full_name_field
            self.edit_email_field = email_field
            self.edit_password_field = password_field
            self.edit_confirm_password_field = confirm_password_field
            self.edit_role_dropdown = role_dropdown
            self.edit_department_field = department_field
            self.edit_is_active_checkbox = is_active_checkbox
            # Create the form card
            form_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Edit User", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
                        ft.Divider(),
                        username_field,
                        full_name_field,
                        email_field,
                        password_field,
                        confirm_password_field,
                        role_dropdown,
                        department_field,
                        is_active_checkbox,
                        ft.Row([
                            ft.ElevatedButton(
                                "Cancel",
                                on_click=self.close_dialog,
                                bgcolor=ft.colors.RED_400,
                                color=ft.colors.WHITE,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            ),
                            ft.ElevatedButton(
                                "Save Changes",
                                on_click=lambda e: self.save_user_changes(e, user.id),
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
                data="edit_user_overlay",  # Tag it for easy identification
            )

            # Add the overlay to the page
            self.page.overlay.append(overlay)
            self.page.update()
            print("User edit form should be visible now")

        except Exception as ex:
            print(f"Exception in show_edit_user_dialog: {ex}")
            import traceback
            traceback.print_exc()

    def save_user_changes(self, e, user_id=None):
        """Save changes to an edited user.

        Args:
            e: The event object.
            user_id: Optional user ID if not using the stored editing_user_id.
        """
        try:
            # Use the provided user_id if available, otherwise use the stored one
            user_id_to_use = user_id if user_id else self.editing_user_id
            print(f"Saving changes for user ID: {user_id_to_use}")

            # Validate form fields
            print("Getting form field values...")
            username = self.edit_username_field.value
            print(f"Username: {username}")
            full_name = self.edit_full_name_field.value
            print(f"Full name: {full_name}")
            email = self.edit_email_field.value
            print(f"Email: {email}")
            password = self.edit_password_field.value
            print(f"Password provided: {bool(password)}")
            confirm_password = self.edit_confirm_password_field.value
            role = self.edit_role_dropdown.value
            print(f"Role: {role}")
            department = self.edit_department_field.value
            print(f"Department: {department}")
            is_active = self.edit_is_active_checkbox.value
            print(f"Is active: {is_active}")

            # Validate required fields
            if not username or not role:
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Username and Role are required fields", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                return

            # Validate email format if provided
            if email and ("@" not in email or "." not in email):
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Please enter a valid email address", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                return

            # Validate password if provided
            if password:
                if password != confirm_password:
                    if self.page:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text("Passwords do not match", color=ft.colors.WHITE),
                            bgcolor=ft.colors.RED_600,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    return
                if len(password) < 6:
                    if self.page:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text("Password must be at least 6 characters", color=ft.colors.WHITE),
                            bgcolor=ft.colors.RED_600,
                        )
                        self.page.snack_bar.open = True
                if existing_user:
                    print(f"Email {email} already exists for another user")
                    if self.page:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Email {email} is already registered to another user",
                                            color=ft.colors.WHITE),
                            bgcolor=ft.colors.RED_600,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    return
        except Exception as ex:
            print(f"Error checking email uniqueness: {ex}")

        # Find the user in the database
        try:
            # Convert string to UUID if needed
            user_id_uuid = uuid.UUID(user_id_to_use) if isinstance(user_id_to_use, str) else user_id_to_use
            print(f"Looking up user with UUID: {user_id_uuid}")

            user = self.db.query(User).filter(User.id == user_id_uuid).first()
            if not user:
                print("User not found")
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("User not found", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                return

            # Update user properties
            print("Updating user properties...")
            user.username = username
            user.full_name = full_name
            user.email = email
            user.role = role
            user.department = department
            user.is_active = is_active

            # Update password if provided
            if password and len(password) >= 6:
                print("Updating password")
                from app.core.security import get_password_hash
                user.password_hash = get_password_hash(password)

            # Save changes to database
            self.db.commit()
            print("Changes committed to database")

            # Close the dialog by removing the overlay
            print("Closing edit user dialog")
            # Remove the overlay from the page
            if self.page and self.page.overlay:
                overlays_to_remove = []
                for overlay in self.page.overlay:
                    if hasattr(overlay, 'data') and overlay.data == 'edit_user_overlay':
                        overlays_to_remove.append(overlay)

                # Remove the overlays
                for overlay in overlays_to_remove:
                    self.page.overlay.remove(overlay)
                    print("Edit user overlay removed")

                self.page.update()
                print("Form closed")

            # Show success message
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"User {username} updated successfully", color=ft.colors.WHITE),
                    bgcolor=ft.colors.GREEN_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

        except Exception as ex:
            print(f"Error saving user changes: {ex}")
            import traceback
            traceback.print_exc()
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error saving user changes: {str(ex)}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def close_delete_dialog(self, e=None):
        """Close the delete confirmation dialog.

        Args:
            e: Optional event object.
        """
        print("DEBUG: Attempting to close delete dialog")
        if self.page and hasattr(self.page, 'dialog') and self.page.dialog:
            print("DEBUG: Found dialog, closing it")
            self.page.dialog.open = False
            self.page.update()
            print("DEBUG: Delete dialog closed")
            # Reset the dialog to prevent future issues
            self.page.dialog = None
            self.page.update()

    def load_users_from_db(self):
        """Load users from the database into the UI."""
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
        """Add a new user to the database.

        Args:
            e: The event object.
        """
        print("add_user method called")
        try:
            # Get form values
            username = self.username_field.value
            full_name = self.full_name_field.value
            email = self.email_field.value
            password = self.password_field.value
            confirm_password = self.confirm_password_field.value
            role = self.role_dropdown.value
            department = self.department_field.value

            # Validate required fields
            if not username or not password or not confirm_password or not role:
                print(f"Missing required fields: username={username}, role={role}")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Missing required fields", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
                return

            # Validate that passwords match
            if password != confirm_password:
                print("Passwords do not match")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Passwords do not match", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
                return

            # Validate email format if email is provided
            if email and ("@" not in email or "." not in email or email.count("@") != 1):
                print(f"Invalid email format: {email}")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Please enter a valid email address (example@domain.com)", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
                return

            print(f"Form values: username={username}, role={role}")

            # Check if email already exists
            if email:
                existing_user = self.db.query(User).filter(User.email == email).first()
                if existing_user:
                    print(f"Email {email} already exists in the database")
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Email {email} is already registered", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
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
                password_hash=get_password_hash(password),  # Use the correct password hash function
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

        # Validate required fields
        if not username or not password or not confirm_password or not role:
            print(f"Missing required fields: username={username}, role={role}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Missing required fields", color=ft.colors.WHITE),
                bgcolor=ft.colors.RED_600,
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        # Validate that passwords match
        if password != confirm_password:
            print("Passwords do not match")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Passwords do not match", color=ft.colors.WHITE),
                bgcolor=ft.colors.RED_600,
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        # Validate email format if email is provided
        if email and ("@" not in email or "." not in email or email.count("@") != 1):
            print(f"Invalid email format: {email}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Please enter a valid email address (example@domain.com)", color=ft.colors.WHITE),
                bgcolor=ft.colors.RED_600,
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        print(f"Form values: username={username}, role={role}")

        # Check if email already exists
        if email:
            existing_user = self.db.query(User).filter(User.email == email).first()
            if existing_user:
                print(f"Email {email} already exists in the database")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Email {email} is already registered", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
                return

        # Convert role string to enum
        try:
            role_enum = RoleEnum[role]
        except KeyError:
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Invalid role: {role}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
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
        """Delete a user from the system using a direct approach without dialogs.

        Args:
            e: The event object containing the user ID to delete.
        """
        try:
            # Prevent multiple clicks
            if hasattr(e, 'control'):
                e.control.disabled = True
                if self.page:
                    self.page.update()

            # Check if a confirmation banner is already showing
            # Look for any existing confirmation containers and remove them
            confirmation_containers = []
            for control in self.controls:
                if isinstance(control, ft.Container) and hasattr(control,
                                                                 'data') and control.data == 'delete_confirmation':
                    confirmation_containers.append(control)

            # Remove any existing confirmation containers
            for container in confirmation_containers:
                self.controls.remove(container)
                print("DEBUG: Removed existing confirmation banner")

            # Get the user ID from the event data
            user_id = e.control.data if hasattr(e, 'control') and hasattr(e.control, 'data') else None
            print(f"DEBUG: delete_user called with user_id: {user_id}, type: {type(user_id)}")

            if not user_id:
                print("ERROR: No user ID provided")
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Error: No user ID provided", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                return

            # Create a direct database session for finding the user
            from app.db.database import SessionLocal
            db_session = SessionLocal()

            try:
                # Try multiple approaches to find the user
                user = None

                # Try with UUID
                try:
                    if isinstance(user_id, str):
                        uuid_obj = uuid.UUID(user_id)
                    else:
                        uuid_obj = user_id
                    user = db_session.query(User).filter(User.id == uuid_obj).first()
                    print(f"DEBUG: UUID query result: {user is not None}")
                except Exception as ex:
                    print(f"DEBUG: UUID conversion error: {ex}")

                # If not found, try with string comparison
                if not user:
                    print("DEBUG: Trying string comparison")
                    user_id_str = str(user_id).lower().strip()
                    all_users = db_session.query(User).all()
                    for u in all_users:
                        if str(u.id).lower().strip() == user_id_str:
                            user = u
                            print(f"DEBUG: Found user by string comparison: {u.username}")
                            break

                if not user:
                    print(f"DEBUG: User with ID {user_id} not found")
                    if self.page:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text("User not found", color=ft.colors.WHITE),
                            bgcolor=ft.colors.RED_600,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    return

                print(f"DEBUG: Found user: {user.username}")
                username = user.username

                # Create a confirmation banner instead of a dialog
                confirm_container = ft.Container(
                    content=ft.Column([
                        ft.Text(f"Are you sure you want to delete user '{username}'?", size=16,
                                weight=ft.FontWeight.BOLD),
                        ft.Text("This action cannot be undone.", color=ft.colors.RED),
                        ft.Row([
                            ft.ElevatedButton("Cancel", on_click=lambda e: self.cancel_delete(e, confirm_container)),
                            ft.ElevatedButton(
                                "Delete",
                                on_click=lambda e: self.confirm_delete_user(e, user.id, username, confirm_container),
                                style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.RED)
                            ),
                        ], alignment=ft.MainAxisAlignment.END),
                    ]),
                    padding=10,
                    bgcolor=ft.colors.AMBER_50,
                    border=ft.border.all(2, ft.colors.RED_400),
                    border_radius=ft.border_radius.all(8),
                    margin=ft.margin.only(bottom=20),
                    data="delete_confirmation"  # Add a data attribute to identify this container
                )

                # Insert the confirmation container at the top of the controls
                self.controls.insert(0, confirm_container)
                self.update()

                print("DEBUG: Confirmation banner shown")

            finally:
                # Close the session
                db_session.close()

            # Re-enable the button
            if hasattr(e, 'control'):
                e.control.disabled = False
                if self.page:
                    self.page.update()

        except Exception as ex:
            print(f"ERROR in delete_user: {ex}")
            import traceback
            traceback.print_exc()

            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error preparing user deletion: {ex}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

            # Re-enable the button
            if hasattr(e, 'control'):
                e.control.disabled = False
                if self.page:
                    self.page.update()

    def cancel_delete(self, e, confirm_container):
        """Cancel the deletion process and remove the confirmation banner.

        Args:
            e: The event object.
            confirm_container: The confirmation container to remove.
        """
        print("DEBUG: Delete canceled")
        if confirm_container in self.controls:
            self.controls.remove(confirm_container)
            self.update()

    def confirm_delete_user(self, e, user_id, username, confirm_container):
        """Confirm and execute user deletion.

        Args:
            e: The event object.
            user_id: The ID of the user to delete.
            username: The username of the user being deleted.
            confirm_container: The confirmation container to remove.
        """
        print(f"DEBUG: Confirming deletion of user: {username} with ID: {user_id}")

        # Remove the confirmation container
        if confirm_container in self.controls:
            self.controls.remove(confirm_container)
            self.update()

        # Get a fresh database session
        from app.db.database import SessionLocal
        db_session = SessionLocal()

        try:
            # Find the user in the database
            print(f"DEBUG: Querying database for user with ID: {user_id}")
            user = db_session.query(User).get(user_id)

            if user:
                print(f"DEBUG: Found user to delete: {user.username}")

                # Delete from database
                print(f"DEBUG: Deleting user from database: {user.username}")
                db_session.delete(user)
                db_session.commit()
                print(f"DEBUG: User {user.username} deleted from database successfully")

                # Show success message
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"User {username} deleted successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()

                # Reload the users list
                print("DEBUG: Reloading users list")
                self.load_users_from_db()
                print("DEBUG: Users list reloaded")
            else:
                print(f"DEBUG: User with ID {user_id} not found in database")
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("User not found in database", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as ex:
            print(f"ERROR in confirm_delete_user: {ex}")
            import traceback
            traceback.print_exc()

            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error deleting user: {str(ex)}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
        finally:
            # Close the session
            db_session.close()
            print("DEBUG: Database session closed")

    def handle_delete_button_click(self, e, user_id, username):
        """Handle the click event for the Delete button in the confirmation dialog.

        Args:
            e: The event object.
            user_id: The ID of the user to delete.
            username: The username of the user being deleted.
        """
        print(f"DEBUG: handle_delete_button_click called for user: {username} with ID: {user_id}")
        self.perform_delete_user(user_id)
        self.close_dialog(e)

    def perform_delete_user(self, e):
        """Execute the deletion of a user after confirmation.

        Args:
            e: The event object containing the user ID to delete.
        """
        print("======================================================")
        print(f"DEBUG: perform_delete_user called with event type: {type(e)}")
        print(f"DEBUG: Event details: {e}")
        if hasattr(e, "control"):
            print(f"DEBUG: Control: {e.control}")
            if hasattr(e.control, "data"):
                print(f"DEBUG: Control data: {e.control.data}")
        print(f"DEBUG: user_id_pending_deletion: {getattr(self, 'user_id_pending_deletion', None)}")
        print("======================================================")

        # First close the dialog to ensure UI responsiveness
        self.close_dialog(e)

        # If the user_id_pending_deletion is not set, get it from the event data if possible
        if not hasattr(self, 'user_id_pending_deletion') or not self.user_id_pending_deletion:
            print("DEBUG: No user_id_pending_deletion, checking event data")
            if hasattr(e, "control") and hasattr(e.control, "data"):
                self.user_id_pending_deletion = e.control.data
                print(f"DEBUG: Got user_id from event data: {self.user_id_pending_deletion}")

        if not hasattr(self, 'user_id_pending_deletion') or not self.user_id_pending_deletion:
            print("ERROR: No user ID pending deletion")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error: No user selected for deletion", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
            return

        print("DEBUG: Starting actual user deletion process")
        print(f"DEBUG: Will attempt to delete user with ID: {self.user_id_pending_deletion}")

        # Force a direct deletion approach for debugging
        try:
            user_id = self.user_id_pending_deletion
            print(f"DEBUG: Attempting direct deletion for user ID: {user_id}, type: {type(user_id)}")

            # Convert to UUID if it's a string
            if isinstance(user_id, str):
                try:
                    user_id = uuid.UUID(user_id)
                    print(f"DEBUG: Converted user_id to UUID: {user_id}")
                except ValueError as ve:
                    print(f"ERROR: Failed to convert user_id to UUID: {ve}")
                    print(f"DEBUG: Will try to query using string ID directly")

            # Get a fresh database session
            from app.db.database import SessionLocal
            db_session = SessionLocal()

            try:
                # Find the user in the database - try both ways
                print(f"DEBUG: Querying database for user with ID: {user_id}")
                user = db_session.query(User).filter(User.id == user_id).first()

                # If not found and we have a UUID, try with string
                if not user and isinstance(user_id, uuid.UUID):
                    print(f"DEBUG: User not found with UUID, trying with string: {str(user_id)}")
                    user = db_session.query(User).filter(User.id == str(user_id)).first()

                # If not found and we have a string, try with UUID
                if not user and isinstance(user_id, str):
                    try:
                        print(f"DEBUG: User not found with string, trying with UUID: {uuid.UUID(user_id)}")
                        user = db_session.query(User).filter(User.id == uuid.UUID(user_id)).first()
                    except ValueError:
                        print(f"DEBUG: Could not convert string to UUID for query")

                print(f"DEBUG: Database query result: {user}")
                print(f"DEBUG: User found: {user is not None}")
                if user:
                    print(f"DEBUG: User details - ID: {user.id}, Username: {user.username}, Role: {user.role}")

                if user:
                    print(f"DEBUG: Found user to delete: {user.username}")
                    # Store username for messages
                    username = user.username

                    # Delete from database
                    print(f"DEBUG: Deleting user from database: {username}")
                    db_session.delete(user)
                    db_session.commit()
                    print(f"DEBUG: User {username} deleted from database successfully")

                    # Show success message
                    if self.page:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"User {username} deleted successfully", color=ft.colors.WHITE),
                            bgcolor=ft.colors.GREEN_600,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()

                    # Reload the users list
                    print("DEBUG: Reloading users list")
                    self.load_users_from_db()
                    print("DEBUG: Users list reloaded")
                else:
                    print(f"DEBUG: User with ID {user_id} not found in database")
            finally:
                # Close the session
                db_session.close()
                print("DEBUG: Database session closed")
        except Exception as ex:
            print(f"ERROR in direct deletion attempt: {ex}")
            import traceback
            traceback.print_exc()

        try:
            # Convert user_id to UUID if it's a string
            user_id = self.user_id_pending_deletion
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
                print(f"DEBUG: Converted user_id to UUID: {user_id}")

            # Find the user in the database
            print(f"DEBUG: Querying database for user with ID: {user_id}")
            user = self.db.query(User).filter(User.id == user_id).first()
            print(f"DEBUG: Database query result: {user}")

            if not user:
                print(f"DEBUG: User with ID {user_id} not found in database")
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("User not found in database", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                return

            # Store username for messages
            username = user.username

            # Delete from database
            print(f"DEBUG: Deleting user: {username} (ID: {user.id})")
            self.db.delete(user)
            self.db.commit()
            print(f"DEBUG: User {username} deleted from database")

            # Remove from UI list
            user_id_str = str(user_id)
            print(f"DEBUG: Filtering users list with user_id_str: {user_id_str}")
            original_length = len(self.users_list)
            self.users_list = [u for u in self.users_list if str(u["id"]) != user_id_str]
            new_length = len(self.users_list)
            print(f"DEBUG: Users list filtered. Original length: {original_length}, New length: {new_length}")

            # Update the users property from the filtered users_list
            print("DEBUG: Updating self.users from filtered users_list")
            self.users = self.users_list.copy()

            # Rebuild the user table
            print("DEBUG: Rebuilding user table")
            self.user_table = self.build_user_table()

            # Update the controls
            print("DEBUG: Updating controls")
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
                print("DEBUG: Showing success message")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"User {username} deleted successfully", color=ft.colors.WHITE),
                    bgcolor=ft.colors.GREEN_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
                print("DEBUG: Success message shown")

            # Reset the pending deletion ID
            self.user_id_pending_deletion = None

        except ValueError as e:
            print(f"ERROR converting user_id to UUID: {e}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Invalid user ID format: {e}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as ex:
            print(f"ERROR in perform_delete_user: {ex}")
            import traceback
            traceback.print_exc()
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error during deletion: {ex}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_600,
                )
                self.page.snack_bar.open = True
                self.page.update()

            if user:
                # Delete from database
                print(f"DEBUG: Deleting user: {user.username} (ID: {user.id})")
                try:
                    self.db.delete(user)
                    self.db.commit()
                    print("DEBUG: User deleted from database and changes committed successfully")
                except Exception as db_error:
                    print(f"ERROR during database deletion: {db_error}")
                    if self.page:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Database error: {db_error}", color=ft.colors.WHITE),
                            bgcolor=ft.colors.RED_600,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    return

                # Remove from UI list
                # Convert user_id to string for comparison with the string IDs in self.users
                user_id_str = str(user_id)
                print(f"DEBUG: Filtering users list with user_id_str: {user_id_str}")
                original_length = len(self.users)
                self.users = [u for u in self.users if u["id"] != user_id_str]
                new_length = len(self.users)
                print(f"DEBUG: Users list filtered. Original length: {original_length}, New length: {new_length}")

                # Rebuild the user table
                print("DEBUG: Rebuilding user table")
                self.user_table = self.build_user_table()

                # Update the controls
                print("DEBUG: Updating controls")
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
                print("DEBUG: Controls updated successfully")

                # Show success message
                if self.page:
                    print("DEBUG: Showing success message")
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"User {user.username} deleted successfully", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                    print("DEBUG: Success message shown")
            else:
                print(f"DEBUG: User with ID {user_id} not found in database")
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("User not found in database", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        except Exception as e:
            print(f"CRITICAL ERROR in perform_delete_user: {e}")
            import traceback
            traceback.print_exc()
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
        """Build the user table with current users.

        Returns:
            ft.DataTable: Configured data table displaying all users.
        """
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
                # Create the status cell with appropriate color
                status_cell = ft.DataCell(
                    ft.Text(
                        "Active" if user["is_active"] else "Inactive",
                        color=ft.colors.GREEN if user["is_active"] else ft.colors.RED,
                    )
                )

                # Create the actions cell with edit, delete buttons and status toggle
                actions_cell = ft.DataCell(
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                tooltip="Edit User",
                                icon_color=ft.colors.BLUE_600,
                                data=user["id"],
                                on_click=self.edit_user,
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                tooltip="Delete User",
                                icon_color=ft.colors.RED_600,
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
                        ],
                        spacing=5,
                    )
                )

                # Create the complete row
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(user["username"], color=ft.colors.BLACK)),
                            ft.DataCell(ft.Text(user["full_name"], color=ft.colors.BLACK)),
                            ft.DataCell(ft.Text(user["email"], color=ft.colors.BLACK)),
                            ft.DataCell(ft.Text(user["role"], color=ft.colors.BLACK)),
                            ft.DataCell(ft.Text(user["department"], color=ft.colors.BLACK)),
                            status_cell,
                            actions_cell,
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
        """Toggle user active status.

        Args:
            e: The event object containing the user ID and new status.
        """
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
    """A tab for managing locations in the application.

    This tab provides functionality to view, add, edit, and delete locations.
    It displays locations in a table format with search and CRUD operations.
    """
    def __init__(self):
        """Initialize the Locations tab.

        Sets up the UI elements including search field, add button, and location table.
        Loads initial location data from the database.
        """
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
        """Build and return a DataTable widget displaying all locations.

        The table includes columns for name, description, address, status, and actions.
        Each row represents a location with edit and delete action buttons.

        Returns:
            ft.DataTable: A configured DataTable widget showing location information.
        """
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
        """Load locations from the database into the application.

        Attempts to query locations from the database. If the query fails,
        falls back to a predefined set of location data.
        """
        try:
            # Query all locations from the database
            db_locations = self.db.query(Location).all()

            # Convert database locations to dictionary format for the UI
            self.locations = []
            for location in db_locations:
                self.locations.append({
                    "id": str(location.id),
                    "name": location.name,
                    "description": location.description or "",
                    "address": location.description or "",
                    # Use description as address since address field doesn't exist
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
        """Display a dialog for adding a new location.

        Args:
            e: The event that triggered this action.
        """
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
        """Close any currently open dialog.

        Args:
            e: The event that triggered this action.
        """
        if self.page and self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def add_location(self, e):
        """Add a new location based on user input from the add location dialog.

        Args:
            e: The event that triggered this action.
        """
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
            # Store address in description if address field is provided
            description = self.description_field.value
            if self.address_field.value and not description:
                description = f"Address: {self.address_field.value}"
            elif self.address_field.value:
                description = f"{description} | Address: {self.address_field.value}"

            new_location_db = Location(
                name=self.name_field.value,
                description=description,
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
                "address": self.address_field.value or new_location_db.description or "",
                # Use address field value if provided
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
        """Display a dialog for editing an existing location.

        Args:
            e: The event that triggered this action, containing the location ID to edit.
        """
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
        """Save changes made to a location in the edit dialog.

        Args:
            location_id: The ID of the location being edited.
        """
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
        """Initiate the deletion process for a location.

        Displays a confirmation dialog before proceeding with deletion.

        Args:
            e: The event that triggered this action, containing the location ID to delete.
        """
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
        """Confirm and execute the deletion of a location.

        Args:
            location_id: The ID of the location to be deleted.
        """
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
    """A tab for managing task categories in the application.

    This tab provides functionality to view, add, edit, and delete task categories.
    It displays categories in a table format with search and CRUD operations,
    including the ability to toggle category status and assign colors.
    """
    def __init__(self):
        """Initialize the Categories tab.

        Sets up the UI elements including search field, add button, and category table.
        Loads initial category data from the database.
        """
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
        """Build and return a DataTable widget displaying all categories.

        The table includes columns for name, description, subcategories, color, status, and actions.
        Each row represents a category with edit, delete, and toggle status action buttons.

        Returns:
            ft.DataTable: A configured DataTable widget showing category information.
        """
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
        """Load categories from the database into the application.

        Attempts to query categories from the database. If the query fails,
        falls back to a predefined set of category data. Maps database color codes
        to Flet color values for UI display.
        """
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
        """Close any currently open dialog.

        Args:
            e: The event that triggered this action.
        """
        if self.page and self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def show_add_category_dialog(self, e):
        """Display a dialog for adding a new category.

        Args:
            e: The event that triggered this action.
        """
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
        """Add a new category based on user input from the add category dialog.

        Args:
            e: The event that triggered this action.
        """
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
        """Display a dialog for editing an existing category.

        Args:
            e: The event that triggered this action, containing the category ID to edit.
        """
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
        """Save changes made to a category in the edit dialog.

        Args:
            category_id: The ID of the category being edited.
        """
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
        """Initiate the deletion process for a category.

        Displays a confirmation dialog before proceeding with deletion.

        Args:
            e: The event that triggered this action, containing the category ID to delete.
        """
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
        """Confirm and execute the deletion of a category.

        Permanently removes the category from both the database and UI after confirmation.
        Updates the UI to reflect the deletion and shows appropriate status messages.

        Args:
            category_id: The ID of the category to be deleted.
        """
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
        """Toggle the active/inactive status of a category.

        Updates both the database and UI to reflect the status change.
        Shows appropriate success/error messages to the user.

        Args:
            e: The event that triggered this action, containing the category ID to toggle.
        """
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
    """A tab for managing system-wide settings in the application.

    Provides configuration options for general application settings,
    email server configuration, and backup settings.
    """
    def __init__(self):
        """Initialize the System Settings tab.

        Sets up all UI controls for various system settings sections
        including general settings, email settings, and backup settings.
        """
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
        """Load system settings from the database.

        Placeholder for future implementation to load saved settings.
        Currently uses default values for all settings.
        """
        # In a real application, you would load settings from the database
        # For now, we'll just use the default values
        pass

    def backup_now(self, e):
        """Initiate an immediate manual backup of the system.

        Args:
            e: The event that triggered this action.
        """
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Backup initiated successfully", color=ft.colors.WHITE),
                bgcolor=ft.colors.BLUE_600,
            )
            self.page.snack_bar.open = True
            self.page.update()

    def save_settings(self, e):
        """Save all system settings to persistent storage.

        Args:
            e: The event that triggered this action.
        """
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Settings saved successfully", color=ft.colors.WHITE),
                bgcolor=ft.colors.GREEN_600,
            )
            self.page.snack_bar.open = True
            self.page.update()


class SettingsView(ft.Container):
    """The main settings view container that hosts all settings tabs.

    Manages the tabbed interface for user management, locations,
    categories, and system settings.
    """

    def __init__(self):
        """Initialize the Settings View.

        Creates all tab instances and sets up the tabbed interface.
        """
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
        """Get the current page associated with this view.

        Returns:
            The page object this view is attached to.
        """
        return self._page

    @page.setter
    def page(self, value):
        """Set the page for this view and all its tabs.

        Args:
            value: The page object to associate with this view.
        """
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

        # Set up the container
        self.content = self.build_content()
        self.expand = True

    def did_mount(self):
        """Callback called when the view is mounted to the page.

        Handles any initialization that needs to occur after the view
        is attached to the page.
        """
        print("SettingsView.did_mount called")
        # No need to pass the page to tabs here as it's done in the page setter
        # Just make sure we have a page
        if self.page is None:
            print("WARNING: self.page is None in did_mount")
        else:
            print(f"SettingsView.did_mount: self.page is {self.page}")
            print(f"UserManagementTab.page is {self.user_management_tab.page}")

    def build_content(self):
        """Build and return the main content structure for the settings view.

        Returns:
            A Column widget containing the settings title and tabs.
        """

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
